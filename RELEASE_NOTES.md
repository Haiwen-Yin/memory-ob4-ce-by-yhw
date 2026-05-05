# Release Notes — OceanBase CE 4.x Memory System

## Version v0.1.1 (2026-05-05)
**Task Plan Support + Performance Optimizations**

---

### 🎉 New Features

#### Task Plan System
Complete task management framework for AI Agents with persistent state tracking:

| Component | Purpose |
|-----------|---------|
| `task_plans` table | Store task plans with status (PENDING/RUNNING/SUCCESS/FAILED/CANCELLED) |
| `task_steps` table | Track individual execution steps |
| `task_context_snapshots` table | Save state for breakpoint recovery after failures |
| `task_tool_calls` table | Audit trail of all tool executions |
| `task_dependencies` table | Define relationships between tasks (HARD/SOFT/EXCLUSIVE) |

#### Python API (`scripts/task_plan_api.py`)
- `create_task_plan()` — Create task with goal, steps, and metadata
- `resume_task()` — Restore execution from latest context snapshot
- `search_completed_tasks()` — Search historical tasks for pattern learning

#### SQL Schema (`scripts/init_task_plan_system.sql`)
OceanBase CE compatible DDL statements for task management tables.

---

### 🔧 Improvements

- **SKILL.md**: Added complete Task Plan documentation and API usage examples
- **All scripts**: Updated to reference v0.1.1 versioning consistently
- **README.md**: Added tenant database connection instructions
- **Documentation**: Updated OceanBase download URL to softwarecenter

---

### 📋 What's Included in This Release

| Category | Content |
|----------|---------|
| Core Schema | memory_nodes, memory_edges, memories tables with decomposition |
| SQL Views | JSON output via JSON_OBJECT/JSON_ARRAYAGG patterns |
| Graph Traversal | Recursive CTE implementation for relationship navigation |
| Vector Search | Application-layer cosine similarity calculation (Python/NumPy) |
| Task Management | Full task plan lifecycle with snapshot recovery |
| Documentation | SKILL.md, README.md, RELEASE_NOTES.md, CHANGELOG.md |
| Scripts | schema_loader.py, vector_similarity.py, task_plan_api.py |

---

### ⚠️ Known Limitations

- **Testing**: Validated on OceanBase CE 4.x standalone deployment only
- **Vector Search**: Requires application-layer calculation (no native index yet)
- **Full-text Search**: Availability depends on specific OceanBase CE build version
- **Cluster Support**: Not tested on distributed OceanBase cluster configuration

---

### 📦 Contents Overview

```
memory-ob4-ce-by-yhw/
├── SKILL.md                  # Complete skill documentation
├── README.md                 # Project overview and setup guide
├── RELEASE_NOTES.md          # This file — release highlights
├── CHANGELOG.md              # Detailed version history
├── LICENSE                   # Apache License 2.0
├── NOTICE                    # Copyright notice
├── scripts/                  # Helper scripts (Python + SQL)
│   ├── schema_loader.py      # Schema deployment automation
│   ├── vector_similarity.py  # Cosine similarity calculation
│   └── task_plan_api.py      # Task management API
├── references/               # External documentation links
└── archive/                  # Historical test scripts
```

---

### 🔗 Quick Links

- **Download**: [OceanBase CE Software Center](https://www.oceanbase.com/softwarecenter)
- **Documentation**: [OceanBase Official Docs](https://www.oceanbase.com/docs)
- **Author Blog**: https://blog.csdn.net/yhw1809

---

**License**: Apache License, Version 2.0
