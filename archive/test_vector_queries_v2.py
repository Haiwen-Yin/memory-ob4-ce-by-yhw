"""
OceanBase CE v4.5.0 向量查询完整测试（修正版）
================================================
修正：解决 VECTOR(768) 数据插入问题
"""

import pymysql
import numpy as np
from typing import List, Dict

print("=" * 80)
print("🧪 OceanBase CE v4.5.0 向量查询完整测试")
print("=" * 80)

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
    cursor.execute("SELECT @@version_comment, @@version")
    version_row = cursor.fetchone()
    print(f"✅ 连接成功!")
    print(f"   版本: {version_row[0]}")
    
except Exception as e:
    print(f"❌ 连接失败: {str(e)[:100]}")
    exit(1)

# ==========================================
# 2. 生成测试向量数据（BGE-M3 格式，768 维）
# ==========================================
print("\n【阶段 2】生成测试向量数据...")

def generate_test_vectors(count: int, dimensions: int = 768) -> List[List[float]]:
    """Generate test vectors with consistent patterns for verification"""
    import random
    
    # Use seed for reproducibility
    random.seed(42)
    
    vectors = []
    for i in range(count):
        # Generate vector with some structure (not purely random)
        base_value = 0.1 + (i * 0.001)  # Base pattern
        vector = [round(base_value + np.random.normal(0, 0.1), 6) for _ in range(dimensions)]
        
        # Normalize to unit length (for cosine similarity)
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = [v / norm for v in vector]
            
        vectors.append((i + 1, vector))  # (id, vector_array)
    
    return vectors

test_vectors = generate_test_vectors(20, 768)
print(f"✅ 生成 {len(test_vectors)} 个测试向量（每维 768）")

# ==========================================
# 3. 创建 VECTOR(768) 测试表
# ==========================================
print("\n【阶段 3】创建 VECTOR(768) 测试表...")

try:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ob_vector_test (
            id INT PRIMARY KEY,
            embedding VECTOR(768),
            model_name VARCHAR(50) DEFAULT 'bge-m3',
            dimensions INT DEFAULT 768,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)
    print("✅ CREATE TABLE (VECTOR(768)) - Query OK")
    
except Exception as e:
    print(f"❌ 表创建失败: {str(e)[:100]}")
    exit(1)

# ==========================================
# 4. 插入测试向量数据（修正插入方式）
# ==========================================
print("\n【阶段 4】插入测试向量数据...")

try:
    insert_count = 0
    
    for vector_id, vector_array in test_vectors:
        # Try different formats for VECTOR insertion
        # Format 1: Direct string representation of array
        try:
            vector_str = str(vector_array)
            
            cursor.execute("""
                INSERT INTO ob_vector_test (id, embedding) VALUES (%s, %s)
            """, (vector_id, vector_str))
            
            insert_count += 1
            
        except Exception as e1:
            # Format 2: JSON string representation
            try:
                import json
                vector_json = json.dumps([round(v, 6) for v in vector_array])
                
                cursor.execute("""
                    INSERT INTO ob_vector_test (id, embedding) VALUES (%s, %s)
                """, (vector_id, vector_json))
                
                insert_count += 1
                
            except Exception as e2:
                print(f"   ⚠️ ID={vector_id} 插入失败: {str(e1)[:50]} / {str(e2)[:50]}")
                continue
    
    print(f"✅ 成功插入 {insert_count}/{len(test_vectors)} 条向量记录")
    
except Exception as e:
    print(f"❌ 数据插入失败: {str(e)[:100]}")
    exit(1)

# ==========================================
# 5. 测试 VECTOR_DISTANCE COSINE 函数
# ==========================================
print("\n【阶段 5】测试 VECTOR_DISTANCE(COSINE) 函数...")

try:
    # Test query vector (first test vector as reference)
    test_query_vector = str(test_vectors[0][1]) if insert_count > 0 else "[0.1] * 768"
    
    cursor.execute("""
        SELECT id, model_name, dimensions, 
               VECTOR_DISTANCE(embedding, %s, COSINE_SIMILARITY AS cosine_distance
        FROM ob_vector_test
        WHERE id = 1
    """, (test_query_vector,))
    
    row = cursor.fetchone()
    if row:
        print(f"✅ VECTOR_DISTANCE(COSINE) 查询成功")
        print(f"   向量 ID: {row[0]}")
        print(f"   模型: {row[1]}, 维度: {row[2]}")
        
        cosine_dist = float(row[3]) if row[3] else None
        if cosine_dist is not None:
            print(f"   Cosine Distance: {cosine_dist:.6f}")
            
            # Verify same vector should have distance ~0 (cosine = 1)
            print(f"   验证：同向量距离应接近 0，实际值：{cosine_dist:.6f}")
    else:
        print("❌ 查询返回空结果")
        
except Exception as e:
    print(f"❌ COSINE 距离查询失败: {str(e)[:100]}")

# ==========================================
# 6. 测试 VECTOR_DISTANCE L2 函数
# ==========================================
print("\n【阶段 6】测试 VECTOR_DISTANCE(L2) 函数...")

try:
    cursor.execute("""
        SELECT id, model_name, dimensions,
               VECTOR_DISTANCE(embedding, %s, L2 AS l2_distance
        FROM ob_vector_test
        WHERE id = 1
    """, (test_query_vector,))
    
    row = cursor.fetchone()
    if row:
        print(f"✅ VECTOR_DISTANCE(L2) 查询成功")
        
        l2_dist = float(row[3]) if row[3] else None
        if l2_dist is not None:
            print(f"   L2 Distance: {l2_dist:.6f}")
        
except Exception as e:
    print(f"❌ L2 距离查询失败: {str(e)[:100]}")

# ==========================================
# 7. 测试 SQL CTE 排名查询
# ==========================================
print("\n【阶段 7】测试 SQL CTE 排名查询...")

try:
    cursor.execute("""
        WITH scored_memories AS (
            SELECT 
                id,
                model_name,
                dimensions,
                VECTOR_DISTANCE(embedding, %s, COSINE_SIMILARITY AS cosine_distance,
                RANK() OVER (ORDER BY VECTOR_DISTANCE(embedding, %s, COSINE_SIMILARITY) as sim_rank
            FROM ob_vector_test
        )
        SELECT * FROM scored_memories
        ORDER BY cosine_distance ASC
        LIMIT 10;
    """, (test_query_vector, test_query_vector))
    
    results = cursor.fetchall()
    print(f"✅ SQL CTE 排名查询成功 - 返回 {len(results)} 条结果")
    
    # Show top 5 most similar vectors
    print("\n   Top-5 最相似向量:")
    for i, row in enumerate(results[:5]):
        memory_id, model_name, dimensions, cosine_distance, sim_rank = row
        
        similarity_score = None
        if cosine_distance is not None:
            try:
                similarity_score = round(1.0 - float(cosine_distance), 4)
            except:
                similarity_score = "N/A"
        
        print(f"     {i+1}. ID={memory_id}, Model={model_name}, "
              f"Distance={cosine_distance}, Similarity={similarity_score}")
        
except Exception as e:
    print(f"❌ CTE 排名查询失败: {str(e)[:100]}")

# ==========================================
# 8. 测试 HNSW 索引 ANN 搜索
# ==========================================
print("\n【阶段 8】测试 HNSW 索引 ANN 搜索...")

try:
    # Create HNSW index
    cursor.execute("""
        CREATE INDEX idx_vector_test_hnsw ON ob_vector_test(embedding) USING HNSW;
    """)
    print("✅ HNSW 索引创建成功")
    
    # Query with index hint
    cursor.execute("""
        SELECT /*+ INDEX(m idx_vector_test_hnsw) */
            m.id,
            m.model_name,
            VECTOR_DISTANCE(m.embedding, %s, COSINE_SIMILARITY AS similarity_score
        FROM ob_vector_test m
        ORDER BY similarity_score ASC
        LIMIT 10;
    """, (test_query_vector,))
    
    results = cursor.fetchall()
    print(f"✅ HNSW ANN 搜索成功 - 返回 {len(results)} 条结果")
    
except Exception as e:
    print(f"❌ HNSW 索引测试失败: {str(e)[:100]}")

# ==========================================
# 清理测试资源
# ==========================================
print("\n【阶段 9】清理测试资源...")

try:
    cursor.execute("DROP INDEX idx_vector_test_hnsw ON ob_vector_test")
    cursor.execute("DROP TABLE IF EXISTS ob_vector_test")
    print("✅ HNSW 索引和表已删除")
except Exception as e:
    print(f"⚠️ 清理失败: {str(e)[:60]}")

conn.close()

# ==========================================
# 输出测试总结报告
# ==========================================
print("\n" + "=" * 80)
print("📊 向量查询完整测试报告")
print("=" * 80)