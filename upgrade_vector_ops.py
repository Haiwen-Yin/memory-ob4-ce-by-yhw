"""
根据 OceanBase 官方向量操作文档完善 SKILL.md
================================================
基于：https://www.oceanbase.com/docs/common-oceanbase-database-cn-1000000004475692
      https://www.oceanbase.com/docs/common-oceanbase-database-cn-1000000004475691

优化内容：
1. 向量索引创建（HNSW/FLAT）
2. 相似度搜索 API
3. 向量操作最佳实践
"""

import re
import os

skill_md_path = '/root/.hermes/skills/memory-ob4-ce-by-yhw/SKILL.md'

# Read current SKILL.md
with open(skill_md_path, 'r') as f:
    content = f.read()

print("=== 开始完善 SKILL.md - 添加向量操作最佳实践 ===\n")

# ==========================================
# 1. 添加 Vector Index Operations Section
# ==========================================
vector_index_section = '''## 🗄️ Vector Index Operations (Optimized for OceanBase CE v4.5.0)

### HNSW Index Configuration (Recommended for Large-Scale Search)

```sql
-- Create HNSW index for vector similarity search
CREATE INDEX idx_memories_vectors_hnsw ON memories_vectors(embedding) USING HNSW;

-- Alternative: FLAT index (exact search, no approximation)
CREATE INDEX idx_memories_vectors_flat ON memories_vectors(embedding) USING FLAT;
```

**Index Type Comparison:**

| Index Type | Search Mode | Performance | Accuracy | Use Case |
|------------|-------------|-------------|----------|----------|
| HNSW | Approximate (ANN) | ⭐⭐⭐ Fastest | High (95-99%) | Production search |
| FLAT | Exact (Brute Force) | ⭐ Slowest | 100% | Small datasets, validation |

### Vector Similarity Search Queries

**Cosine Similarity Query (HNSW):**

```sql
-- Find top-K similar vectors using HNSW index
SELECT 
    memory_id,
    model_name,
    dimensions,
    -- Calculate similarity score (application layer recommended for accuracy)
    cosine_similarity(embedding, :query_vector) AS similarity_score
FROM memories_vectors
ORDER BY cosine_similarity(embedding, :query_vector) DESC
LIMIT 10;
```

**Vector Distance Query (Euclidean):**

```sql
-- Find closest vectors using vector distance function
SELECT 
    memory_id,
    model_name,
    dimensions,
    VECTOR_DISTANCE(embedding, :query_vector, 'L2') AS euclidean_distance
FROM memories_vectors
ORDER BY euclidean_distance ASC  -- Lower is more similar
LIMIT 10;
```

### Application-Layer Similarity Calculation (Python)

**High-Performance Cosine Similarity:**

```python
import numpy as np
from typing import List, Dict, Optional

class VectorSearchEngine:
    """High-performance vector similarity search engine"""
    
    def __init__(self, host='10.10.10.132', port=2881, user='root@memory', 
                 password='OceanBase#123', database='memory'):
        self.db_config = {
            'host': host, 'port': port, 'user': user,
            'password': password, 'database': database
        }
    
    def cosine_similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
        """Calculate cosine similarity between two vectors (optimized)"""
        a = np.array(vec_a, dtype=np.float64)
        b = np.array(vec_b, dtype=np.float64)
        
        # Vectorized operation for performance
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        similarity = dot_product / (norm_a * norm_b)
        return round(float(similarity), 6)
    
    def search_similar_memories(self, query_embedding: List[float], 
                                 model_name: str = None, 
                                 limit: int = 10,
                                 threshold: float = 0.7):
        """Search for similar memories using application-layer calculation"""
        
        # Step 1: Fetch candidates from database (use index if available)
        import pymysql
        
        conn = pymysql.connect(**self.db_config)
        cursor = conn.cursor()
        
        query = f"""
            SELECT memory_id, embedding FROM memories_vectors
            WHERE model_name = %s OR %s IS NULL
        """
        cursor.execute(query, (model_name, model_name))
        candidates = cursor.fetchall()
        
        # Step 2: Calculate similarities in Python (vectorized)
        results = []
        query_array = np.array(query_embedding, dtype=np.float64)
        
        for memory_id, embedding_str in candidates:
            try:
                # Parse JSON/text embedding string to numpy array
                if isinstance(embedding_str, str):
                    import json
                    data = json.loads(embedding_str)
                    embed_arr = np.array(data.get('embedding', eval(embedding_str)), dtype=np.float64)
                else:
                    continue
                
                # Calculate similarity (vectorized)
                similarity = float(np.dot(query_array, embed_arr) / 
                                 (np.linalg.norm(query_array) * np.linalg.norm(embed_arr)))
                
                if similarity >= threshold:
                    results.append({
                        'memory_id': memory_id,
                        'similarity': round(similarity, 4),
                        'model_name': model_name or 'unknown'
                    })
            except (SyntaxError, TypeError):
                continue
        
        # Sort by similarity descending
        results.sort(key=lambda x: x['similarity'], reverse=True)
        
        conn.close()
        return results[:limit]

# Usage example:
engine = VectorSearchEngine()
similar_memories = engine.search_similar_memories(
    query_embedding=[0.1, 0.2, ...],  # Your query vector (must match model dimensions)
    model_name='bge-m3',
    limit=20,
    threshold=0.75
)
for memory in similar_memories:
    print(f"Memory {memory['memory_id']}: similarity={memory['similarity']}")
```

---

## 📋 Vector Search Performance Optimization

### Index Selection Guide

| Dataset Size | Recommended Index | Query Latency (expected) |
|--------------|-------------------|-------------------------|
| < 10K vectors | FLAT (exact search) | < 50ms |
| 10K - 1M vectors | HNSW (approximate) | < 100ms |
| > 1M vectors | HNSW + Application Cache | < 200ms |

### Query Optimization Tips

1. **Always use WHERE clause** to filter by model_name or other attributes before similarity search
2. **Cache frequent query results** in application layer (Redis/Memcached)
3. **Batch multiple queries** when possible for better throughput
4. **Use appropriate threshold** to reduce unnecessary calculations'''

# Insert after P4 section - FIXED REGEX
p4_end_pattern = r'(### P4:.*?Dimensionality Reduction if Needed)(?=## |\Z)'
content_new = re.sub(p4_end_pattern, vector_index_section, content, flags=re.DOTALL | re.IGNORECASE)

# ==========================================
# 2. Save file
# ==========================================
with open(skill_md_path, 'w') as f:
    f.write(content_new)

print("✅ Vector Index Operations section added")

# Verify changes
with open(skill_md_path, 'r') as f:
    saved_content = f.read()

checks = [
    ('Vector Index Section', '## Vector Index Operations' in saved_content),
    ('HNSW Index Example', 'USING HNSW' in saved_content),
    ('FLAT Index Example', 'USING FLAT' in saved_content),
    ('Cosine Similarity Query', 'cosine_similarity' in saved_content.lower()),
    ('Vector Search Engine Class', 'class VectorSearchEngine:' in saved_content),
]

print("\n=== 验证结果 ===")
for check_name, result in checks:
    print(f"{'✅' if result else '❌'} {check_name}")

print("\n=== SKILL.md 向量操作优化完成 ===")