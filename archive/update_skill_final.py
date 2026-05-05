"""
更新 SKILL.md - 添加可配置的 embedding 模型支持
==================================================
从文件读取新内容并替换到 SKILL.md
"""

import re
import os

skill_md_path = '/root/.hermes/skills/memory-ob4-ce-by-yhw/SKILL.md'
config_section_file = '/root/.hermes/skills/memory-ob4-ce-by-yhw/config_section.txt'
p4_section_file = '/root/.hermes/skills/memory-ob4-ce-by-yhw/p4_section.txt'

# Read SKILL.md
with open(skill_md_path, 'r') as f:
    content = f.read()

print("=== 开始更新 SKILL.md - 添加可配置 embedding 模型支持 ===\n")

# ==========================================
# 1. 读取配置文件内容
# ==========================================
with open(config_section_file, 'r') as f:
    config_section = f.read().strip()

# Insert after "System Overview" section
insert_marker = '## ✨ Core Features (v0.1.1 - with Performance Optimizations)'
if insert_marker in content:
    idx = content.find(insert_marker)
    content = content[:idx] + '\n\n' + config_section + content[idx:]
    print("✅ Configuration section added")

# ==========================================
# 2. 读取 P4 章节内容并替换
# ==========================================
with open(p4_section_file, 'r') as f:
    new_p4_content = f.read().strip()

pattern_p4 = r'(### P4:.*?Dimensionality Reduction if Needed)(?=## |\Z)'

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
with open(skill_md_path, 'w') as f:
    f.write(final_content)

print("\n=== 验证更新结果 ===")

# Verify changes in saved file
with open(skill_md_path, 'r') as f:
    saved_content = f.read()

checks = [
    ('Configuration section added', '## Configuration (Embedding Model Support)' in saved_content),
    ('MEMORY_EMBEDDING_CONFIG defined', 'MEMORY_EMBEDDING_CONFIG = {' in saved_content),
    ('Model-Aware Storage Selection', 'Model-Aware Storage Selection' in saved_content or 'model-aware' in saved_content.lower()),
    ('MemoryStorageConfig class added', 'class MemoryStorageConfig:' in saved_content),
    ('generate_sql_schema method added', 'def generate_sql_schema(self):' in saved_content),
    ('BGE-M3 dimensions correct (1024)', 'bge-m3": 1024' in saved_content or 'VECTOR(1024)' in saved_content),
]

for check_name, result in checks:
    print(f"{'✅' if result else '❌'} {check_name}")

print("\n=== SKILL.md 更新完成 ===")