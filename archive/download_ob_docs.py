"""
下载并分析 OceanBase 向量操作快速入门文档
========================================
URL: https://www.oceanbase.com/docs/common-oceanbase-database-cn-1000000004475692
     https://www.oceanbase.com/docs/common-oceanbase-database-cn-1000000004475691
"""

import urllib.request
import json
import os

urls = [
    "https://www.oceanbase.com/docs/common-oceanbase-database-cn-1000000004475692",  # 向量操作快速入门
    "https://www.oceanbase.com/docs/common-oceanbase-database-cn-1000000004475691"   # 相关文档
]

output_dir = "/tmp/oceanbase_docs"
os.makedirs(output_dir, exist_ok=True)

print("=== 下载 OceanBase 向量操作文档 ===\n")

for i, url in enumerate(urls):
    output_file = os.path.join(output_dir, f"ob_vector_doc_{i+1}.md")
    
    try:
        print(f"正在获取: {url}")
        
        # Set user agent to avoid blocking
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (compatible; Agent/1.0)')
        
        response = urllib.request.urlopen(req, timeout=30)
        content = response.read().decode('utf-8', errors='ignore')
        
        # Save raw HTML/content
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content[:50000])  # Limit size
        
        print(f"✅ 已保存到 {output_file} ({len(content)} bytes)")
        
    except Exception as e:
        print(f"❌ 下载失败: {str(e)[:100]}")

print("\n=== 文档分析 ===\n")

for i in range(2):
    output_file = os.path.join(output_dir, f"ob_vector_doc_{i+1}.md")
    if os.path.exists(output_file):
        print(f"\n📄 文档 {i+1}: {output_file}")
        
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract key sections (first 2000 chars)
        preview = content[:3000]
        print(f"预览:\n{preview}\n")
        