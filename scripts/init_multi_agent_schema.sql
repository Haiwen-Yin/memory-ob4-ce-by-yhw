-- ============================================================
-- memory-ob4-ce-by-yhw v0.1.2 - Multi-Agent Architecture Schema
-- OceanBase CE 4.x Compatible (Fixed for v4.5.0)
-- ============================================================

-- Agent Registry Table - Centralized agent lifecycle management
CREATE TABLE IF NOT EXISTS agent_registry (
    id              BIGINT AUTO_INCREMENT PRIMARY KEY,
    agent_id        VARCHAR(64) UNIQUE NOT NULL,
    agent_name      VARCHAR(100) NOT NULL,
    agent_type      VARCHAR(50) DEFAULT 'general',  -- analytical, content, deployment, etc.
    capabilities    JSON,                            -- Agent capabilities as JSON object (JSON->JSON for OB compatibility)
    status          VARCHAR(20) DEFAULT 'INACTIVE', -- INACTIVE, ACTIVE, PAUSED, STOPPED
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP,
    last_heartbeat  TIMESTAMP,
    metadata        JSON
);

-- Agent Memory Access Control - Fine-grained visibility policies
CREATE TABLE IF NOT EXISTS agent_memory_access (
    id              BIGINT AUTO_INCREMENT PRIMARY KEY,
    agent_id        INTEGER, -- REFERENCES agent_registry(agent_id) ON DELETE CASCADE
    memory_scope    VARCHAR(20), -- PRIVATE, SHARED, COLLABORATIVE
    accessible_to   JSON,       -- Array of agent_ids that can access
    can_read        TINYINT DEFAULT 1,
    can_write       TINYINT DEFAULT 0,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP
);

-- Agent Collaboration - Inter-agent communication records
CREATE TABLE IF NOT EXISTS agent_collaboration (
    id              BIGINT AUTO_INCREMENT PRIMARY KEY,
    collab_id       VARCHAR(64) UNIQUE NOT NULL,
    source_agent_id INTEGER, -- REFERENCES agent_registry(agent_id) ON DELETE SET NULL
    target_agent_id INTEGER, -- REFERENCES agent_registry(agent_id) ON DELETE SET NULL
    collab_type     VARCHAR(30), -- REQUEST, RESPONSE, SHARING, QUERY
    status          VARCHAR(20) DEFAULT 'PENDING', -- PENDING, ACTIVE, COMPLETED, FAILED
    message         TEXT,
    metadata        JSON,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at    TIMESTAMP,
    duration_ms     INTEGER  -- Time to complete in milliseconds
);

-- Agent Session - Active session tracking and monitoring
CREATE TABLE IF NOT EXISTS agent_session (
    id              BIGINT AUTO_INCREMENT PRIMARY KEY,
    session_id      VARCHAR(64) UNIQUE NOT NULL,
    agent_id        INTEGER, -- REFERENCES agent_registry(agent_id) ON DELETE CASCADE
    task_plan_id    INTEGER,  -- Optional: link to a task plan
    status          VARCHAR(20) DEFAULT 'ACTIVE', -- ACTIVE, IDLE, COMPLETED, ERROR
    session_data    JSON,  -- Session state and context
    started_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at        TIMESTAMP,
    last_activity   TIMESTAMP,
    duration_ms     INTEGER,  -- Total session duration in milliseconds
    agent_state     JSON   -- Current agent execution state
);

-- ============================================================
-- Indexes for Performance Optimization
-- ============================================================

CREATE INDEX idx_agent_registry_status ON agent_registry(status);
CREATE INDEX idx_agent_registry_type ON agent_registry(agent_type);
CREATE INDEX idx_agent_memory_access_scope ON agent_memory_access(memory_scope);
CREATE INDEX idx_agent_collaboration_status ON agent_collaboration(status);
CREATE INDEX idx_agent_session_status ON agent_session(status);

-- ============================================================
-- Views for Common Queries
-- ============================================================

-- Active Sessions View
DROP VIEW IF EXISTS v_active_sessions;
CREATE OR REPLACE VIEW v_active_sessions AS
SELECT 
    s.session_id,
    ar.agent_name,
    ar.agent_type,
    s.status,
    s.started_at,
    s.last_activity,
    s.duration_ms,
    CASE 
        WHEN TIMESTAMPDIFF(MINUTE, s.last_activity, NOW()) < 5 THEN 'ACTIVE'
        ELSE 'IDLE'
    END AS session_state,
    tp.plan_name
FROM agent_session s
LEFT JOIN agent_registry ar ON s.agent_id = ar.id
LEFT JOIN task_plans tp ON s.task_plan_id = tp.plan_id
WHERE s.status != 'COMPLETED' AND s.status != 'ERROR';

-- Collaboration Status View
DROP VIEW IF EXISTS v_collaboration_status;
CREATE OR REPLACE VIEW v_collaboration_status AS
SELECT 
    ac.collab_id,
    sa.agent_name AS source_agent,
    ta.agent_name AS target_agent,
    ac.collab_type,
    ac.status,
    ac.created_at,
    ac.completed_at,
    ac.duration_ms
FROM agent_collaboration ac
LEFT JOIN agent_registry sa ON ac.source_agent_id = sa.id
LEFT JOIN agent_registry ta ON ac.target_agent_id = ta.id;

-- ============================================================
-- Seed Data (Optional - for testing)
-- ============================================================

INSERT IGNORE INTO agent_registry (agent_id, agent_name, agent_type, capabilities, status) 
VALUES ('analysis-agent', 'Analysis Agent', 'analytical', '{"sql_query": true, "data_analysis": true}', 'ACTIVE');

INSERT IGNORE INTO agent_registry (agent_id, agent_name, agent_type, capabilities, status) 
VALUES ('writing-agent', 'Writing Agent', 'content', '{"text_generation": true, "editing": true}', 'ACTIVE');

INSERT IGNORE INTO agent_registry (agent_id, agent_name, agent_type, capabilities, status) 
VALUES ('deploy-agent', 'Deployment Agent', 'deployment', '{"schema_migrate": true, "backup_restore": true}', 'ACTIVE');
