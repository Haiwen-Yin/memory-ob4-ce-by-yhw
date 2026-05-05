# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of OceanBase CE 4.x Memory System for AI Agents
- Core schema design (memory_nodes, memory_edges, memories tables)
- Decomposition relationship tables for JSON-like structure storage
- SQL view patterns for JSON output via JSON_OBJECT/JSON_ARRAYAGG
- Recursive CTE graph traversal implementation
- Application-layer vector similarity calculation framework using Python/NumPy
- Full-text search support (version-dependent on OceanBase CE build)
- Comprehensive deployment checklist and pre-flight verification procedures

### Architecture
- Property Graph management via recursive CTEs for relationship navigation
- Vector similarity retrieval through application-layer cosine calculation
- Structured JSON views for API-friendly data consumption
- Memory decomposition tables replacing Oracle AI DB native features

## [0.1.1] - 2026-05-05 (Task Plan Support)

### Added
- **Task Plan System** — Complete task management framework for AI Agents
  - `task_plans` table with status tracking (PENDING/RUNNING/SUCCESS/FAILED/CANCELLED/PAUSED)
  - `task_steps` table for step-by-step execution tracking
  - `task_context_snapshots` table for breakpoint recovery after failures
  - `task_tool_calls` audit trail table for all tool executions
  - `task_dependencies` table with HARD/SOFT/EXCLUSIVE dependency types
- **Task Plan Python API** (`scripts/task_plan_api.py`) — High-level interface:
  - `create_task_plan()` — Create task with goal, steps, and metadata
  - `resume_task()` — Restore execution from latest context snapshot
  - `search_completed_tasks()` — Search historical tasks for pattern learning
- **Task Plan SQL Schema** (`scripts/init_task_plan_system.sql`) — OceanBase CE compatible DDL

### Features
- **Breakpoint Recovery**: Automatic context snapshots enable resuming from any point after failure
- **Historical Learning**: Search completed tasks to reuse successful patterns across projects
- **Tool Call Auditing**: Full record of all tool executions with duration and result size tracking
- **Task Dependencies**: Define relationships between plans (HARD/SOFT/EXCLUSIVE/RECOMMENDED)

### Updated
- SKILL.md: Added Task Plan documentation and API usage examples
- All scripts updated to reference v0.1.1 versioning

## [0.1.0] - 2026-05-01 (PRELIMINARY RESEARCH VERSION)

⚠️ **IMPORTANT**: This is a preliminary research version — not fully tested or production-ready.

### Added
- Initial project structure and documentation
- Complete schema design with all core tables
- Architecture diagram and implementation patterns
- Python cosine similarity calculator for vector operations
- Graph traversal SQL templates using WITH RECURSIVE CTEs
- JSON view definitions for API consumption
- Indexing strategy recommendations
- Deployment checklist with verification steps

### Notes
- This version represents initial architectural exploration and design validation
- Not recommended for production use without thorough testing
- All DDL statements require validation on actual OceanBase CE deployment
- Vector search performance needs benchmarking
- Graph traversal scalability under heavy load untested

