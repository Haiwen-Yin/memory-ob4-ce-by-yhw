-- ============================================================
-- OceanBase CE Knowledge Base System Schema v1.0.0
-- Author: yhw (胖头鱼 🐟)
-- Database: OceanBase CE v4.5.0
-- Compatible with: oracle-memory-by-yhw v1.0.0
-- ============================================================

-- ============================================================
-- 1. KNOWLEDGE_CONCEPTS - Stable Knowledge Concepts
-- ============================================================
CREATE TABLE IF NOT EXISTS KNOWLEDGE_CONCEPTS (
    CONCEPT_ID          BIGINT AUTO_INCREMENT PRIMARY KEY,
    CONCEPT_NAME        VARCHAR(255) NOT NULL,
    CONCEPT_TYPE        VARCHAR(50) NOT NULL,
    CATEGORY            VARCHAR(100),
    TITLE               VARCHAR(255),
    DESCRIPTION         TEXT,
    CONTENT             TEXT,
    SOURCE_TYPE          VARCHAR(50),
    SOURCE_MEMORY_IDS    TEXT,
    CONFIDENCE          DECIMAL(3,2) DEFAULT 0.80,
    VALIDATION_STATUS    VARCHAR(30) DEFAULT 'PENDING',
    EMBEDDING          TEXT
) ENGINE=InnoDB;

-- ============================================================
-- 2. KNOWLEDGE_GRAPH - Knowledge Graph Relationships
-- ============================================================
CREATE TABLE IF NOT EXISTS KNOWLEDGE_GRAPH (
    RELATIONSHIP_ID     BIGINT AUTO_INCREMENT PRIMARY KEY,
    SOURCE_CONCEPT_ID   BIGINT NOT NULL,
    TARGET_CONCEPT_ID   BIGINT NOT NULL,
    RELATIONSHIP_TYPE   VARCHAR(50) NOT NULL,
    RELATIONSHIP_STRENGTH DECIMAL(3,2) DEFAULT 0.90,
    PROPERTIES          TEXT,
    SOURCE_TYPE         VARCHAR(50),
    CONFIDENCE          DECIMAL(3,2) DEFAULT 0.80,
    CREATED_AT          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UPDATED_AT          TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (SOURCE_CONCEPT_ID) REFERENCES KNOWLEDGE_CONCEPTS(CONCEPT_ID) ON DELETE CASCADE,
    FOREIGN KEY (TARGET_CONCEPT_ID) REFERENCES KNOWLEDGE_CONCEPTS(CONCEPT_ID) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- 3. KNOWLEDGE_VERSIONS - Concept Version History
-- ============================================================
CREATE TABLE IF NOT EXISTS KNOWLEDGE_VERSIONS (
    VERSION_ID          BIGINT AUTO_INCREMENT PRIMARY KEY,
    CONCEPT_ID          BIGINT NOT NULL,
    VERSION_NUMBER      INT NOT NULL,
    CONTENT             TEXT NOT NULL,
    CHANGE_SUMMARY      TEXT,
    CREATED_BY          VARCHAR(100),
    CREATED_AT          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY (CONCEPT_ID, VERSION_NUMBER),
    FOREIGN KEY (CONCEPT_ID) REFERENCES KNOWLEDGE_CONCEPTS(CONCEPT_ID) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- 4. KNOWLEDGE_TAGS - Concept Tags
-- ============================================================
CREATE TABLE IF NOT EXISTS KNOWLEDGE_TAGS (
    TAG_ID              BIGINT AUTO_INCREMENT PRIMARY KEY,
    CONCEPT_ID          BIGINT NOT NULL,
    TAG_NAME            VARCHAR(100) NOT NULL,
    TAG_VALUE           VARCHAR(255),
    CREATED_AT          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (CONCEPT_ID) REFERENCES KNOWLEDGE_CONCEPTS(CONCEPT_ID) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- 5. KNOWLEDGE_VALIDATION - Validation Queue
-- ============================================================
CREATE TABLE IF NOT EXISTS KNOWLEDGE_VALIDATION (
    VALIDATION_ID       BIGINT AUTO_INCREMENT PRIMARY KEY,
    CONCEPT_ID          BIGINT NOT NULL,
    VALIDATION_TYPE     VARCHAR(50),
    STATUS              VARCHAR(30) DEFAULT 'PENDING',
    VALIDATOR           VARCHAR(100),
    COMMENTS            TEXT,
    VALIDATED_AT        TIMESTAMP,
    CREATED_AT          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (CONCEPT_ID) REFERENCES KNOWLEDGE_CONCEPTS(CONCEPT_ID) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- 6. KNOWLEDGE_CITATIONS - Cross-References
-- ============================================================
CREATE TABLE IF NOT EXISTS KNOWLEDGE_CITATIONS (
    CITATION_ID         BIGINT AUTO_INCREMENT PRIMARY KEY,
    SOURCE_CONCEPT_ID   BIGINT NOT NULL,
    TARGET_CONCEPT_ID   BIGINT NOT NULL,
    CITATION_TYPE       VARCHAR(50),
    CONTEXT             TEXT,
    CREATED_AT          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (SOURCE_CONCEPT_ID) REFERENCES KNOWLEDGE_CONCEPTS(CONCEPT_ID) ON DELETE CASCADE,
    FOREIGN KEY (TARGET_CONCEPT_ID) REFERENCES KNOWLEDGE_CONCEPTS(CONCEPT_ID) ON DELETE CASCADE

) ENGINE=InnoDB;

-- ============================================================
-- 7. KNOWLEDGE_AUDIT_LOG - Audit Trail
-- ============================================================
CREATE TABLE IF NOT EXISTS KNOWLEDGE_AUDIT_LOG (
    LOG_ID              BIGINT AUTO_INCREMENT PRIMARY KEY,
    CONCEPT_ID          BIGINT,
    OPERATION           VARCHAR(50),
    OPERATION_TYPE      VARCHAR(50),
    DETAILS             TEXT,
    PERFORMED_BY        VARCHAR(100),
    CREATED_AT          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ============================================================
-- Indexes for Performance
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_concepts_type ON KNOWLEDGE_CONCEPTS(CONCEPT_TYPE);
CREATE INDEX IF NOT EXISTS idx_concepts_category ON KNOWLEDGE_CONCEPTS(CATEGORY);
CREATE INDEX IF NOT EXISTS idx_concepts_status ON KNOWLEDGE_CONCEPTS(VALIDATION_STATUS);
CREATE INDEX IF NOT EXISTS idx_concepts_confidence ON KNOWLEDGE_CONCEPTS(CONFIDENCE);

CREATE INDEX IF NOT EXISTS idx_graph_source ON KNOWLEDGE_GRAPH(SOURCE_CONCEPT_ID);
CREATE INDEX IF NOT EXISTS idx_graph_target ON KNOWLEDGE_GRAPH(TARGET_CONCEPT_ID);
CREATE INDEX IF NOT EXISTS idx_graph_type ON KNOWLEDGE_GRAPH(RELATIONSHIP_TYPE);
CREATE INDEX IF NOT EXISTS idx_graph_strength ON KNOWLEDGE_GRAPH(RELATIONSHIP_STRENGTH);

CREATE INDEX IF NOT EXISTS idx_tags_concept ON KNOWLEDGE_TAGS(CONCEPT_ID);
CREATE INDEX IF NOT EXISTS idx_tags_name ON KNOWLEDGE_TAGS(TAG_NAME);

CREATE INDEX IF NOT EXISTS idx_citations_source ON KNOWLEDGE_CITATIONS(SOURCE_CONCEPT_ID);
CREATE INDEX IF NOT EXISTS idx_citations_target ON KNOWLEDGE_CITATIONS(TARGET_CONCEPT_ID);

CREATE INDEX IF NOT EXISTS idx_audit_concept ON KNOWLEDGE_AUDIT_LOG(CONCEPT_ID);
CREATE INDEX IF NOT EXISTS idx_audit_operation ON KNOWLEDGE_AUDIT_LOG(OPERATION);
CREATE INDEX IF NOT EXISTS idx_audit_created ON KNOWLEDGE_AUDIT_LOG(CREATED_AT);

-- ============================================================
-- Views for Common Queries
-- ============================================================

-- Active concepts (validated)
CREATE OR REPLACE VIEW ACTIVE_KNOWLEDGE_CONCEPTS_V AS
SELECT * FROM KNOWLEDGE_CONCEPTS 
WHERE VALIDATION_STATUS = 'VALIDATED';

-- Knowledge graph with concept names
CREATE OR REPLACE VIEW KNOWLEDGE_GRAPH_NAMES_V AS
SELECT 
    g.RELATIONSHIP_ID,
    g.SOURCE_CONCEPT_ID,
    s.CONCEPT_NAME AS SOURCE_CONCEPT_NAME,
    g.TARGET_CONCEPT_ID,
    t.CONCEPT_NAME AS TARGET_CONCEPT_NAME,
    g.RELATIONSHIP_TYPE,
    g.RELATIONSHIP_STRENGTH,
    g.CONFIDENCE,
    g.CREATED_AT
FROM KNOWLEDGE_GRAPH g
JOIN KNOWLEDGE_CONCEPTS s ON g.SOURCE_CONCEPT_ID = s.CONCEPT_ID
JOIN KNOWLEDGE_CONCEPTS t ON g.TARGET_CONCEPT_ID = t.CONCEPT_ID;

-- ============================================================
-- Summary
-- ============================================================
SELECT 'Knowledge Base Schema v1.0.0 deployed successfully' AS STATUS,
       (SELECT COUNT(*) FROM KNOWLEDGE_CONCEPTS) AS concept_count,
       (SELECT COUNT(*) FROM KNOWLEDGE_GRAPH) AS relationship_count;
