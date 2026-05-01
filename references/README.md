# References and External Resources

This directory contains external references and documentation for the OceanBase CE Memory System.

## OceanBase Documentation

- [OceanCE Community Edition Download](https://www.oceanbase.com/software-download/community)
  - Official download page for OceanBase Community Edition 4.x
  - Includes installation packages for Linux, macOS, and Windows
  
- [OceanBase Official Documentation](https://www.oceanbase.com/docs)
  - Complete API reference documentation
  - Installation guides for various deployment modes
  - Configuration recommendations for production environments

## Embedding Models

### BGE-M3 (Recommended for this project)
- **Dimensions**: 1024
- **Source**: [BAAI/bge-m3](https://huggingface.co/BAAI/bge-m3)
- **Features**: 
  - Multilingual support (Chinese, English, and 100+ languages)
  - High-quality dense embeddings for semantic search
  - Efficient for application-layer cosine similarity calculation

### Alternative Embedding Models
- OpenAI text-embedding-3-small: 1536 dimensions
- Sentence Transformers (all-MiniLM-L6-v2): 384 dimensions

## Vector Search Resources

- [Cosine Similarity](https://en.wikipedia.org/wiki/Cosine_similarity) - Mathematical foundation for vector comparison
- [Recursive CTEs in SQL](https://en.wikipedia.org/wiki/Hierarchical_and_recursive_queries_in_SQL) - Graph traversal patterns
- [JSON in Databases](https://www.oceanbase.com/docs/oceanbase-database-v4.x-concept-json-object-and-array-types-olb12a) - JSON support in OceanBase CE

## Testing Resources

- [OceanBase Client Tools](https://www.oceanbase.com/docs/oceanbase-database-v4.x-concept-obclient-utility-olb13s)
  - obclient command-line client for database interaction
  
- NumPy Documentation:
  - [numpy.linalg.norm](https://numpy.org/doc/stable/reference/generated/numpy.linalg.norm.html)
  - [numpy.dot](https://numpy.org/doc/stable/reference/generated/numpy.dot.html)

## Related Projects

- Hermes Agent Memory Systems (Oracle AI DB): For comparison and architectural reference
- Apache AGE Property Graph: Alternative graph database approach for PostgreSQL