# OceanBase CE 4.x Memory System v0.1.0

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

## ⚠️ PRELIMINARY RESEARCH VERSION

This is a **preliminary research version** — not fully tested or production-ready. Use at your own risk for research purposes only.

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
- [OceanBase CE Download](https://www.oceanbase.com/software-download/community)
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

| Feature | Status | Implementation |
|---------|--------|----------------|
| Memory Nodes | ✅ | TEXT column storage |
| Graph Edges | ✅ | Foreign key relationships |
| Vector Search | ⚠️ | Application-layer cosine similarity |
| Full-text Search | ❓ | Version-dependent (CE varies) |
| JSON Views | ✅ | SQL JSON_OBJECT/JSON_ARRAYAGG |
| Recursive CTEs | ✅ | Graph traversal patterns |

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

## Testing Status (v0.1.0)

| Component | Tested? | Notes |
|-----------|---------|-------|
| Schema DDL (nodes/edges/memories) | Partially | Syntax verified only |
| SQL JSON views | Partially | Basic query format checked |
| Recursive CTEs | No | Needs real data testing |
| Vector search (app-layer) | No | Requires OceanBase deployment |
| Full-text indexing | Version-dependent | CE support varies |

## Next Steps for v0.2.0

1. Deploy on standalone OceanBase CE instance and validate all DDL statements
2. Test vector similarity calculation with real embedding data
3. Benchmark graph traversal performance with realistic node/edge counts
4. Validate full-text search availability across supported CE versions
5. Add comprehensive SQL test cases for each major query pattern

## Related Documentation

- [OceanBase CE Download](https://www.oceanbase.com/software-download/community) — Community edition downloads
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