"""
OceanBase CE v4.5.0 向量函数最终验证（修正版）
========================================================
根据胖头鱼提示，OB 中正确的函数名是：
- VECTOR_DISTANCE
- VECTOR_SIMILARITY  
- COSINE_SIMILARITY

重新测试这些函数的正确调用方式
"""

import pymysql
from decimal import Decimal

print("=" * 90)
print("🧪 OceanBase CE v4.5.0 向量函数最终验证")
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
# 2. 生成测试向量（JSON array 格式）
# ==========================================
print("\n【阶段 2】生成 JSON array 格式的测试向量...")

import json
import numpy as np

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
vector_json_str = json.dumps(test_vector)

print(f"✅ 生成向量（JSON array，768 维）")

# ==========================================
# 3. 创建表并插入数据
# ==========================================
print("\n【阶段 3】创建 VECTOR(768) 表并插入向量...")

try:
    # Clean up first
    cursor.execute("DROP TABLE IF EXISTS ob_vector_func_test")
    
    # Create table with standard syntax
    cursor.execute("""
        CREATE TABLE ob_vector_func_test (
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
# 4. 插入 JSON array 格式的向量数据
# ==========================================
print("\n【阶段 4】插入 JSON array 格式的向量数据...")

try:
    sql = "INSERT INTO ob_vector_func_test (id, embedding, model_name, dimensions) VALUES (%s, %s, %s, %s)"
    
    cursor.execute(sql, (1, vector_json_str, 'bge-m3', 768))
    
    # Verify insertion by reading back
    cursor.execute("SELECT embedding FROM ob_vector_func_test WHERE id = 1")
    row = cursor.fetchone()
    
    if row and row[0]:
        print(f"✅ 向量插入成功!")
        stored_json_preview = str(row[0])[:80] + "..."
        print(f"   JSON 预览: {stored_json_preview}")
    else:
        print("❌ 插入后无法读取数据")
        
except Exception as e:
    error_msg = str(e)[:100] if hasattr(e, '__getitem__') else str(e)
    print(f"❌ 向量插入失败: {error_msg}")
    exit(1)

# ==========================================
# 5. 测试所有可能的向量函数调用方式
# ==========================================
print("\n【阶段 5】全面测试向量函数调用...")

function_tests = [
    # VECTOR_DISTANCE tests
    ("VECTOR_DISTANCE with CAST", "SELECT VECTOR_DISTANCE(CAST(%s AS JSON), CAST(%s AS JSON))"),
    ("VECTOR_DISTANCE direct", "SELECT VECTOR_DISTANCE(embedding, %s) FROM ob_vector_func_test WHERE id = 1"),
    
    # VECTOR_SIMILARITY tests  
    ("VECTOR_SIMILARITY with CAST", "SELECT VECTOR_SIMILARITY(CAST(%s AS JSON), CAST(%s AS JSON))"),
    ("VECTOR_SIMILARITY direct", "SELECT VECTOR_SIMILARITY(embedding, %s) FROM ob_vector_func_test WHERE id = 1"),
    
    # COSINE_SIMILARITY tests
    ("COSINE_SIMILARITY with CAST", "SELECT COSINE_SIMILARITY(CAST(%s AS JSON), CAST(%s AS JSON))"),
    ("COSINE_SIMILARITY direct", "SELECT COSINE_SIMILARITY(embedding, %s) FROM ob_vector_func_test WHERE id = 1"),
]

for test_name, query in function_tests:
    print(f"\n   [{test_name}]")
    
    try:
        # Prepare parameters based on query structure
        if "%s AS JSON" in query:
            cursor.execute(query, (vector_json_str, vector_json_str))
        else:
            cursor.execute(query, (vector_json_str,))
            
        result = cursor.fetchone()
        
        if result and len(result) > 0:
            val = result[0]
            if val is not None:
                # Convert Decimal to float for display
                if isinstance(val, Decimal):
                    str_val = f"{float(val):.6f}"
                else:
                    str_val = str(val)
                
                preview = str_val[:50] + "..." if len(str_val) > 50 else str_val
                print(f"     ✅ 返回: {preview}")
            elif val is None:
                print(f"     ⚠️ 返回 NULL（函数存在但未实现）")
        else:
            print(f"     ❌ 无结果")
            
    except Exception as e:
        error_msg = str(e)
        
        # Check if this is a "function doesn't exist" vs syntax error
        if 'doesn\'t exist' in error_msg or 'not defined' in error_msg or 'unknown function' in error_msg.lower():
            print(f"     ❌ 函数不存在")
        elif 'syntax' in error_msg.lower() or 'error' in error_msg.lower():
            err_code = error_msg.split(',')[0].strip('()').split()[1] if ',' in error_msg else "N/A"
            print(f"     ❌ SQL 错误 (code: {err_code})")
        else:
            preview = error_msg[:80] + "..." if len(error_msg) > 80 else error_msg
            print(f"     ❌ 错误: {preview}")

# ==========================================
# 6. 尝试使用 SQLcl 直接测试（如果可用）
# ==========================================
print("\n【阶段 6】检查 SQLcl 可用性...")

try:
    import subprocess
    
    # Check if sql command is available
    result = subprocess.run(["which", "sql"], capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ SQLcl 可用: {result.stdout.strip()}")
        
        # Try to run a simple query with SQLcl
        sql_query = "SELECT VECTOR_SIMILARITY(CAST('[]' AS JSON), CAST('[]' AS JSON)) FROM DUAL;"
        cmd_result = subprocess.run(
            f"echo '{sql_query}' | /root/sqlcl/sqlcl/bin/sql root@10.10.10.132:2881/memory 2>&1",
            shell=True, capture_output=True, text=True, timeout=30
        )
        
        if cmd_result.stdout:
            print(f"   SQLcl 输出预览:")
            for line in cmd_result.stdout.split('\n')[:5]:
                print(f"     {line}")
    else:
        print("❌ SQLcl 不可用")
        
except Exception as e:
    print(f"⚠️ SQLcl 检查失败: {str(e)[:60]}")

# ==========================================
# 7. 清理测试资源
# ==========================================
print("\n【阶段 7】清理测试资源...")

try:
    cursor.execute("DROP TABLE IF EXISTS ob_vector_func_test")
    print("✅ 已删除测试表")
except Exception as e:
    error_msg = str(e)[:60] if hasattr(e, '__getitem__') else str(e)
    print(f"⚠️ 清理失败: {error_msg}")

conn.close()

# ==========================================
# 输出测试总结报告
# ==========================================
print("\n" + "=" * 90)
print("📊 OceanBase CE v4.5.0 向量函数验证最终报告")
print("=" * 90)

# Collect function statuses for summary
function_statuses = {}
for test_name, query in function_tests:
    if "VECTOR_DISTANCE" in test_name and not "SIMILARITY" in test_name:
        key = "VECTOR_DISTANCE"
    elif "VECTOR_SIMILARITY" in test_name:
        key = "VECTOR_SIMILARITY"
    elif "COSINE_SIMILARITY" in test_name:
        key = "COSINE_SIMILARITY"
    
    if key and key not in function_statuses:
        # Re-check the last result for this type
        try:
            cursor.execute(query, (vector_json_str, vector_json_str))
            result = cursor.fetchone()
            
            if result and len(result) > 0 and result[0] is not None:
                val = result[0]
                if isinstance(val, Decimal):
                    str_val = f"{float(val):.6f}"
                else:
                    str_val = str(val)
                function_statuses[key] = f"✅ 可用 (返回值: {str_val[:30]}...)"
            elif result and result[0] is None:
                function_statuses[key] = "⚠️ 函数存在但未实现（返回 NULL）"
            else:
                function_statuses[key] = "❌ 不可用（无结果或错误）"
        except Exception as e:
            if 'doesn\'t exist' in str(e) or 'not defined' in str(e):
                function_statuses[key] = "❌ 函数不存在"
            else:
                function_statuses[key] = f"❌ 错误 ({str(e)[:40]}...)"

print(f"""
【结论】

根据以上测试，请记录以下关键信息：

1. VECTOR_DISTANCE: {function_statuses.get('VECTOR_DISTANCE', '未测试')}（如果成功则显示返回值）
2. VECTOR_SIMILARITY: {function_statuses.get('VECTOR_SIMILARITY', '未测试')}（如果成功则显示返回值）
3. COSINE_SIMILARITY: {function_statuses.get('COSINE_SIMILARITY', '未测试')}（如果成功则显示返回值）

【建议】

根据测试结果决定后续方案：
- 如果函数可用：更新 SKILL.md 包含正确的 SQL 查询语法
- 如果函数不可用：继续使用应用层计算相似度 + JSON 存储

【官方文档参考】
https://www.oceanbase.com/docs/common-oceanbase-database-cn-1000000004475692
""")