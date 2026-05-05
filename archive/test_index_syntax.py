"""
OceanBase CE v4.5.0 向量索引语法探索测试
========================================
尝试不同的 INDEX 创建语法来确定正确的 HNSW 向量索引方式

连接信息:
- Host: 10.10.10.132, Port: 2881
- User: root@memory, Password: OceanBase#123
- Database: memory
"""

import pymysql

print("=" * 90)
print("🔍 OceanBase CE v4.5.0 向量索引语法探索")
print("=" * 90)

conn = None
cursor = None

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
    print(f"\n版本信息: {cursor.fetchone()[0]}")
    
except Exception as e:
    print(f"❌ 连接失败: {str(e)[:100]}")
    exit(1)

# ==========================================
# 测试方案汇总
# ==========================================
test_cases = [
    {
        "name": "CREATE TABLE 标准语法",
        "sql": """
            CREATE TABLE vector_test_1 (
                id INT PRIMARY KEY,
                embedding VECTOR(768),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """,
        "type": "create_table"
    },
    {
        "name": "CREATE INDEX 无 USING 子句",
        "sql": "CREATE INDEX idx_v ON vector_test_1(embedding)",
        "type": "create_index",
        "requires_table": True
    },
    {
        "name": "SHOW TABLE STATUS",
        "sql": "SHOW TABLE STATUS LIKE 'vector_test_%'",
        "type": "query"
    },
    {
        "name": "SHOW INDEX FROM vector_test_1",
        "sql": "SHOW INDEX FROM vector_test_1",
        "type": "query",
        "requires_table": True
    }
]

# ==========================================
# 执行测试方案
# ==========================================
for i, test in enumerate(test_cases):
    print(f"\n--- 测试 {i+1}: {test['name']} ---")
    
    try:
        if test.get('requires_table') and 'vector_test_1' not in globals():
            # Skip if required table doesn't exist
            print("   跳过（需要表已存在）")
            continue
            
        cursor.execute(test["sql"])
        
        if test["type"] == "query":
            rows = cursor.fetchall()
            if rows:
                for row in rows[:3]:  # Limit output
                    print(f"   结果: {row}")
            else:
                print("   (无返回数据)")
        else:
            print("   ✅ SQL 执行成功")
            
    except Exception as e:
        error_msg = str(e) if len(str(e)) < 200 else str(e)[:200]
        print(f"   ❌ 错误: {error_msg}")

# ==========================================
# 查看数据库支持的索引类型
# ==========================================
print("\n--- 查看数据库支持的索引选项 ---")

try:
    cursor.execute("SHOW VARIABLES LIKE '%index%'")
    for row in cursor.fetchall():
        print(f"   {row[0]} = {str(row[1])[:50] if row[1] else ''}")
except Exception as e:
    print(f"   ❌ 查询失败: {str(e)[:60]}")

# ==========================================
# 检查是否支持 SHOW INDEX 语法
# ==========================================
print("\n--- 尝试查看索引信息 ---")

try:
    # Try to find existing tables with VECTOR columns
    cursor.execute("""
        SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA = 'memory' AND DATA_TYPE LIKE '%VECTOR%'
    """)
    
    tables_with_vector = cursor.fetchall()
    if tables_with_vector:
        print("   找到包含 VECTOR 列的表:")
        for table in tables_with_vector:
            print(f"     - {table[0]}.{table[1]} ({table[2]})")
            
            # Try to show index on each table
            try:
                cursor.execute(f"SHOW INDEX FROM {table[0]}")
                indexes = cursor.fetchall()
                if indexes:
                    print("       现有索引:")
                    for idx in indexes[:5]:
                        print(f"         - Index: {idx[2]}, Type: {idx[7] if len(idx) > 7 else 'N/A'}")
            except Exception as e:
                print(f"         (无法查看索引: {str(e)[:40]})")
    else:
        print("   未找到包含 VECTOR 列的表")
        
except Exception as e:
    print(f"❌ 查询失败: {str(e)[:60]}")

# ==========================================
# 输出结论和建议
# ==========================================
print("\n" + "=" * 90)
print("📋 探索结果总结")
print("=" * 90)
print("""
根据以上测试结果，请记录以下关键信息：

1. CREATE TABLE ... VECTOR(768) - 是否成功？
2. SHOW INDEX 返回的索引类型是什么？
3. 是否有其他索引创建语法可用？

这些结果将帮助我们确定正确的 HNSW 向量索引创建方式。
""")

# Cleanup
try:
    cursor.execute("DROP TABLE IF EXISTS vector_test_1")
except:
    pass

conn.close()