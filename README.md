# OceanBase CE 4.x Memory System v0.1.1 (Task Plan Support)

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

## 📋 Environment

This system has been **validated on OceanBase CE 4.x standalone/deployment**.

## Requirements

- **Database**: OceanBase Community Edition (CE) 4.5.0 or later
- **Python**: 3.8+ with `pymysql` library
- **Network**: Access to OceanBase server (port 2881 by default)

## Overview

A universal memory system for AI Agents built on **OceanBase Community Edition 4.x**, providing:

- ✅ Semantic search via application-layer vector similarity
- ✅ Knowledge graph relationship management via recursive CTEs
- ✅ Vector similarity retrieval (application-layer cosine calculation)
- ✅ Full-text search capabilities (version-dependent)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer (Python/Java)          │
│  Embedding Generation → Text Vector Conversion              │
│  Cosine Similarity Calculation                              │
│  Graph Traversal via Recursive CTEs                         │
│  JSON View Construction                                     │
├─────────────────────────────────────────────────────────────┤
│                    OceanBase CE 4.x Database Layer          │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Deploy OceanBase CE 4.x (Required)

Download and deploy OceanBase Community Edition 4.x:
- [OceanBase CE Download](https://www.oceanbase.com/softwarecenter)
- Minimum version: **4.2.x** recommended for JSON support

### 2. Install Prerequisites

```bash
# Java Runtime (Optional but Recommended)
sudo apt install openjdk-17-jdk

# Python 3.9+ with dependencies
pip3 install numpy requests
```

### 3. Apply Schema

Use the DDL statements from SKILL.md to create all tables and indexes.

## Features

- **Vector Similarity Search**: Application-layer cosine similarity calculation for semantic search
- **Knowledge Graph Management**: Property graph relationships via recursive CTEs and JSON
- **Full-text Search**: Version-dependent text indexing capabilities  
- **Task Plan System**: Persistent task execution with state management and snapshots
- **Property Graph Queries**: Node-edge relationship traversal using SQL

---

## Installation

### Prerequisites

| Component | Requirement | Notes |
|-----------|-------------|-------|
| Database | OceanBase CE 4.5.0+ | Single-node deployment tested |
| Python | 3.8+ | With pymysql, numpy packages |
| Network | Port 2881 accessible | Default OB port |

### Quick Start

```bash
# Clone or copy skill files to your workspace
cp -r memory-ob4-ce-by-yhw/ ~/.hermes/skills/

# Install Python dependencies
pip install pymysql numpy

# Configure environment variables
export OB_HOST=10.10.10.132
export OB_USER=root@memory  
export OB_PASS=your_password

## Connecting to Tenant Database

OceanBase uses a multi-tenant architecture. Connect to the **tenant database** (not the SYS tenant):

```bash
# Using OceanBase CLI (obclient)
obclient -h 10.10.10.132 -P 2881 -u root@memory -p memory

# Or using Python with pymysql
python3 -c "import pymysql; conn = pymysql.connect(host='10.10.10.132', port=2881, user='root@memory', password='your_password', database='memory')"
```

**Connection Parameters:**
| Parameter | Value | Description |
|-----------|-------|-------------|
| Host | 10.10.10.132 | OB server IP |
| Port | 2881 | Default OB port |
| User | root@memory | Format: `username@tenant` |
| Database | memory | Tenant name (database) |

**Alternative: Direct tenant connection string**
```bash
# Format: mysql://user@tenant:password@host:port/database
mysql -u root@memory -p -h 10.10.10.132 -P 2881 memory
```

---

## Usage

### Vector Similarity Search

```python
from scripts.vector_similarity import (
    cosine_similarity,
    find_similar_nodes,
    embedding_to_text
)

# Calculate cosine similarity between two vectors
vec_a = [0.1, 0.2, 0.3]
vec_b = [0.15, 0.25, 0.35]
similarity = cosine_similarity(vec_a, vec_b)

# Find similar nodes in database
similar_nodes = find_similar_nodes(
    query_vector=your_embedding,
    limit=10
)
```

### Task Plan Management

```python
from scripts.task_plan_api import (
    create_task_plan,
    resume_task,
    search_completed_tasks
)

# Create a new task plan
plan_id = create_task_plan(
    plan_name="my_task",
    plan_type="task",
    description="Task description"
)

# Resume an existing task
result = resume_task(plan_id)

# Search completed tasks
tasks = search_completed_tasks({
    "status": "completed",
    "type": "task"
})
```

### Schema Management

```python
from scripts.schema_loader import (
    apply_schema,
    check_schema_exists
)

# Check if schema exists
exists = check_schema_exists()

# Apply or update schema
apply_schema(dry_run=False)
```

## Directory Structure

```
memory-ob4-ce-by-yhw/
├── SKILL.md              # Complete skill documentation
├── README.md             # This file - project overview
├── LICENSE               # Apache License 2.0
├── NOTICE                # Copyright notice
├── CHANGELOG.md          # Version history
├── scripts/              # Helper scripts
├── references/           # External references
└── *.md                  # Test reports, etc.
```

## Related Documentation

- [OceanBase CE Download](https://www.oceanbase.com/softwarecenter) — Community edition downloads
- [OceanBase Documentation](https://www.oceanbase.com/docs) — Official documentation

## Author & Maintainer

**Haiwen Yin (胖头鱼 🐟)**  
Oracle/PostgreSQL/MySQL ACE Database Expert

- **Blog**: https://blog.csdn.net/yhw1809
- **GitHub**: https://github.com/Haiwen-Yin

## License

This project is licensed under the [Apache License, Version 2.0](LICENSE).

---

**Last Updated**: 2026-05-01 v0.1.0 (Preliminary Research)