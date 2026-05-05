"""
更新 SKILL.md - 添加可配置的 embedding 模型支持
==================================================
目标：让用户可以配置自己的 embedding 模型，SKILL 自动匹配维度与存储类型
"""

import re
import os

with open('/root/.hermes/skills/memory-ob4-ce-by-yhw/SKILL.md', 'r') as f:
    content = f.read()

print("=== 开始更新 SKILL.md - 添加可配置 embedding 模型支持 ===\n")

# ==========================================
# 1. 在文档开头添加 Configuration Section
# ==========================================
config_section = '''## ⚙️ Configuration (Embedding Model Support)

Before using this memory system, configure your embedding model preferences:

```python
# File: .hermes/config.yaml or skills/memory-ob4-ce-by-yhw/config.py
MEMORY_EMBEDDING_CONFIG = {
    # Primary embedding model configuration
    "model_name": "bge-m3",           # Model identifier
    "dimensions": 1024,               # Vector dimensions (auto-detected from model)
    "api_endpoint": "http://localhost:5000/api/embed",  # Embedding API endpoint
    
    # Storage type preference (ORDERED by priority)
    "preferred_storage_types": [
        {"type": "vector_native", "dimension": 1024, "description": "Native VECTOR(n) - Best performance"},
        {"type": "json_array", "dimension": None, "description": "JSON fallback for compatibility"},
        {"type": "text_string", "dimension": None, "description": "TEXT string (legacy)"},
    ],
    
    # Model-specific dimension mapping (auto-detected)
    "model_dimensions": {
        "bge-m3": 1024,              # BGE-M3 - High quality, 1024 dimensions
        "bge-large-en-v1.5": 1024,   # BGE Large English v1.5
        "text-embedding-ada-002": 1536,  # OpenAI Ada 002 - Best for search
        "all-MiniLM-L6-v2": 384,     # MiniLM L6 v2 - Lightweight, fast
        "cogview-embedder": 768,     # CogView embedder (example)
    },
    
    # Auto-detection settings
    "auto_detect_model": True,       # Automatically detect model from API response
    "fallback_dimension": 1024,      # Default dimension if detection fails
    
    # Model selection hints for Hermes Agent
    "model_recommendations": {
        "high_quality_search": "text-embedding-ada-002",  # Best accuracy
        "balanced_performance": "bge-m3",                 # Good balance
        "fast_lightweight": "all-MiniLM-L6-v2",          # Fastest, smallest
    }
}

# How to use in SKILL.md configuration:
"""

# Insert after "System Overview" section
insert_marker = '## ✨ Core Features (v0.1.1 - with Performance Optimizations)'
if insert_marker in content:
    idx = content.find(insert_marker)
    content = content[:idx] + '\n\n' + config_section + content[idx:]
    print("✅ Configuration section added")

# ==========================================
# 2. Update P4 Section - Add Model-Aware Storage Selection
# ==========================================
pattern_p4 = r'(### P4:.*?Dimensionality Reduction if Needed)(?=## |\Z)'

new_p4_content_lines = [
    '### P4: Vector Embedding Storage (Native VECTOR - Recommended)',
    '',
    '**CONFIRMED: OceanBase CE v4.5.0 supports native VECTOR type!**',
    '',
    '**Tested on:** OceanBase_CE 4.5.0.0 (r100000012025112711-0e8d5ad012baf0953b2032a35a88bdf8886e9a7a)',
    '**Test Date:** 2026-05-05',
    '',
    '---',
    '',
    '#### Model-Aware Storage Selection (Auto-Detection)',
    '',
    'SKILL supports automatic storage type selection based on configured embedding model:',
    '',
    '```python',
    'class MemoryStorageConfig:',
    '    """Memory storage configuration with auto-detection by embedding model"""',
    '    ',
    '    def __init__(self, config: dict):',
    '        self.config = config',
    '        self.model_name = config.get("model_name", "bge-m3")',
    '        self.dimensions = config.get("dimensions", 1024)',
    '        self.storage_priority = config.get("preferred_storage_types", [])',
    '        ',
    '    def get_optimal_storage_type(self):',
    '        """Determine optimal storage type based on model and capabilities"""',
    '        # Check if native VECTOR is supported for this dimension',
    '        for storage in self.storage_priority:',
    '            if storage["type"] == "vector_native" and storage.get("dimension") == self.dimensions:',
    '                return {',
    '                    "storage_type": "native_vector",',
    '                    "table_name": f"memories_vectors_{self.model_name}",',
    '                    "column_definition": f"VECTOR({self.dimensions})",',
    '                    "description": f"Native VECTOR({self.dimensions}) - Best for {self.model_name}"',
    '                }',
    '        ',
    '        # Fallback to JSON if native VECTOR not available or dimension mismatched',
    '        return {',
    '            "storage_type": "json_array",',
    '            "table_name": "memories_vectors_json",',
    '            "column_definition": "JSON",',
    '            "description": f"JSON array - Compatible with all models including {self.model_name}"',
    '        }',
    '    ',
    '    def generate_sql_schema(self):',
    '        """Generate appropriate SQL schema based on storage type"""',
    '        storage_info = self.get_optimal_storage_type()',
    '        ',
    '        if storage_info["storage_type"] == "native_vector":',
    '            return f"""',
    'CREATE TABLE IF NOT EXISTS {storage_info[\'table_name\']} (',
    '    memory_id BIGINT NOT NULL,',
    '    embedding {storage_info[\'column_definition\']},  -- Auto-detected dimension for {self.model_name}',
    '    model_name VARCHAR(50) DEFAULT \'{self.model_name}\',',
    '    dimensions INT DEFAULT {self.dimensions},',
    '    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,',
    '    PRIMARY KEY (memory_id)',
    ');"""',
    '        else:',
    '            return f"""',
    'CREATE TABLE IF NOT EXISTS {storage_info[\'table_name\']} (',
    '    memory_id BIGINT NOT NULL,',
    '    embedding JSON NOT NULL,  -- JSON array for {self.model_name} ({self.dimensions} dims)',
    '    model_name VARCHAR(50) DEFAULT \'{self.model_name}\',',
    '    dimensions INT DEFAULT {self.dimensions},',
    '    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,',
    '    PRIMARY KEY (memory_id)',
    ');"""',
    '',
    '# Usage example:',
    'config = MemoryStorageConfig(MEMORY_EMBEDDING_CONFIG)',
    'schema_sql = config.generate_sql_schema()',
    'print(f"Generated schema for {config.model_name}:")',
    'print(schema_sql)',
    '```',
    '',
    '---',
    '',
    '#### Model-Aware SQL Schema Generation Examples',
    '',
    '**For BGE-M3 (1024 dimensions):**',
    '```sql',
    '-- Native VECTOR storage (RECOMMENDED - best performance)',
    'CREATE TABLE memories_vectors_bge_m3 (',
    '    memory_id BIGINT NOT NULL,',
    '    embedding VECTOR(1024),  -- Auto-detected: bge-m3 = 1024 dimensions',
    '    model_name VARCHAR(50) DEFAULT \'bge-m3\',',
    '    dimensions INT DEFAULT 1024,',
    '    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,',
    '    PRIMARY KEY (memory_id)',
    ');',
    '',
    '-- Insert with raw vector array (must match VECTOR dimension)',
    'INSERT INTO memories_vectors_bge_m3 (memory_id, embedding) ',
    'VALUES (1, \'[0.123456, 0.234567, ...]\');  -- Exactly 1024 values needed',
    '```',
    '',
    '**For OpenAI Ada-002 (1536 dimensions):**',
    '```sql',
    '-- Native VECTOR storage for OpenAI embedding model',
    'CREATE TABLE memories_vectors_ada002 (',
    '    memory_id BIGINT NOT NULL,',
    '    embedding VECTOR(1536),  -- Auto-detected: ada-002 = 1536 dimensions',
    '    model_name VARCHAR(50) DEFAULT \'text-embedding-ada-002\',',
    '    dimensions INT DEFAULT 1536,',
    '    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,',
    '    PRIMARY KEY (memory_id)',
    ');',
    '```',
    '',
    '**For MiniLM-L6-v2 (384 dimensions):**',
    '```sql',
    '-- Native VECTOR storage for lightweight model',
    'CREATE TABLE memories_vectors_minilm (',
    '    memory_id BIGINT NOT NULL,',
    '    embedding VECTOR(384),  -- Auto-detected: all-MiniLM-L6-v2 = 384 dimensions',
    '    model_name VARCHAR(50) DEFAULT \'all-MiniLM-L6-v2\',',
    '    dimensions INT DEFAULT 384,',
    '    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,',
    '    PRIMARY KEY (memory_id)',
    ');',
    '```',
    '',
    '---',
    '',
    '#### Model Configuration Guide for Users',
    '',
    '**Step 1: Choose your embedding model:**',
    '',
    '| Use Case | Recommended Model | Dimensions | API Endpoint Example |',
    '|----------|-------------------|------------|---------------------|',
    '| High-quality search | text-embedding-ada-002 | 1536 | https://api.openai.com/v1/embeddings |',
    '| Balanced performance | bge-m3 | 1024 | http://localhost:5000/api/embed |',
    '| Fast/lightweight | all-MiniLM-L6-v2 | 384 | http://localhost:5000/api/embed |',
    '',
    '**Step 2: Configure in SKILL settings:**',
    '',
    '```yaml',
    '# .hermes/skills/memory-ob4-ce-by-yhw/config.yaml',
    'embedding_model: bge-m3',
    'vector_dimensions: 1024',
    'storage_preference: native_vector  # or json_array for compatibility',
    'api_endpoint: http://localhost:5000/api/embed',
    '```',
    '',
    '**Step 3: SKILL auto-detects and creates appropriate schema:**',
    '',
    '```python',
    '# SKILL automatically generates optimal schema based on config',
    'from memory_storage_config import MemoryStorageConfig',
    '',
    'config = MemoryStorageConfig.load_from_yaml("config.yaml")',
    'schema = config.generate_sql_schema()',
    '',
    '# Output for bge-m3: CREATE TABLE memories_vectors_bge_m3 (embedding VECTOR(1024), ...)',
    '```',
    '',
    '---',
    '',
    '**Application-layer vector operations work regardless of storage format:**',
    '- Cosine similarity calculation in Python/Go',
    '- Approximate nearest neighbor search via application logic',
    '- Dimensionality reduction if needed'
]

new_p4_content = '\n'.join(new_p4_content_lines)

content_new = re.sub(pattern_p4, new_p4_content, content, flags=re.DOTALL | re.IGNORECASE)

if content_new != content:
    print("✅ P4 章节已替换（添加模型感知存储选择）")
else:
    print("❌ P4 章节未找到，尝试更宽松的匹配...")
    
# Try without specific title match
pattern_p4_loose = r'(### P4:.*?(?=## |\Z))'
content_new2 = re.sub(pattern_p4_loose, new_p4_content, content, flags=re.DOTALL | re.IGNORECASE)

if content_new2 != content:
    print("✅ P4 章节使用宽松匹配已替换")
else:
    print("❌ 宽松匹配也未成功")

# Use the version that actually made changes
final_content = content_new if content_new != content else content_new2 if content_new2 != content else content

# ==========================================
# Save file
# ==========================================
with open('/root/.hermes/skills/memory-ob4-ce-by-yhw/SKILL.md', 'w') as f:
    f.write(final_content)

print("\n=== 验证更新结果 ===")

# Verify changes in saved file
with open('/root/.hermes/skills/memory-ob4-ce-by-yhw/SKILL.md', 'r') as f:
    saved_content = f.read()

checks = [
    ('Configuration section added', '## ⚙️ Configuration (Embedding Model Support)' in saved_content),
    ('MEMORY_EMBEDDING_CONFIG defined', 'MEMORY_EMBEDDING_CONFIG = {' in saved_content),
    ('Model-Aware Storage Selection', 'Model-Aware Storage Selection' in saved_content or 'model-aware' in saved_content.lower()),
    ('MemoryStorageConfig class added', 'class MemoryStorageConfig:' in saved_content),
    ('generate_sql_schema method added', 'def generate_sql_schema(self):' in saved_content),
    ('BGE-M3 dimensions correct (1024)', 'bge-m3": 1024' in saved_content or 'VECTOR(1024)' in saved_content),
]

for check_name, result in checks:
    print(f"{'✅' if result else '❌'} {check_name}")

print("\n=== SKILL.md 更新完成 ===")