"""
memory-ob4-ce-by-yhw v0.1.2 - Agent API for Multi-Agent Architecture

Python API for managing multiple AI agents with centralized memory access control,
session management, and collaboration capabilities on OceanBase CE 4.x.

Author: Haiwen Yin (胖头鱼 🐟)
Version: v0.1.2
License: Apache License 2.0
"""

import json
import time
import uuid
from datetime import datetime
from typing import Optional, Dict, List, Any


class AgentRegistryAPI:
    """Agent lifecycle management API for the Multi-Agent Architecture."""
    
    def __init__(self, conn_params=None):
        """
        Initialize the agent registry API.
        
        Args:
            conn_params (dict): Connection parameters for OceanBase
                - host: Database host address (default: '127.0.0.1')
                - port: Database port number (default: 2881)
                - user: Username (default: 'root@mem')
                - password: Password
                - database: Database name (default: 'memory_graph')
        """
        if conn_params is None:
            self.conn_params = {
                'host': '127.0.0.1',
                'port': 2881,
                'user': 'root@mem',
                'password': '',
                'database': 'memory_graph'
            }
        else:
            self.conn_params = conn_params
    
    def register_agent(self, agent_name, agent_type="general", capabilities=None, status="ACTIVE"):
        """
        Register a new AI agent in the registry.
        
        Args:
            agent_name (str): Human-readable name for the agent
            agent_type (str): Type of agent - analytical, content, deployment, etc.
            capabilities (dict): Dictionary of agent capabilities
            status (str): Initial status - INACTIVE, ACTIVE, PAUSED, STOPPED
        
        Returns:
            dict: Registered agent information including id and agent_id
        """
        # Generate unique agent ID
        agent_id = f"{agent_type}-agent-{int(time.time())}"
        
        if capabilities is None:
            capabilities = {}
        
        query = """
            INSERT INTO agent_registry (agent_id, agent_name, agent_type, 
                                        capabilities, status, created_at)
            VALUES (%s, %s, %s, %s, %s, NOW())
            RETURNING id;
        """
        
        params = [
            agent_id,
            agent_name,
            agent_type,
            json.dumps(capabilities),  # Serialize capabilities to JSON
            status
        ]
        
        try:
            cursor = self._execute_query(query, params)
            row = cursor.fetchone()
            
            result = {
                'id': row[0],
                'agent_id': agent_id,
                'agent_name': agent_name,
                'agent_type': agent_type,
                'status': status,
                'capabilities': capabilities,
                'registered_at': datetime.now()
            }
            
            print(f"Registered agent: {agent_name} (ID: {agent_id})")
            return result
            
        except Exception as e:
            raise RuntimeError(f"Failed to register agent: {str(e)}")
    
    def get_agent(self, agent_id=None, agent_db_id=None):
        """
        Get details of a specific registered agent.
        
        Args:
            agent_id (str): Unique identifier for the agent
            agent_db_id (int): Primary key in database
        
        Returns:
            dict: Agent information or None if not found
        """
        query = "SELECT * FROM agent_registry WHERE 1=0"
        params = []
        
        if agent_id:
            query += " AND agent_id = %s"
            params.append(agent_id)
        elif agent_db_id:
            query += " AND id = %s"
            params.append(agent_db_id)
        else:
            raise ValueError("Must provide either agent_id or agent_db_id")
        
        cursor = self._execute_query(query, params)
        row = cursor.fetchone()
        
        if not row:
            return None
        
        # Map column names to values
        columns = [desc[0] for desc in cursor.description]
        result = dict(zip(columns, row))
        
        # Deserialize JSON fields
        if 'capabilities' in result and isinstance(result['capabilities'], str):
            try:
                result['capabilities'] = json.loads(result['capabilities'])
            except:
                pass
        
        return result
    
    def list_active_agents(self):
        """
        List all agents with ACTIVE status.
        
        Returns:
            list[dict]: List of active agents
        """
        query = "SELECT * FROM agent_registry WHERE status = 'ACTIVE'"
        cursor = self._execute_query(query)
        rows = cursor.fetchall()
        
        if not rows:
            return []
        
        columns = [desc[0] for desc in cursor.description]
        agents = []
        
        for row in rows:
            agent = dict(zip(columns, row))
            # Deserialize JSON fields
            if 'capabilities' in agent and isinstance(agent['capabilities'], str):
                try:
                    agent['capabilities'] = json.loads(agent['capabilities'])
                except:
                    pass
            agents.append(agent)
        
        print(f"Found {len(agents)} active agent(s)")
        return agents
    
    def _execute_query(self, query, params=None):
        """Execute a SQL query and return cursor."""
        try:
            import pymysql
            connection = None
            cursor = None
            try:
                connection = pymysql.connect(
                    host=self.conn_params.get('host', '127.0.0.1'),
                    port=int(self.conn_params.get('port', 2881)),
                    user=self.conn_params.get('user', 'root@mem'),
                    password=self.conn_params.get('password', ''),
                    database=self.conn_params.get('database', 'memory_graph')
                )
                cursor = connection.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                return cursor
                
            finally:
                # Ensure connection is properly closed to prevent resource leaks
                if cursor:
                    try:
                        cursor.close()
                    except Exception:
                        pass
                if connection and not connection.closed:
                    try:
                        connection.close()
                    except Exception:
                        pass
                    
        except ImportError:
            # Fallback to psycopg2 for PostgreSQL compatibility testing
            import psycopg2
            conn_string = f"host={self.conn_params.get('host', 'localhost')} " \
                         f"port={self.conn_params.get('port', 5432)} " \
                         f"user={self.conn_params.get('user', 'postgres')} " \
                         f"password={self.conn_params.get('password', '')} " \
                         f"dbname={self.conn_params.get('database', 'memory_graph')}"
            
            connection = psycopg2.connect(conn_string)
            cursor = connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            return cursor


class MemoryVisibilityAPI:
    """Memory access control API for the Multi-Agent Architecture."""
    
    def __init__(self, conn_params=None):
        if conn_params is None:
            self.conn_params = {
                'host': '127.0.0.1',
                'port': 2881,
                'user': 'root@mem',
                'password': '',
                'database': 'memory_graph'
            }
        else:
            self.conn_params = conn_params
    
    def set_access_policy(self, agent_id, memory_scope="PRIVATE", 
                          accessible_to=None, can_read=True, can_write=False):
        """
        Set access policy for an agent's memory visibility.
        
        Args:
            agent_id (int or str): Agent identifier
            memory_scope (str): Visibility scope - PRIVATE, SHARED, COLLABORATIVE
            accessible_to (list): List of agent IDs that can access
            can_read (bool): Whether agent can read the memory
            can_write (bool): Whether agent can write to the memory
        
        Returns:
            dict: Created or updated policy information
        """
        if accessible_to is None:
            accessible_to = []
        
        query = """
            SELECT id FROM agent_memory_access WHERE agent_id = %s LIMIT 1;
        """
        
        params = [
            agent_id,
            memory_scope,
            json.dumps(accessible_to),  # Serialize to JSON array
            can_read,
            can_write
        ]
        
        try:
            cursor = self._execute_query(query, params)
            row = cursor.fetchone()
            
            if row:
                result = {
                    'id': row[0],
                    'agent_id': agent_id,
                    'memory_scope': memory_scope,
                    'accessible_to': accessible_to,
                    'can_read': can_read,
                    'can_write': can_write
                }
                print(f"Set access policy for agent {agent_id}: {memory_scope}")
                return result
            else:
                # Update existing policy if insert failed due to conflict
                update_query = """
                    UPDATE agent_memory_access 
                    SET memory_scope = %s, accessible_to = %s, can_read = %s, can_write = %s
                    WHERE agent_id = %s;
                """
                self._execute_query(update_query, params)
                
                return {
                    'agent_id': agent_id,
                    'memory_scope': memory_scope,
                    'accessible_to': accessible_to,
                    'can_read': can_read,
                    'can_write': can_write,
                    'status': 'updated'
                }
                
        except Exception as e:
            raise RuntimeError(f"Failed to set access policy: {str(e)}")
    
    def get_access_policy(self, agent_id):
        """Get the current access policy for an agent."""
        query = "SELECT * FROM agent_memory_access WHERE agent_id = %s ORDER BY created_at DESC LIMIT 1"
        cursor = self._execute_query(query, [agent_id])
        row = cursor.fetchone()
        
        if not row:
            return None
        
        columns = [desc[0] for desc in cursor.description]
        result = dict(zip(columns, row))
        
        # Deserialize JSON fields
        if 'accessible_to' in result and isinstance(result['accessible_to'], str):
            try:
                result['accessible_to'] = json.loads(result['accessible_to'])
            except:
                pass
        
        return result
    
    def _execute_query(self, query, params=None):
        """Execute a SQL query and return cursor."""
        try:
            import pymysql
            connection = None
            cursor = None
            try:
                connection = pymysql.connect(
                    host=self.conn_params.get('host', '127.0.0.1'),
                    port=int(self.conn_params.get('port', 2881)),
                    user=self.conn_params.get('user', 'root@mem'),
                    password=self.conn_params.get('password', ''),
                    database=self.conn_params.get('database', 'memory_graph')
                )
                cursor = connection.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                return cursor
                
            finally:
                # Ensure connection is properly closed to prevent resource leaks
                if cursor:
                    try:
                        cursor.close()
                    except Exception:
                        pass
                if connection and not connection.closed:
                    try:
                        connection.close()
                    except Exception:
                        pass
                    
        except ImportError:
            import psycopg2
            conn_string = f"host={self.conn_params.get('host', 'localhost')} " \
                         f"port={self.conn_params.get('port', 5432)} " \
                         f"user={self.conn_params.get('user', 'postgres')} " \
                         f"password={self.conn_params.get('password', '')} " \
                         f"dbname={self.conn_params.get('database', 'memory_graph')}"
            connection = psycopg2.connect(conn_string)
            cursor = connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor


class AgentSessionAPI:
    """Session management API for the Multi-Agent Architecture."""
    
    def __init__(self, conn_params=None):
        if conn_params is None:
            self.conn_params = {
                'host': '127.0.0.1',
                'port': 2881,
                'user': 'root@mem',
                'password': '',
                'database': 'memory_graph'
            }
        else:
            self.conn_params = conn_params
    
    def create_session(self, agent_id, task_plan_id=None):
        """
        Create a new session for an agent.
        
        Args:
            agent_id (int or str): Agent identifier
            task_plan_id (int): Optional link to a task plan
        
        Returns:
            dict: Created session information
        """
        session_id = f"session-{str(uuid.uuid4())[:12]}"
        
        query = """
            INSERT INTO agent_session 
                (session_id, agent_id, task_plan_id, status, started_at)
            VALUES (%s, %s, %s, 'ACTIVE', NOW());
        """
        
        params = [session_id, agent_id, task_plan_id]
        
        try:
            self._execute_query(query, params)
            
            result = {
                'session_id': session_id,
                'agent_id': agent_id,
                'task_plan_id': task_plan_id,
                'status': 'ACTIVE',
                'started_at': datetime.now()
            }
            print(f"Created session: {session_id}")
            return result
            
        except Exception as e:
            raise RuntimeError(f"Failed to create session: {str(e)}")
    
    def get_active_sessions(self):
        """Get all non-completed sessions."""
        query = "SELECT * FROM agent_session WHERE status != 'COMPLETED' AND status != 'ERROR'"
        cursor = self._execute_query(query)
        rows = cursor.fetchall()
        
        if not rows:
            return []
        
        columns = [desc[0] for desc in cursor.description]
        sessions = []
        
        for row in rows:
            session = dict(zip(columns, row))
            # Deserialize JSON fields
            for field in ['session_data', 'agent_state']:
                if field in session and isinstance(session[field], str):
                    try:
                        session[field] = json.loads(session[field])
                    except:
                        pass
            sessions.append(session)
        
        print(f"Found {len(sessions)} active session(s)")
        return sessions
    
    def end_session(self, session_id):
        """Mark a session as completed."""
        query = """
            UPDATE agent_session 
            SET status = 'COMPLETED', ended_at = NOW()
            WHERE session_id = %s;
        """
        
        try:
            cursor = self._execute_query(query, [session_id])
            
            if cursor.rowcount > 0:
                print(f"Ended session: {session_id}")
                return {'status': 'completed', 'session_id': session_id}
            else:
                raise ValueError(f"Session {session_id} not found")
                
        except Exception as e:
            raise RuntimeError(f"Failed to end session: {str(e)}")
    
    def _execute_query(self, query, params=None):
        """Execute a SQL query and return cursor."""
        try:
            import pymysql
            connection = None
            cursor = None
            try:
                connection = pymysql.connect(
                    host=self.conn_params.get('host', '127.0.0.1'),
                    port=int(self.conn_params.get('port', 2881)),
                    user=self.conn_params.get('user', 'root@mem'),
                    password=self.conn_params.get('password', ''),
                    database=self.conn_params.get('database', 'memory_graph')
                )
                cursor = connection.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                return cursor
                
            finally:
                # Ensure connection is properly closed to prevent resource leaks
                if cursor:
                    try:
                        cursor.close()
                    except Exception:
                        pass
                if connection and not connection.closed:
                    try:
                        connection.close()
                    except Exception:
                        pass
                    
        except ImportError:
            import psycopg2
            conn_string = f"host={self.conn_params.get('host', 'localhost')} " \
                         f"port={self.conn_params.get('port', 5432)} " \
                         f"user={self.conn_params.get('user', 'postgres')} " \
                         f"password={self.conn_params.get('password', '')} " \
                         f"dbname={self.conn_params.get('database', 'memory_graph')}"
            connection = psycopg2.connect(conn_string)
            cursor = connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor


class CollaborationAPI:
    """Agent-to-agent collaboration messaging API."""
    
    def __init__(self, conn_params=None):
        if conn_params is None:
            self.conn_params = {
                'host': '127.0.0.1',
                'port': 2881,
                'user': 'root@mem',
                'password': '',
                'database': 'memory_graph'
            }
        else:
            self.conn_params = conn_params
    
    def send_collaboration_message(self, source_agent_id, target_agent_id, 
                                    collab_type="REQUEST", message="", metadata=None):
        """
        Send a collaboration request between agents.
        
        Args:
            source_agent_id (int or str): Source agent identifier
            target_agent_id (int or str): Target agent identifier
            collab_type (str): Type of collaboration - REQUEST, RESPONSE, SHARING, QUERY
            message (str): Message content
            metadata (dict): Optional additional data
        
        Returns:
            dict: Created collaboration record
        """
        if metadata is None:
            metadata = {}
        
        collab_id = f"collab-{str(uuid.uuid4())[:12]}"
        
        query = """
            INSERT INTO agent_collaboration 
                (collab_id, source_agent_id, target_agent_id, collab_type, message, status)
            VALUES (%s, %s, %s, %s, %s, 'PENDING');
        """
        
        params = [collab_id, source_agent_id, target_agent_id, collab_type, message]
        
        try:
            cursor = self._execute_query(query, params)
            
            # Update metadata if provided
            if metadata:
                meta_query = "UPDATE agent_collaboration SET metadata = %s WHERE collab_id = %s"
                self._execute_query(meta_query, [json.dumps(metadata), collab_id])
            
            result = {
                'collab_id': collab_id,
                'source_agent_id': source_agent_id,
                'target_agent_id': target_agent_id,
                'collab_type': collab_type,
                'status': 'PENDING',
                'message': message,
                'created_at': datetime.now()
            }
            print(f"Sent {collab_type} from agent {source_agent_id} to {target_agent_id}")
            return result
            
        except Exception as e:
            raise RuntimeError(f"Failed to send collaboration message: {str(e)}")
    
    def update_collaboration_status(self, collab_id, new_status):
        """Update the status of a collaboration request."""
        query = "UPDATE agent_collaboration SET status = %s WHERE collab_id = %s"
        
        try:
            cursor = self._execute_query(query, [new_status, collab_id])
            
            if cursor.rowcount > 0:
                print(f"Updated collaboration {collab_id} to {new_status}")
                return {'status': new_status, 'collab_id': collab_id}
            else:
                raise ValueError(f"Collaboration {collab_id} not found")
                
        except Exception as e:
            raise RuntimeError(f"Failed to update collaboration status: {str(e)}")
    
    def get_pending_requests(self):
        """Get all pending collaboration requests."""
        query = "SELECT * FROM agent_collaboration WHERE status = 'PENDING'"
        cursor = self._execute_query(query)
        rows = cursor.fetchall()
        
        if not rows:
            return []
        
        columns = [desc[0] for desc in cursor.description]
        requests = []
        
        for row in rows:
            request = dict(zip(columns, row))
            # Deserialize JSON fields
            if 'metadata' in request and isinstance(request['metadata'], str):
                try:
                    request['metadata'] = json.loads(request['metadata'])
                except:
                    pass
            requests.append(request)
        
        print(f"Found {len(requests)} pending request(s)")
        return requests
    
    def _execute_query(self, query, params=None):
        """Execute a SQL query and return cursor."""
        try:
            import pymysql
            connection = None
            cursor = None
            try:
                connection = pymysql.connect(
                    host=self.conn_params.get('host', '127.0.0.1'),
                    port=int(self.conn_params.get('port', 2881)),
                    user=self.conn_params.get('user', 'root@mem'),
                    password=self.conn_params.get('password', ''),
                    database=self.conn_params.get('database', 'memory_graph')
                )
                cursor = connection.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                return cursor
                
            finally:
                # Ensure connection is properly closed to prevent resource leaks
                if cursor:
                    try:
                        cursor.close()
                    except Exception:
                        pass
                if connection and not connection.closed:
                    try:
                        connection.close()
                    except Exception:
                        pass
                    
        except ImportError:
            import psycopg2
            conn_string = f"host={self.conn_params.get('host', 'localhost')} " \
                         f"port={self.conn_params.get('port', 5432)} " \
                         f"user={self.conn_params.get('user', 'postgres')} " \
                         f"password={self.conn_params.get('password', '')} " \
                         f"dbname={self.conn_params.get('database', 'memory_graph')}"
            connection = psycopg2.connect(conn_string)
            cursor = connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor


# Convenience functions for quick access

def create_agent(agent_name, agent_type="general", capabilities=None):
    """Create and register a new agent (convenience function)."""
    registry = AgentRegistryAPI()
    return registry.register_agent(agent_name, agent_type, capabilities)

def get_active_agents():
    """Get all active agents (convenience function)."""
    registry = AgentRegistryAPI()
    return registry.list_active_agents()

def create_session(agent_id):
    """Create a new session for an agent (convenience function)."""
    session_api = AgentSessionAPI()
    return session_api.create_session(agent_id)


# Module-level documentation
__all__ = [
    'AgentRegistryAPI',
    'MemoryVisibilityAPI', 
    'CollaborationAPI',
    'AgentSessionAPI',
    'create_agent',
    'get_active_agents',
    'create_session'
]
