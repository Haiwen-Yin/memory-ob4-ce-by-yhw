# memory-ob4-ce-by-yhw — OceanBase CE v4.5+ AI Agent Memory System

**Version**: v1.0.0 (Knowledge Base System Production Release)  
**Created**: 2026-05-10  
**Updated**: 2026-05-11  
**Author**: Haiwen Yin (胖头鱼 🐟 / yhw)  
**License**: Apache License, Version 2.0

---

## Overview

A universal memory system for AI Agents built on **OceanBase Community Edition v4.5+**, featuring complete Knowledge Base system with native vector search capabilities and knowledge graph management.

### Key Features (v1.0.0)

#### Knowledge Base System
- **Knowledge Concepts** - Stable knowledge entities (FACT/RULE/PATTERN/EXPERIENCE/PRINCIPLE)
- **Knowledge Graph** - Property graph-based relationship management (IS_A/PART_OF/CAUSES/ENABLES/CONTRADICTS/SUPPORTS)
- **Version Control** - Complete version history for knowledge concepts
- **Validation Workflow** - Knowledge validation and approval process
- **Audit Trail** - Complete audit logging for all operations
- **Citation Tracking** - Knowledge concept citation relationships

#### Hybrid Search
- **Text Search** - Keyword-based full-text search
- **Semantic Search** - Vector similarity-based semantic search (application-layer implementation)
- **Graph Traversal** - Knowledge graph relationship queries

---

## Quick Start

### Prerequisites

- **Database**: OceanBase Community Edition 4.5+
- **Python**: 3.8+ with `pymysql` and `numpy` libraries
- **Network**: Access to OceanBase server (port 2881 by default)

### Install Dependencies

```bash
pip install pymysql numpy requests
```

### Deploy Schema

```bash
# Create database
mysql -h10.10.10.132 -P2881 -uroot@memory -e "CREATE DATABASE IF NOT EXISTS memory;"

# Deploy Knowledge Base Schema
mysql -h10.10.10.132 -P2881 -uroot@memory -D memory < scripts/knowledge_base_schema_ob.sql

# Verify deployment
mysql -h10.10.10.132 -P2881 -uroot@memory -D memory -e "SHOW TABLES LIKE 'knowledge%';"
```

### Run Tests

```bash
python3 scripts/test_ob4_v1.0.0_complete.py
```

---

## Usage Examples

### Knowledge Base Operations

```python
from scripts.knowledge_base_api_ob import KnowledgeBaseAPI

# Initialize API
kb = KnowledgeBaseAPI()

# Create a knowledge concept
concept = kb.create_concept(
    concept_name="OceanBase CE 4.5.0",
    concept_type="FACT",
    description="OceanBase Community Edition v4.5.0 with native vector search",
    category="database",
    confidence=0.95,
    tags=["oceanbase", "vector", "database"],
    metadata={"version": "4.5.0", "license": "Apache 2.0"}
)
print(f"Created concept: {concept}")

# Create a relationship
relationship = kb.create_relationship(
    source_concept_id=concept['concept_id'],
    target_concept_id=other_concept_id,
    relationship_type="SUPPORTS",
    strength=0.90,
    confidence=0.85
)

# Text search
results = kb.search_by_text(keyword="OceanBase", limit=10)

# Semantic search
similar_concepts = kb.search_similar_concepts(
    query_text="OceanBase vector database",
    limit=5,
    threshold=0.75
)

# Get concept with graph
concept_with_graph = kb.get_concept_with_graph(concept_id=concept['concept_id'])

# Get statistics
stats = kb.get_statistics()
print(f"Total concepts: {stats['total_concepts']}")
print(f"Total relationships: {stats['total_relationships']}")
```

---

## Architecture

### Knowledge Base System

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer (Python/Java)          │
│  Embedding Generation → Text Vector Conversion              │
│  SQL Query Building with cosine_similarity()                │
├─────────────────────────────────────────────────────────────┤
│                    OceanBase Cluster (v4.5+)                │
│                                                             │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐               │
│  │ OBServer │◄──►│ Rootsrv  │◄──►│ OBServer │               │
│  │(SQL/Calc)│    │(Metadata)│    │(Storage) │               │
│  └──────────┘    └──────────┘    └──────────┘               │
│                                                             │
│  Table Engine (Partitioned Storage)                         │
│  - Accelerates Analytical Queries                           │
└─────────────────────────────────────────────────────────────┘
```

---

## Testing Status

### v1.0.0 Complete Test Suite (9 Tests)

| Test | Status | Description |
|------|--------|-------------|
| Database Connection | ✅ Pass | OceanBase CE v4.5.0 (10.10.10.132:2881) |
| Create Knowledge Concepts | ✅ Pass | Created 4 test concepts with tags and embeddings |
| Update Knowledge Concept | ✅ Pass | Updated concept description and confidence |
| Create Knowledge Relationships | ✅ Pass | Created 3 test relationships |
| Text Search | ✅ Pass | Keyword search working (4 results found) |
| Semantic Search | ✅ Pass | Application-layer semantic search working (2 similar concepts found) |
| Get Concept with Graph | ✅ Pass | Graph relationship queries working |
| Get Statistics | ✅ Pass | Knowledge base statistics working |
| Delete Knowledge Concept | ✅ Pass | Cascading delete working |

**Total**: 9/9 Pass (100%)

### Test Environment

- **OceanBase Version**: v4.5.0.0
- **Host**: 10.10.10.132:2881 (cluster: memorycluster, tenant: memory)
- **Database**: memory
- **User**: root@memory
- **Test Time**: 2026-05-11 (CST)

---

## Directory Structure

```
memory-ob4-ce-by-yhw/
├── SKILL.md              # Complete skill documentation
├── README.md             # Project overview and quick start guide
├── LICENSE               # Apache License 2.0
├── NOTICE                # Copyright notice for Haiwen Yin/yhw
├── CHANGELOG.md          # Version history
├── VERSION               # Current version string
├── scripts/              # Helper scripts
│   ├── knowledge_base_schema_ob.sql   # Knowledge Base Schema (v1.0.0)
│   ├── knowledge_base_api_ob.py       # Knowledge Base Python API (v1.0.0)
│   └── ...                       # Additional utilities
├── references/           # External documentation references
└── test_ob4_v1.0.0_complete.py  # Complete test suite
```

---

## Related Documentation

- [OceanBase CE Download](https://www.oceanbase.com/download/community) — Community Edition download links
- [OceanBase Documentation](https://www.oceanbase.com/docs/) — Official documentation entry point
- [oracle-memory-by-yhw v1.0.0](../oracle-memory-by-yhw/) — Original version reference

---

## Author & Maintainer

**Haiwen Yin (胖头鱼 🐟)**  
Oracle/PostgreSQL/MySQL ACE Database Expert

- **Blog**: https://blog.csdn.net/yhw1809
- **GitHub**: https://github.com/Haiwen-Yin

---

## License

This project is licensed under [Apache License, Version 2.0](LICENSE).

---

**Last Updated**: 2026-05-11 v1.0.0 (Knowledge Base System Production Release)
