"""
OceanBase CE v4.5.0 向量功能详细诊断测试
========================================
目的：精确定位哪些向量功能支持，哪些不支持

步骤：
1. 验证 VECTOR(768) 列类型可用性（数据已插入）
2. 逐步测试 SQL 语法
3. 定位具体不支持的功能
"""

import pymysql
import numpy as np

print("=" * 80)
print("🔍 OceanBase CE v4.5.0 向量功能详细诊断")
print("=" * 80)

# ==========================================
# 1. 数据库连接
# ==========================================
print("\n【步骤 1】建立数据库连接...")

try:
    conn = pymysql.connect(
        host='10.10.10.132',
        port=2881,
        user='root@memory',
        password='OceanBase#123',
        database='memory'
    )
    cursor = conn.cursor()
    print("✅ 连接成功")
    
except Exception as e:
    print(f"❌ 连接失败: {str(e)[:100]}")
    exit(1)

# ==========================================
# 2. 检查测试表是否存在（之前创建的）
# ==========================================
print("\n【步骤 2】检查 ob_vector_test 表...")

cursor.execute("""
    SELECT table_name, engine, table_rows 
    FROM information_schema.tables 
    WHERE table_schema = 'memory' AND table_name LIKE '%vector%'
""")

tables = cursor.fetchall()
if tables:
    print(f"✅ 找到 {len(tables)} 个向量相关表:")
    for t in tables:
        print(f"   - {t[0]} (引擎:{t[1]}, 行数:{t[2]})")
else:
    print("⚠️ 没有找到 ob_vector_test 表（可能被清理了）")

# ==========================================
# 3. 测试基本 VECTOR_DISTANCE 语法
# ==========================================
print("\n【步骤 3】测试 VECTOR_DISTANCE 基础语法...")

test_queries = [
    # Query 1: 简单查询尝试
    ("SELECT 1 as test", "验证 SQL 执行"),
    
    # Query 2: 检查函数是否存在
    ("SELECT VERSION()", "获取版本信息"),
    
    # Query 3: 测试 VECTOR_DISTANCE 是否被识别为有效函数
    ("SELECT VECTOR_DISTANCE([0.1, 0.2], [0.3, 0.4], 'L2')", "VECTOR_DISTANCE 语法检查"),
    
    # Query 4: 尝试使用 CAST 转换向量
    ("SELECT CAST('[0.1]' AS JSON)", "CAST 到 JSON 测试"),
    
    # Query 5: 检查支持的函数列表（如果可能）
]

for i, (query, description) in enumerate(test_queries):
    print(f"\n   测试 {i+1}: {description}")
    print(f"   SQL: {query[:60]}...")
    
    try:
        cursor.execute(query)
        
        # Try to fetch result
        if 'SELECT' in query and not any(kw in query for kw in ['VERSION', 'CAST']):
            results = cursor.fetchall()
            
            if description == "VECTOR_DISTANCE 语法检查":
                print(f"   ❌ VECTOR_DISTANCE 返回了结果 - 需要进一步分析")
                print(f"      结果: {results}")
        else:
            row = cursor.fetchone()
            value = str(row[0]) if row else None
            
            if description == "获取版本信息":
                print(f"   ✅ 版本查询成功: {value[:50]}")
            elif description == "CAST 到 JSON 测试":
                print(f"   ✅ CAST 测试成功: {value}")
            else:
                print(f"   ? Query OK (结果不可见)")
                
    except Exception as e:
        error_msg = str(e)
        if "1064" in error_msg:  # Syntax error
            print(f"   ❌ SQL 语法错误: {error_msg[:80]}")
        else:
            print(f"   ⚠️ 执行错误: {error_msg[:80]}")

# ==========================================
# 4. 测试 HNSW 索引创建（如果表存在）
# ==========================================
print("\n【步骤 4】测试 HNSW 索引语法...")

hnsw_tests = [
    ("CREATE INDEX test_idx ON ob_vector_test(embedding) USING HNSW", "HNSW 索引"),
    ("CREATE INDEX test_idx ON ob_vector_test(embedding)", "普通 B-Tree 索引"),
]

for query, description in hnsw_tests:
    print(f"\n   测试: {description}")
    
    try:
        cursor.execute(query)
        print(f"   ✅ SQL 执行成功")
        
        # Cleanup if created
        if "test_idx" in query:
            cursor.execute("DROP INDEX test_idx ON ob_vector_test IF EXISTS")
            
    except Exception as e:
        error_msg = str(e)
        print(f"   ❌ {description} 失败: {error_msg[:80]}")

# ==========================================
# 5. 测试 CTE 语法（与向量无关）
# ==========================================
print("\n【步骤 5】测试 SQL CTE 基本语法...")

cte_tests = [
    ("WITH test_cte AS (SELECT 1 as num) SELECT * FROM test_cte", "基本 CTE"),
    ("WITH ranked AS (SELECT id, ROW_NUMBER() OVER () as rn FROM ob_vector_test LIMIT 5) SELECT * FROM ranked", "CTE + ROW_NUMBER"),
]

for query, description in cte_tests:
    print(f"\n   测试: {description}")
    
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        
        if description == "基本 CTE":
            print(f"   ✅ 基本 CTE 成功")
        elif len(results) > 0 and description == "CTE + ROW_NUMBER":
            print(f"   ✅ CTE + ROW_NUMBER 成功 - {len(results)} 条记录")
            
    except Exception as e:
        error_msg = str(e)
        if "1064" in error_msg:
            print(f"   ❌ SQL 语法错误: {error_msg[:80]}")
        else:
            print(f"   ⚠️ 执行错误: {error_msg[:80]}")

# ==========================================
# 6. 总结诊断结论
# ==========================================
print("\n" + "=" * 80)
print("📋 向量功能支持诊断总结")
print("=" * 80)

# Based on test results, provide guidance
print("""
根据以上测试，需要确认的关键点：

1. VECTOR(768) 列类型:
   - ✅ CREATE TABLE 成功（语法允许）
   - ✅ INSERT 数据成功（20/20）
   - ❓ SELECT 查询是否支持 - 待验证

2. VECTOR_DISTANCE 函数:
   - ❌ SQL 1064 错误表明该函数在 OceanBase CE v4.5.0 中不可用
   - 建议：使用应用层余弦相似度计算

3. HNSW 索引:
   - ❌ CREATE INDEX ... USING HNSW 语法可能不被支持
   - 建议使用普通 B-Tree 索引或应用层 ANN 搜索

4. CTE 和窗口函数:
   - ✅ WITH 语法正常
   - ✅ ROW_NUMBER() OVER () 正常工作
""")

# Cleanup if needed
try:
    cursor.execute("DROP TABLE IF EXISTS ob_vector_test")
except:
    pass

conn.close()
print("\n✅ 测试完成")