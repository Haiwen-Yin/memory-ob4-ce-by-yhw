#!/usr/bin/env python3
"""
Task Plan API for OceanBase CE 4.x - Ported from PostgreSQL implementation
OceanBase CE Memory System integration for AI Agent task management

Features:
- Task plan persistence across sessions
- Breakpoint recovery after failures  
- Historical pattern learning from completed tasks
- Detailed status auditing

Usage:
    from scripts.task_plan_api import create_task_plan, resume_task, search_completed_tasks
    
Author: Haiwen Yin (胖头鱼 🐟)
Version: v0.1.1 for OceanBase CE 4.x
License: Apache License 2.0
"""

import json
import obpython  # OceanBase Python connector or use standard library
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any


class TaskPlanAPI:
    """Task Plan Management API for AI Agents on OceanBase CE 4.x"""
    
    def __init__(self, host="localhost", port=2881, database="memory_graph", 
                 user="root", tenant="@sys", password=""):
        self.host = host
        self.port = port  
        self.database = database
        self.user = user
        self.tenant = tenant  # OceanBase CE uses tenant for multi-tenancy
        self.password = password
        
    def get_connection(self):
        """Get OceanBase connection"""
        try:
            import obpython
            conn = obpython.connect(
                host=self.host,
                port=self.port,  
                user=f"{self.user}@{self.tenant}",
                database=self.database,
                password=self.password
            )
            return conn
        except ImportError:
            # Fallback: use standard SQL execution via terminal
            print("Note: Using terminal-based SQL execution (obclient)")
            return None
        
    def create_task_plan(self, plan_name: str, plan_type: str = "task", 
                        description: str = "", goal: Dict = None, 
                        steps: List[Dict] = None) -> Dict[str, Any]:
        """
        Create a new task plan and automatically save initial context snapshot
        
        Args:
            plan_name (str): Task name
            plan_type (str): task/deployment/research/analysis
            description (str): Task description
            goal (dict): Final goal (structured)
            steps (list[dict]): Step list [{order, name, action}, ...]
            
        Returns:
            dict: Created plan information
        """
        # Execute via terminal using obclient for OceanBase CE compatibility
        import os
        import subprocess
        
        conn_str = f"obclient -h{self.host} -P2881 -u{self.user}@{self.tenant}"
        
        if self.password:
            conn_str += f" -p{self.password}"
            
        # Convert goal to JSON string for TEXT storage
        goal_json = json.dumps(goal) if goal else None
        
        sql_insert = f"""
INSERT INTO task_plans (PLAN_NAME, PLAN_TYPE, DESCRIPTION, GOAL, METADATA, PRIORITY)
VALUES ('{plan_name}', '{plan_type}', '{description}', 
        {goal_json or 'NULL'}, NULL, 2) RETURNING PLAN_ID;
"""
        
        # Execute SQL and get plan_id
        result = subprocess.run(
            f"echo \"{sql_insert}\" | {conn_str}",
            shell=True, capture_output=True, text=True
        )
        
        # Parse plan_id from output (format varies by obclient version)
        lines = result.stdout.strip().split('\n')
        plan_id = None
        for line in lines:
            if 'PLAN_ID' not in line and line.strip():
                try:
                    plan_id = int(line.strip())
                    break
                except ValueError:
                    continue
        
        if not plan_id:
            # Try last numeric value as fallback
            values = []
            for part in lines[-1].split('|'):
                part = part.strip()
                if part.isdigit():
                    values.append(int(part))
            if values:
                plan_id = values[-1]
        
        result_dict = {
            'plan_id': plan_id,
            'plan_name': plan_name,
            'plan_type': plan_type,
            'description': description,
            'goal': goal,
            'priority': 2,
            'status': 'PENDING',
            'created_at': str(datetime.now())
        }
        
        # Save initial context snapshot
        self._save_snapshot(plan_id, "INIT", {
            "agent_state": "idle",
            "conversation_history": [],
            "next_action": f"Start task: {plan_name}"
        })
        
        # Add steps if provided
        if steps:
            for step_info in steps:
                order = step_info.get('order', 1)
                name = step_info.get('name', '')
                action = step_info.get('action', '')
                
                sql_step = f"""
INSERT INTO task_steps (PLAN_ID, STEP_ORDER, STEP_NAME, ACTION)
VALUES ({plan_id}, {order}, '{name}', '{action}');
"""
                subprocess.run(
                    f"echo \"{sql_step}\" | {conn_str}",
                    shell=True, capture_output=True
                )
        
        return result_dict
    
    def resume_task(self, plan_id: int) -> Dict[str, Any]:
        """
        Resume task execution from breakpoint
        
        Args:
            plan_id (int): Plan ID
            
        Returns:
            dict: Restored context information including next_action, incomplete_steps
        """
        conn_str = f"obclient -h{self.host} -P2881 -u{self.user}@{self.tenant}"
        
        if self.password:
            conn_str += f" -p{self.password}"
            
        # Get latest snapshot
        query_snapshot = f"""
SELECT CONTEXT_DATA FROM task_context_snapshots 
WHERE PLAN_ID = {plan_id} AND IS_LATEST = 1 ORDER BY CREATED_AT DESC LIMIT 1;
"""
        
        result = subprocess.run(
            f"echo \"{query_snapshot}\" | {conn_str}",
            shell=True, capture_output=True, text=True
        )
        
        lines = result.stdout.strip().split('\n')
        context_data = None
        
        # Extract CONTEXT_DATA from output
        for i, line in enumerate(lines):
            if 'CONTEXT_DATA' not in line and line.strip():
                # Try to parse JSON - might be quoted or formatted differently
                try:
                    # Clean up the value (remove trailing semicolons, quotes etc.)
                    clean_value = line.strip()
                    if clean_value.endswith(';'):
                        clean_value = clean_value[:-1]
                    context_data = json.loads(clean_value)
                    break
                except json.JSONDecodeError:
                    continue
        
        if not context_data:
            return {"error": "No snapshot found for this plan"}
        
        # Get incomplete steps
        query_steps = f"""
SELECT STEP_ORDER, STEP_NAME, ACTION FROM task_steps 
WHERE PLAN_ID = {plan_id} AND STATUS IN ('PENDING', 'BLOCKED') 
ORDER BY STEP_ORDER;
"""
        
        result_steps = subprocess.run(
            f"echo \"{query_steps}\" | {conn_str}",
            shell=True, capture_output=True, text=True
        )
        
        incomplete_steps = []
        lines_steps = result_steps.stdout.strip().split('\n')
        
        for line in lines_steps:
            if 'STEP_ORDER' not in line and line.strip():
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 3:
                    try:
                        incomplete_steps.append({
                            "order": int(parts[0]),
                            "name": parts[1],
                            "action": parts[2]
                        })
                    except (ValueError, IndexError):
                        continue
        
        context_data["incomplete_steps"] = incomplete_steps
        return {"restored_context": context_data, "plan_id": plan_id}
    
    def search_completed_tasks(self, query_params: Dict[str, Any]) -> List[Dict]:
        """
        Search completed tasks for learning and pattern reuse
        
        Args:
            query_params (dict): {type, status, tags, keywords, date_range}
            
        Returns:
            list[dict]: Matching task list with success metrics and statistics
        """
        conn_str = f"obclient -h{self.host} -P2881 -u{self.user}@{self.tenant}"
        
        if self.password:
            conn_str += f" -p{self.password}"
            
        # Build query based on params
        conditions = []
        if query_params.get("status"):
            conditions.append(f"STATUS = '{query_params['status']}'")
        if query_params.get("type"):
            conditions.append(f"PLAN_TYPE = '{query_params['type']}'")
            
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        # Limit to 20 results
        query = f"""
SELECT PLAN_ID, PLAN_NAME, PLAN_TYPE, STATUS, CREATED_AT, PRIORITY
FROM task_plans 
WHERE {where_clause}
ORDER BY CREATED_AT DESC LIMIT 20;
"""
        
        result = subprocess.run(
            f"echo \"{query}\" | {conn_str}",
            shell=True, capture_output=True, text=True
        )
        
        results = []
        lines = result.stdout.strip().split('\n')
        
        for line in lines:
            if 'PLAN_ID' not in line and line.strip():
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 6:
                    try:
                        results.append({
                            "plan_id": int(parts[0]),
                            "plan_name": parts[1],
                            "plan_type": parts[2], 
                            "status": parts[3],
                            "created_at": str(parts[4]) if parts[4] else None,
                            "priority": int(parts[5])
                        })
                    except (ValueError, IndexError):
                        continue
        
        return results
    
    def _save_snapshot(self, plan_id, snapshot_type, context_data):
        """Save task context snapshot (internal)"""
        conn_str = f"obclient -h{self.host} -P2881 -u{self.user}@{self.tenant}"
        
        if self.password:
            conn_str += f" -p{self.password}"
            
        # Mark existing latest as not latest
        mark_sql = f"""
UPDATE task_context_snapshots SET IS_LATEST = 0 WHERE PLAN_ID = {plan_id} AND IS_LATEST = 1;
"""
        subprocess.run(f"echo \"{mark_sql}\" | {conn_str}", shell=True, capture_output=True)
        
        # Insert new snapshot with is_latest = 1
        context_json = json.dumps(context_data)
        insert_sql = f"""
INSERT INTO task_context_snapshots (PLAN_ID, SNAPSHOT_TYPE, CONTEXT_DATA, IS_LATEST)
VALUES ({plan_id}, '{snapshot_type}', '{context_json}', 1);
"""
        subprocess.run(f"echo \"{insert_sql}\" | {conn_str}", shell=True, capture_output=True)


# Convenience functions for direct use
def create_task_plan(plan_name, plan_type="task", description="", goal=None, steps=None):
    """Create a new task plan"""
    api = TaskPlanAPI()
    return api.create_task_plan(plan_name, plan_type, description, goal, steps)

def resume_task(plan_id):
    """Resume task execution from breakpoint"""
    api = TaskPlanAPI()
    return api.resume_task(plan_id)

def search_completed_tasks(query_params=None):
    """Search completed tasks for learning"""
    api = TaskPlanAPI()
    if query_params is None:
        query_params = {"status": "SUCCESS"}
    return api.search_completed_tasks(query_params)


if __name__ == "__main__":
    # Demo usage - requires OceanBase connection configured
    print("Task Plan API v0.1.1 for OceanBase CE 4.x")
    print("=" * 50)
    
    # Note: This demo will fail if no OceanBase is running
    try:
        # Create sample task plan
        result = create_task_plan(
            plan_name="Deploy Database Migration",
            plan_type="deployment",
            description="Execute production database migration with rollback capability",
            goal={
                "objective": "Migrate schema changes safely",
                "risk_level": "high",
                "rollback_required": True
            },
            steps=[
                {"order": 1, "name": "Backup current state"},
                {"order": 2, "name": "Execute migration script"},
                {"order": 3, "name": "Run validation queries"},
                {"order": 4, "name": "Update documentation"}
            ]
        )
        
        print(f"\n✅ Created task plan: {result['plan_id']} - {result['plan_name']}")
        print(f"   Status: {result.get('status', 'PENDING')}")
    except Exception as e:
        print(f"⚠️  Demo mode - OceanBase connection required: {e}")
