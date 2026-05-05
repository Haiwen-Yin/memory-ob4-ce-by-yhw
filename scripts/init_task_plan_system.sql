-- ============================================
-- Task Plan System for OceanBase CE 4.x (v0.1.1)
-- Adapted from PostgreSQL implementation with OceanBase compatibility
-- ============================================

-- ============================================
-- 1. TASK_PLANS - Core task plan table
-- ============================================
CREATE TABLE IF NOT EXISTS task_plans (
    PLAN_ID       BIGINT PRIMARY KEY,
    PLAN_NAME     VARCHAR(200),                    -- Task name
    PLAN_TYPE     VARCHAR(50) NOT NULL DEFAULT 'task',  -- task/deployment/research/analysis
    STATUS        VARCHAR(30) DEFAULT 'PENDING',   -- PENDING/RUNNING/SUCCESS/FAILED/CANCELLED/PAUSED
    DESCRIPTION   TEXT,                            -- Task description and intent
    GOAL          TEXT,                            -- JSON: final goal (structured)
    
    -- Priority and time management
    PRIORITY      INT DEFAULT 2 CHECK(PRIORITY BETWEEN 1 AND 5),
    CREATED_AT    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    STARTED_AT    TIMESTAMP NULL,                  -- Start execution time
    UPDATED_AT    TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    COMPLETED_AT  TIMESTAMP NULL,                 -- Completion time
    EXPIRES_AT    TIMESTAMP NULL,                 -- Expiration time
    
    -- Metadata (JSON text)
    METADATA      TEXT,                            -- JSON: session_id, agent_context etc.
    TAGS          TEXT                             -- JSON: tag array
);

-- ============================================
-- 2. TASK_STEPS - Task step execution table
-- ============================================
CREATE TABLE IF NOT EXISTS task_steps (
    STEP_ID       BIGINT PRIMARY KEY,
    PLAN_ID       BIGINT NOT NULL REFERENCES task_plans(PLAN_ID),
    STEP_ORDER    INT NOT NULL,                  -- Step sequence (1,2,3...)
    STEP_NAME     VARCHAR(200),                    -- Step name
    ACTION        TEXT,                             -- Action description to execute
    TOOLS_USED    TEXT,                            -- JSON: tools used list
    
    -- Execution status
    STATUS        VARCHAR(30) DEFAULT 'PENDING',   -- PENDING/IN_PROGRESS/SUCCESS/FAILED/BLOCKED
    RESULT        TEXT,                             -- Step execution result
    ERROR_MSG     TEXT,                             -- Error message (if any)
    
    -- Timestamps
    CREATED_AT    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    STARTED_AT    TIMESTAMP NULL,
    COMPLETED_AT  TIMESTAMP NULL,
    
    UNIQUE (PLAN_ID, STEP_ORDER)
);

-- ============================================
-- 3. TASK_CONTEXT_SNAPSHOTS - Task context snapshot (critical for breakpoint recovery)
-- ============================================
CREATE TABLE IF NOT EXISTS task_context_snapshots (
    SNAPSHOT_ID   BIGINT PRIMARY KEY,
    PLAN_ID       BIGINT NOT NULL REFERENCES task_plans(PLAN_ID),
    
    -- Snapshot type
    SNAPSHOT_TYPE VARCHAR(30) DEFAULT 'AUTO',      -- AUTO/MANUAL/ON_ERROR
    
    -- Context content (complete state)
    CONTEXT_DATA  TEXT,                             -- JSON: agent_state, conversation_history etc.
    MEMORY_IDS    TEXT,                             -- JSON: associated memory node ID list
    NEXT_ACTION   TEXT,                             -- Next action to execute description
    
    -- Snapshot information
    CREATED_AT    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    IS_LATEST     INT CHECK(IS_LATEST IN (0, 1)) DEFAULT 0,
    
    -- Trigger reason (Oracle TRIGGER is a reserved word, use trigger_reason instead)
    TRIGGER_REASON TEXT                             -- JSON: trigger_reason
);

-- ============================================
-- 4. TASK_TOOL_CALLS - Tool call records (audit trail)
-- ============================================
CREATE TABLE IF NOT EXISTS task_tool_calls (
    CALL_ID       BIGINT PRIMARY KEY,
    PLAN_ID       BIGINT NOT NULL REFERENCES task_plans(PLAN_ID),
    STEP_ID       BIGINT REFERENCES task_steps(STEP_ID),
    
    -- Tool information
    TOOL_NAME     VARCHAR(100) NOT NULL,           -- tool name (terminal/browser/memory etc.)
    ACTION        TEXT NOT NULL,                    -- Executed operation description
    
    -- Call result
    STATUS        VARCHAR(30) DEFAULT 'SUCCESS',   -- SUCCESS/FAILED/TIMEOUT
    RESULT_SIZE   INT,                           -- Return result size (bytes)
    
    -- Time information
    CREATED_AT    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    DURATION_MS   INT                            -- Execution duration milliseconds
);

-- ============================================
-- 5. TASK_DEPENDENCIES - Task dependency graph
-- ============================================
CREATE TABLE IF NOT EXISTS task_dependencies (
    DEPENDENCY_ID BIGINT PRIMARY KEY,
    SOURCE_PLAN_ID BIGINT NOT NULL REFERENCES task_plans(PLAN_ID),
    TARGET_PLAN_ID BIGINT NOT NULL REFERENCES task_plans(PLAN_ID),
    
    -- Dependency type
    DEPENDENCY_TYPE VARCHAR(30) DEFAULT 'HARD',    -- HARD/SOFT/EXCLUSIVE/RECOMMENDED
    CONDITION     TEXT,                             -- JSON: trigger condition description
    
    CREATED_AT    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- Task Plan Indexes (OceanBase CE 4.x optimized)
-- ============================================
CREATE INDEX IF NOT EXISTS idx_task_plans_status ON task_plans(STATUS);
CREATE INDEX IF NOT EXISTS idx_task_plans_type ON task_plans(PLAN_TYPE);
CREATE INDEX IF NOT EXISTS idx_task_plans_created ON task_plans(CREATED_AT DESC);
CREATE INDEX IF NOT EXISTS idx_task_plans_priority ON task_plans(PRIORITY, CREATED_AT);

CREATE INDEX IF NOT EXISTS idx_task_steps_plan ON task_steps(PLAN_ID, STEP_ORDER);
CREATE INDEX IF NOT EXISTS idx_task_steps_status ON task_steps(STATUS);

-- NOTE: OceanBase CE 4.x may not support WHERE on indexes - use regular index instead
CREATE INDEX IF NOT EXISTS idx_context_snapshot_plan ON task_context_snapshots(PLAN_ID);

CREATE INDEX IF NOT EXISTS idx_tool_calls_plan ON task_tool_calls(PLAN_ID);
CREATE INDEX IF NOT EXISTS idx_tool_calls_time ON task_tool_calls(CREATED_AT DESC);
