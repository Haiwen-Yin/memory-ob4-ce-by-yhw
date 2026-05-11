# OceanBase CE Deployment Pitfalls - Session Learnings

**Date**: 2026-05-11  
**OceanBase CE Version**: v4.5.0.0  
**Client**: MySQL 5.7.25

---

## Critical Syntax Differences

### 1. ROW_FORMAT Syntax Error

**Problem**: OceanBase CE rejects `ROW_FORMAT=DYNAMIC, ENGINE=InnoDB` in table definition.

**Error**:
```
ERROR 1064 (42000): You have an error in your SQL syntax; check the manual
near ') ROW_FORMAT=DYNAMIC, ENGINE=InnoDB' at line 14
```

**Root Cause**: Incorrect separator between table options.

**Solution**: Remove comma before ENGINE clause or use only ENGINE:
```sql
-- ❌ BAD
CREATE TABLE KNOWLEDGE_CONCEPTS (
    CONCEPT_ID BIGINT AUTO_INCREMENT PRIMARY KEY,
    CONCEPT_NAME VARCHAR(255) NOT NULL
) ROW_FORMAT=DYNAMIC, ENGINE=InnoDB;

-- ✅ GOOD - Option 1: Remove comma
CREATE TABLE KNOWLEDGE_CONCEPTS (
    CONCEPT_ID BIGINT AUTO_INCREMENT PRIMARY KEY,
    CONCEPT_NAME VARCHAR(255) NOT NULL
) ENGINE=InnoDB;

-- ✅ GOOD - Option 2: Use semicolon (if supported)
CREATE TABLE KNOWLEDGE_CONCEPTS (
    CONCEPT_ID BIGINT AUTO_INCREMENT PRIMARY KEY,
    CONCEPT_NAME VARCHAR(255) NOT NULL
) ROW_FORMAT=DYNAMIC; ENGINE=InnoDB;
```

---

### 2. FOREIGN KEY Inline Syntax

**Problem**: Cannot use `REFERENCES` clause inline with column definition in OceanBase CE.

**Error**:
```
ERROR 1064 (42000): You have an error in your SQL syntax; check the manual
near 'REFERENCES KNOWLEDGE_CONCEPTS(CONCEPT_ID) ON DELETE CASCADE'
```

**Root Cause**: FOREIGN KEY constraints must be defined after column definitions.

**Solution**: Define FOREIGN KEY as table constraint:
```sql
-- ❌ BAD
CREATE TABLE KNOWLEDGE_GRAPH (
    RELATIONSHIP_ID BIGINT AUTO_INCREMENT PRIMARY KEY,
    SOURCE_CONCEPT_ID BIGINT NOT NULL REFERENCES KNOWLEDGE_CONCEPTS(CONCEPT_ID) ON DELETE CASCADE
);

-- ✅ GOOD
CREATE TABLE KNOWLEDGE_GRAPH (
    RELATIONSHIP_ID BIGINT AUTO_INCREMENT PRIMARY KEY,
    SOURCE_CONCEPT_ID BIGINT NOT NULL,
    FOREIGN KEY (SOURCE_CONCEPT_ID) REFERENCES KNOWLEDGE_CONCEPTS(CONCEPT_ID) ON DELETE CASCADE
) ENGINE=InnoDB;
```

---

### 3. MySQL Client Warnings

**Problem**: MySQL client always returns password warning on command line.

**Output**:
```
mysql: [Warning] Using a password on the command line interface can be insecure.
```

**Impact**: Warnings clutter automated parsing and pipeline output.

**Solution**: Filter warnings with grep:
```bash
# ❌ Output includes warning
mysql -hhost -Pport -uuser -ppassword -e "SELECT NOW();"

# ✅ Clean output
mysql -hhost -Pport -uuser -ppassword -e "SELECT NOW();" 2>&1 | grep -v Warning
```

---

## Connection String Format

### OceanBase CE Multi-Tenant Architecture

**Problem**: OceanBase CE requires `user@tenant` format for connections.

**Incorrect**:
```
-u root  -- Will fail with authentication error
```

**Correct**:
```
-u root@memory  -- Specifies user 'root' in tenant 'memory'
```

**Port Difference**:
- MySQL default: 3306
- OceanBase CE SQL proxy: 2881

**Example**:
```bash
mysql -h10.10.10.132 -P2881 -uroot@memory -pOceanBase#123 -D memory
```

---

## Data Type Mappings

| Oracle Type | OceanBase CE Type | Notes |
|-------------|------------------|--------|
| `NUMBER` | `BIGINT` or `DECIMAL(x,y)` | Use DECIMAL for fixed-point |
| `VARCHAR2` | `VARCHAR` | No VARCHAR2 in MySQL/OB |
| `CLOB` | `TEXT` | TEXT for large strings |
| `DATE` | `DATE` or `DATETIME` | Similar semantics |
| `TIMESTAMP WITH TIME ZONE` | `TIMESTAMP` | Time zone in application layer |
| `SEQUENCE.NEXTVAL` | `AUTO_INCREMENT` | Table-level auto-increment |

---

## Version Detection

**Verified Version String**:
```
5.7.25-OceanBase_CE-v4.5.0.0
```

**Detection Query**:
```sql
SELECT VERSION();
```

**Expected Output Format**: `X.Y.Z-OceanBase_CE-vX.Y.Z.W`

---

## Feature Availability

### JSON Support

**Test**:
```sql
SELECT JSON_OBJECT('key', 'value');
```

**Expected**: JSON object output

### Recursive CTE Support

**Test**:
```sql
WITH RECURSIVE t AS (
    SELECT 1 n 
    UNION ALL 
    SELECT n+1 FROM t WHERE n<3
) 
SELECT * FROM t;
```

**Expected**: Returns 3 rows (1, 2, 3)

### VECTOR Type Support (v4.5.0+)

**Test**:
```sql
CREATE TABLE IF NOT EXISTS test_vector (
    id INT PRIMARY KEY,
    embedding VECTOR(1024)
) ENGINE=InnoDB;
```

**Expected**: Table created successfully

---

## Common Error Messages

### ER_PARSE_ERROR (1064)

**Pattern**: `ERROR 1064 (42000): You have an error in your SQL syntax`

**Common Causes**:
1. Reserved word used as identifier (e.g., `order`, `group`)
2. Missing comma between columns
3. Incorrect function syntax
4. Invalid data type

**Solution**: Check SQL syntax against MySQL 5.7 documentation (OceanBase CE compatible)

### ER_BAD_FIELD_ERROR (1054)

**Pattern**: `ERROR 1054 (42S22): Unknown column`

**Common Causes**:
1. Column name typo
2. Column not created in schema
3. Table or column name mismatch between Schema and API

**Solution**: Always verify actual schema with `DESCRIBE table_name` before writing queries

---

## Best Practices

### 1. Schema Verification Before Deployment

Always verify actual deployed schema before writing application code:

```bash
# Check table exists and has correct columns
mysql -hhost -Pport -uuser@tenant -ppassword -e "DESCRIBE KNOWLEDGE_CONCEPTS;"
```

### 2. Test SQL Before Integration

Test each DDL statement individually:

```bash
# Test table creation
mysql -hhost -Pport -uuser@tenant -ppassword -D database -e "
CREATE TABLE test_table (id INT PRIMARY KEY) ENGINE=InnoDB;
"

# Clean up
mysql -hhost -Pport -uuser@tenant -ppassword -D database -e "
DROP TABLE IF EXISTS test_table;
"
```

### 3. Use Transactions for Schema Changes

```sql
BEGIN;
-- Multiple DDL statements
CREATE TABLE ...;
CREATE INDEX ...;
COMMIT;
```

### 4. Handle Index Creation Failures Gracefully

OceanBase CE may not support `CREATE INDEX IF NOT EXISTS`:

```sql
-- Check if index exists first
SELECT COUNT(*) FROM information_schema.statistics 
WHERE table_name = 'KNOWLEDGE_CONCEPTS' 
  AND index_name = 'idx_concepts_type';
```

---

## Reference Implementations

### Knowledge Base Schema (Working Example)

```sql
-- 1. Main table
CREATE TABLE IF NOT EXISTS KNOWLEDGE_CONCEPTS (
    CONCEPT_ID BIGINT AUTO_INCREMENT PRIMARY KEY,
    CONCEPT_NAME VARCHAR(255) NOT NULL,
    CONCEPT_TYPE VARCHAR(50) NOT NULL,
    EMBEDDING TEXT
) ENGINE=InnoDB;

-- 2. Related table with foreign key
CREATE TABLE IF NOT EXISTS KNOWLEDGE_GRAPH (
    RELATIONSHIP_ID BIGINT AUTO_INCREMENT PRIMARY KEY,
    SOURCE_CONCEPT_ID BIGINT NOT NULL,
    TARGET_CONCEPT_ID BIGINT NOT NULL,
    RELATIONSHIP_TYPE VARCHAR(50) NOT NULL,
    FOREIGN KEY (SOURCE_CONCEPT_ID) REFERENCES KNOWLEDGE_CONCEPTS(CONCEPT_ID) ON DELETE CASCADE,
    FOREIGN KEY (TARGET_CONCEPT_ID) REFERENCES KNOWLEDGE_CONCEPTS(CONCEPT_ID) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 3. Create index separately
CREATE INDEX IF NOT EXISTS idx_graph_type ON KNOWLEDGE_GRAPH(RELATIONSHIP_TYPE);
```

---

**Last Updated**: 2026-05-11  
**OceanBase CE Version**: v4.5.0.0
