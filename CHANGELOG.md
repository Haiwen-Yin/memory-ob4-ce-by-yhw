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

### Testing Status (v0.1.0)
- Schema DDL syntax verified on SQLcl
- Basic query format checked for SQL views
- Graph traversal patterns documented but not tested with real data
- Vector search requires OceanBase deployment for validation
- Full-text indexing support varies by OceanBase CE version

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

## Planned Changes (v0.2.0)

### To Be Implemented
1. Deploy on standalone OceanBase CE instance and validate all DDL statements
2. Test vector similarity calculation with real embedding data
3. Benchmark graph traversal performance with realistic node/edge counts
4. Validate full-text search availability across supported CE versions
5. Add comprehensive SQL test cases for each major query pattern
6. Create automated testing framework for CI/CD integration

### To Be Optimized
1. JSON view query optimization and profiling
2. Memory decomposition table indexing strategy validation
3. Application-layer vector storage format standardization
4. Graph traversal algorithm improvements for large datasets
5. Full-text search tokenization strategies for Chinese text