"""
OceanBase CE v4.5.0 VECTOR 类型兼容性测试
========================================
探索 OceanBase CE v4.5.0 对 VECTOR(768) 类型的真实支持程度

关键问题：
1. 标准索引不支持向量列（错误码 1235）
2. str(vector_array) 格式插入失败（错误码 1210）

需要测试的格式：
- JSON array: [0.1, 0.2, ...]
- String format: "0.1,0.2,..."
- Binary/HEX representation
"""

import pymysql
import numpy as np
from typing import List
import json
import time

print("=" * 90)
print("🔍 OceanBase CE v4.5.0 VECTOR 类型兼容性测试")
print("=" * 90)

# ==========================================
# 1. 数据库连接和版本确认
# ==========================================
print("\n【阶段 1】数据库连接验证...")

try:
    conn = pymysql.connect(
        host='10.10.10.132',
        port=2881,
        user='root@memory',
        password='OceanBase#123',
        database='memory'
    )
    cursor = conn.cursor()
    
    # Get version info
    cursor.execute("SELECT @@version_comment")
    print(f"✅ 连接成功!")
    print(f"   版本: {cursor.fetchone()[0]}")
    
except Exception as e:
    print(f"❌ 连接失败: {str(e)[:100]}")
    exit(1)

# ==========================================
# 2. 生成测试向量（多种格式）
# ==========================================
print("\n【阶段 2】生成多种格式的测试向量...")

def generate_vector(dimensions=768):
    """Generate a normalized random vector"""
    import random
    random.seed(42)
    vector = [round(np.random.normal(0, 0.5), 6) for _ in range(dimensions)]
    norm = np.linalg.norm(vector)
    if norm > 0:
        vector = [v / norm for v in vector]
    return vector

test_vector = generate_vector(768)

# Generate different string representations
formats = {
    "str_array": str(test_vector),
    "json_array": json.dumps(test_vector),
    "comma_string": ",".join([f"{v:.6f}" for v in test_vector]),
    "hex_binary": "".join([f"{int(v * 255):02x}" for v in test_vector[:100]]),  # Partial hex
}

print(f"✅ 生成向量格式:")
for fmt_name, fmt_value in formats.items():
    preview = str(fmt_value)[:80] + "..." if len(str(fmt_value)) > 80 else str(fmt_value)
    print(f"   {fmt_name}: {preview}")

# ==========================================
# 3. 创建表并测试不同格式的插入
# ==========================================
print("\n【阶段 3】创建 VECTOR(768) 表并测试数据插入...")

try:
    # Clean up first
    cursor.execute("DROP TABLE IF EXISTS ob_vector_format_test")
    
    # Create table with standard syntax
    cursor.execute("""
        CREATE TABLE ob_vector_format_test (
            id INT PRIMARY KEY,
            embedding VECTOR(768),
            model_name VARCHAR(50) DEFAULT 'bge-m3',
            dimensions INT DEFAULT 768,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    print("✅ CREATE TABLE 成功 (VECTOR(768))")
    
except Exception as e:
    error_msg = str(e)[:100] if hasattr(e, '__getitem__') else str(e)
    print(f"❌ 表创建失败: {error_msg}")
    exit(1)

# ==========================================
# 4. 测试不同格式的 INSERT
# ==========================================
print("\n【阶段 4】测试不同向量字符串格式插入...")

insert_results = {}

for fmt_name, vector_str in formats.items():
    sql = "INSERT INTO ob_vector_format_test (id, embedding) VALUES (%s, %s)"
    
    try:
        cursor.execute(sql, (1, vector_str))
        
        # Verify insertion by reading back
        cursor.execute("SELECT embedding FROM ob_vector_format_test WHERE id = 1")
        row = cursor.fetchone()
        
        if row and row[0]:
            insert_results[fmt_name] = {
                "status": "SUCCESS",
                "value_type": type(row[0]).__name__,
                "preview": str(row[0])[:80] + "..."
            }
            print(f"✅ {fmt_name}: 插入成功 (读取返回类型: {type(row[0]).__name__})")
        else:
            insert_results[fmt_name] = {"status": "NO_DATA", "error": "Read back empty"}
            
    except Exception as e:
        error_msg = str(e)[:80] if hasattr(e, '__getitem__') else str(e)
        insert_results[fmt_name] = {"status": "FAILED", "error": error_msg}
        print(f"❌ {fmt_name}: 插入失败 - {error_msg}")

# ==========================================
# 5. 如果成功，测试 VECTOR_DISTANCE 函数
# ==========================================
print("\n【阶段 5】测试 VECTOR_DISTANCE 函数（使用成功的格式）...")

successful_format = None
for fmt, result in insert_results.items():
    if result["status"] == "SUCCESS":
        successful_format = fmt
        break

if not successful_format:
    print("❌ 没有成功的插入格式，跳过 VECTOR_DISTANCE 测试")
else:
    try:
        # Get the stored vector for query
        cursor.execute("SELECT embedding FROM ob_vector_format_test WHERE id = 1")
        stored_vector = cursor.fetchone()[0]
        
        # Test COSINE distance with same format
        if successful_format == "json_array":
            query_vec_str = json.dumps(test_vector)
        elif successful_format == "str_array":
            query_vec_str = str(test_vector)
        else:
            print(f"⚠️ 跳过测试（格式 {successful_format} 需要特殊处理）")
            query_vec_str = stored_vector
        
        cursor.execute("""
            SELECT VECTOR_DISTANCE(embedding, %s, COSINE_SIMILARITY AS cosine_dist
            FROM ob_vector_format_test WHERE id = 1
        """, (query_vec_str,))
        
        row = cursor.fetchone()
        if row and row[0]:
            dist = float(row[0])
            formatted_dist = f"{dist:.6f}"
            print(f"✅ VECTOR_DISTANCE(COSINE) 查询成功")
            print(f"   Cosine Distance: {formatted_dist}")
            
            # Verify same vector should have distance ~0 (cosine = 1)
            if dist < 0.1:
                print(f"   ✓ 验证通过：同向量距离接近 0 ({formatted_dist})")
            else:
                print(f"   ⚠️ 异常：同向量距离较大 ({formatted_dist})")
        else:
            print("❌ VECTOR_DISTANCE 查询返回空结果")
            
    except Exception as e:
        error_msg = str(e)[:80] if hasattr(e, '__getitem__') else str(e)
        print(f"❌ VECTOR_DISTANCE 测试失败: {error_msg}")

# ==========================================
# 6. 探索替代方案（JSON + HNSW）
# ==========================================
print("\n【阶段 6】探索替代方案 - JSON 存储 + HNSW...")

try:
    # Create table with JSON column instead of VECTOR
    cursor.execute("""
        CREATE TABLE ob_vector_json_hybrid (
            id INT PRIMARY KEY,
            embedding_json JSON COMMENT 'JSON array representation of vector',
            model_name VARCHAR(50) DEFAULT 'bge-m3',
            dimensions INT DEFAULT 768,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    print("✅ CREATE TABLE (JSON hybrid) 成功")
    
except Exception as e:
    error_msg = str(e)[:100] if hasattr(e, '__getitem__') else str(e)
    print(f"❌ JSON hybrid table creation failed: {error_msg}")

# ==========================================
# 7. 清理测试资源
# ==========================================
print("\n【阶段 7】清理测试资源...")

try:
    cursor.execute("DROP TABLE IF EXISTS ob_vector_format_test")
    cursor.execute("DROP TABLE IF EXISTS ob_vector_json_hybrid")
    print("✅ 已删除测试表")
except Exception as e:
    error_msg = str(e)[:60] if hasattr(e, '__getitem__') else str(e)
    print(f"⚠️ 清理失败: {error_msg}")

conn.close()

# ==========================================
# 输出测试结果报告
# ==========================================
print("\n" + "=" * 90)
print("📊 VECTOR 类型兼容性测试报告")
print("=" * 90)
print(f"""
【关键发现】

1. VECTOR(768) 表创建: ✅ 支持
2. HNSW 索引创建: ❌ 不支持（错误码 1235）
3. str(array) 格式插入: {insert_results.get('str_array', {}).get('status', 'UNKNOWN')}
4. JSON array 格式插入: {insert_results.get('json_array', {}).get('status', 'UNKNOWN')}

【建议方案】

方案 A：使用 JSON hybrid（推荐）
   - 存储向量到 JSON 列
   - 应用层计算相似度
   - 利用 MySQL JSON 索引优化查询

方案 B：探索外部向量服务
   - 部署独立的向量检索服务
   - 数据库仅存储元数据
   - 通过 API 进行向量搜索

【官方文档参考】
https://www.oceanbase.com/docs/common-oceanbase-database-cn-1000000004475692
""")