# OceanBase CE Knowledge Base API v1.0.0
# Author: yhw (胖头鱼 🐟)
# Compatible with: oracle-memory-by-yhw v1.0.0

import mysql.connector
import json
import requests
from typing import List, Dict, Optional
from datetime import datetime

class KnowledgeBaseAPI:
    """
    OceanBase CE Knowledge Base API
    Provides CRUD operations for knowledge concepts and relationships
    """
    
    def __init__(self, host='10.10.10.132', port=2881, 
                 user='root@memory', password='OceanBase#123', 
                 database='memory'):
        """
        Initialize Knowledge Base API
        
        Args:
            host: OceanBase CE server host
            port: OceanBase CE server port (default: 2881)
            user: Username in format user@tenant
            password: User password
            database: Database name
        """
        self.db_config = {
            'host': host,
            'port': port,
            'user': user,
            'password': password,
            'database': database,
            'charset': 'utf8mb4'
        }
        
        # Embedding API configuration
        self.embedding_api = "http://10.10.10.1:12345/v1/embeddings"
        self.embedding_model = "text-embedding-ada-002"  # or BGE-M3
    
    def _get_connection(self):
        """Get database connection"""
        return mysql.connector.connect(**self.db_config)
    
    def _generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector from text
        
        Args:
            text: Input text
            
        Returns:
            List[float]: Embedding vector
        """
        try:
            response = requests.post(
                self.embedding_api,
                json={"model": self.embedding_model, "input": text},
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            if 'data' in data and len(data['data']) > 0:
                return data['data'][0]['embedding']
            return []
        except Exception as e:
            print(f"Warning: Failed to generate embedding: {e}")
            return []
    
    def create_concept(self, concept_name: str, concept_type: str,
                     description: str = None, category: str = None,
                     content: str = None, confidence: float = 0.80,
                     tags: List[str] = None, metadata: Dict = None) -> Dict:
        """
        Create a new knowledge concept
        
        Args:
            concept_name: Concept name
            concept_type: Concept type (FACT/RULE/PATTERN/EXPERIENCE/PRINCIPLE)
            description: Concept description
            category: Concept category
            content: Full content
            confidence: Confidence score (0.0-1.0)
            tags: List of tags
            metadata: Additional metadata (dict)
            
        Returns:
            Dict: Created concept with concept_id
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Generate embedding
            embedding_text = self._generate_embedding(concept_name + ' ' + (description or ''))
            embedding_str = json.dumps(embedding_text) if embedding_text else None
            
            # Insert concept (使用小写表名和列名）
            sql = """
                INSERT INTO knowledge_concepts (
                    CONCEPT_NAME, CONCEPT_TYPE, DESCRIPTION, CATEGORY,
                    CONTENT, CONFIDENCE, EMBEDDING,
                    SOURCE_TYPE, VALIDATION_STATUS
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(sql, (
                concept_name,
                concept_type,
                description,
                category,
                content,
                confidence,
                embedding_str,
                'MANUAL',
                'PENDING'
            ))
            
            concept_id = cursor.lastrowid
            
            # Add tags
            if tags:
                for tag in tags:
                    cursor.execute("""
                        INSERT INTO knowledge_tags (CONCEPT_ID, TAG_NAME, TAG_VALUE)
                        VALUES (%s, %s, %s)
                    """, (concept_id, tag, tag))
            
            # Log creation
            cursor.execute("""
                INSERT INTO knowledge_audit_log (CONCEPT_ID, OPERATION, OPERATION_TYPE, DETAILS, PERFORMED_BY)
                VALUES (%s, 'Create', 'CONCEPT', %s, %s)
            """, (concept_id, f'Created concept: {concept_name}', 'KnowledgeBaseAPI'))
            
            conn.commit()
            
            return {
                'concept_id': concept_id,
                'concept_name': concept_name,
                'concept_type': concept_type,
                'description': description,
                'category': category,
                'confidence': confidence,
                'created_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            conn.rollback()
            raise Exception(f"Failed to create concept: {e}")
        finally:
            cursor.close()
            conn.close()
    
    def update_concept(self, concept_id: int, **kwargs) -> Dict:
        """
        Update a knowledge concept
        
        Args:
            concept_id: Concept ID
            **kwargs: Fields to update (description, content, confidence, etc.)
            
        Returns:
            Dict: Updated concept
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Build update query dynamically
            update_fields = []
            values = []
            
            for key, value in kwargs.items():
                if key.upper() in ['DESCRIPTION', 'CONTENT', 'CATEGORY', 'CONFIDENCE']:
                    update_fields.append(f"{key.upper()} = %s")
                    values.append(value)
            
            if not update_fields:
                raise Exception("No valid fields to update")
            
            values.append(concept_id)
            
            sql = f"""
                UPDATE knowledge_concepts
                SET {', '.join(update_fields)}
                WHERE CONCEPT_ID = %s
            """
            
            cursor.execute(sql, values)
            
            # Log update
            cursor.execute("""
                INSERT INTO knowledge_audit_log (CONCEPT_ID, OPERATION, OPERATION_TYPE, DETAILS, PERFORMED_BY)
                VALUES (%s, 'Update', 'CONCEPT', %s, %s)
            """, (concept_id, f'Updated concept: {list(kwargs.keys())}', 'KnowledgeBaseAPI'))
            
            conn.commit()
            
            return {'concept_id': concept_id, 'updated': True}
            
        except Exception as e:
            conn.rollback()
            raise Exception(f"Failed to update concept: {e}")
        finally:
            cursor.close()
            conn.close()
    
    def delete_concept(self, concept_id: int) -> Dict:
        """
        Delete a knowledge concept
        
        Args:
            concept_id: Concept ID
            
        Returns:
            Dict: Deletion result
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Get concept name for logging
            cursor.execute("""
                SELECT CONCEPT_NAME FROM knowledge_concepts 
                WHERE CONCEPT_ID = %s
            """, (concept_id,))
            
            result = cursor.fetchone()
            if not result:
                raise Exception(f"Concept {concept_id} not found")
            
            concept_name = result[0]
            
            # Delete concept (cascade will handle related records)
            cursor.execute("""
                DELETE FROM knowledge_concepts WHERE CONCEPT_ID = %s
            """, (concept_id,))
            
            # Log deletion
            cursor.execute("""
                INSERT INTO knowledge_audit_log (CONCEPT_ID, OPERATION, OPERATION_TYPE, DETAILS, PERFORMED_BY)
                VALUES (%s, 'Delete', 'CONCEPT', %s, %s)
            """, (concept_id, f'Deleted concept: {concept_name}', 'KnowledgeBaseAPI'))
            
            conn.commit()
            
            return {'concept_id': concept_id, 'deleted': True}
            
        except Exception as e:
            conn.rollback()
            raise Exception(f"Failed to delete concept: {e}")
        finally:
            cursor.close()
            conn.close()
    
    def create_relationship(self, source_concept_id: int, target_concept_id: int,
                          relationship_type: str, strength: float = 0.90,
                          confidence: float = 0.80, properties: Dict = None) -> Dict:
        """
        Create a knowledge graph relationship
        
        Args:
            source_concept_id: Source concept ID
            target_concept_id: Target concept ID
            relationship_type: Relationship type (IS_A/PART_OF/CAUSES/ENABLES/CONTRADICTS/SUPPORTS)
            strength: Relationship strength (0.0-1.0)
            confidence: Confidence score (0.0-1.0)
            properties: Additional properties (dict)
            
        Returns:
            Dict: Created relationship with relationship_id
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            sql = """
                INSERT INTO knowledge_graph (
                    SOURCE_CONCEPT_ID, TARGET_CONCEPT_ID, RELATIONSHIP_TYPE,
                    RELATIONSHIP_STRENGTH, CONFIDENCE, PROPERTIES, SOURCE_TYPE
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(sql, (
                source_concept_id,
                target_concept_id,
                relationship_type,
                strength,
                confidence,
                json.dumps(properties) if properties else None,
                'MANUAL'
            ))
            
            relationship_id = cursor.lastrowid
            
            conn.commit()
            
            return {
                'relationship_id': relationship_id,
                'source_concept_id': source_concept_id,
                'target_concept_id': target_concept_id,
                'relationship_type': relationship_type,
                'strength': strength,
                'created_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            conn.rollback()
            raise Exception(f"Failed to create relationship: {e}")
        finally:
            cursor.close()
            conn.close()
    
    def search_by_text(self, keyword: str, limit: int = 10) -> List[Dict]:
        """
        Search concepts by text keyword
        
        Args:
            keyword: Search keyword
            limit: Maximum results
            
        Returns:
            List[Dict]: Matching concepts
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            sql = """
                SELECT CONCEPT_ID, CONCEPT_NAME, CONCEPT_TYPE, DESCRIPTION,
                       CATEGORY, CONFIDENCE, VALIDATION_STATUS
                FROM knowledge_concepts
                WHERE CONCEPT_NAME LIKE %s
                   OR DESCRIPTION LIKE %s
                   OR CONTENT LIKE %s
                LIMIT %s
            """
            
            cursor.execute(sql, (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%', limit))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'concept_id': row[0],
                    'concept_name': row[1],
                    'concept_type': row[2],
                    'description': row[3],
                    'category': row[4],
                    'confidence': float(row[5]) if row[5] else 0.0,
                    'validation_status': row[6]
                })
            
            return results
            
        except Exception as e:
            raise Exception(f"Failed to search: {e}")
        finally:
            cursor.close()
            conn.close()
    
    def search_similar_concepts(self, query_text: str, limit: int = 5,
                               threshold: float = 0.75) -> List[Dict]:
        """
        Search concepts by semantic similarity (application-layer fallback)
        
        Args:
            query_text: Query text
            limit: Maximum results
            threshold: Similarity threshold (0.0-1.0)
            
        Returns:
            List[Dict]: Similar concepts with similarity scores
        """
        # Note: OceanBase CE v4.5.0 supports native VECTOR_DISTANCE
        # This is a fallback implementation
        # For production, use native VECTOR_DISTANCE in SQL
        
        import numpy as np
        
        # Generate query embedding
        query_embedding = self._generate_embedding(query_text)
        if not query_embedding:
            return []
        
        # Fetch all concepts with embeddings
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT CONCEPT_ID, CONCEPT_NAME, CONCEPT_TYPE, EMBEDDING, CONFIDENCE
                FROM knowledge_concepts
                WHERE EMBEDDING IS NOT NULL
            """)
            
            results = []
            for row in cursor.fetchall():
                concept_id, concept_name, concept_type, embedding_str, confidence = row
                
                try:
                    # Parse embedding
                    embedding = json.loads(embedding_str)
                    
                    # Calculate cosine similarity
                    query_vec = np.array(query_embedding, dtype=np.float64)
                    doc_vec = np.array(embedding, dtype=np.float64)
                    
                    similarity = np.dot(query_vec, doc_vec) / (
                        np.linalg.norm(query_vec) * np.linalg.norm(doc_vec)
                    )
                    
                    if similarity >= threshold:
                        results.append({
                            'concept_id': concept_id,
                            'concept_name': concept_name,
                            'concept_type': concept_type,
                            'similarity': float(similarity),
                            'confidence': float(confidence) if confidence else 0.0
                        })
                except Exception:
                    continue
            
            # Sort by similarity descending
            results.sort(key=lambda x: x['similarity'], reverse=True)
            
            return results[:limit]
            
        except Exception as e:
            raise Exception(f"Failed to search similar concepts: {e}")
        finally:
            cursor.close()
            conn.close()
    
    def get_concept_with_graph(self, concept_id: int) -> Dict:
        """
        Get concept with its knowledge graph relationships
        
        Args:
            concept_id: Concept ID
            
        Returns:
            Dict: Concept with outgoing and incoming relationships
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Get concept
            cursor.execute("""
                SELECT CONCEPT_ID, CONCEPT_NAME, CONCEPT_TYPE, DESCRIPTION,
                       CATEGORY, CONFIDENCE, VALIDATION_STATUS
                FROM knowledge_concepts
                WHERE CONCEPT_ID = %s
            """, (concept_id,))
            
            concept = cursor.fetchone()
            if not concept:
                raise Exception(f"Concept {concept_id} not found")
            
            result = {
                'concept_id': concept[0],
                'concept_name': concept[1],
                'concept_type': concept[2],
                'description': concept[3],
                'category': concept[4],
                'confidence': float(concept[5]) if concept[5] else 0.0,
                'validation_status': concept[6],
                'outgoing_relationships': [],
                'incoming_relationships': []
            }
            
            # Get outgoing relationships
            cursor.execute("""
                SELECT RELATIONSHIP_ID, TARGET_CONCEPT_ID, RELATIONSHIP_TYPE,
                       RELATIONSHIP_STRENGTH, CONFIDENCE
                FROM knowledge_graph
                WHERE SOURCE_CONCEPT_ID = %s
            """, (concept_id,))
            
            for row in cursor.fetchall():
                result['outgoing_relationships'].append({
                    'relationship_id': row[0],
                    'target_concept_id': row[1],
                    'relationship_type': row[2],
                    'strength': float(row[3]) if row[3] else 0.0,
                    'confidence': float(row[4]) if row[4] else 0.0
                })
            
            # Get incoming relationships
            cursor.execute("""
                SELECT RELATIONSHIP_ID, SOURCE_CONCEPT_ID, RELATIONSHIP_TYPE,
                       RELATIONSHIP_STRENGTH, CONFIDENCE
                FROM knowledge_graph
                WHERE TARGET_CONCEPT_ID = %s
            """, (concept_id,))
            
            for row in cursor.fetchall():
                result['incoming_relationships'].append({
                    'relationship_id': row[0],
                    'source_concept_id': row[1],
                    'relationship_type': row[2],
                    'strength': float(row[3]) if row[3] else 0.0,
                    'confidence': float(row[4]) if row[4] else 0.0
                })
            
            return result
            
        except Exception as e:
            raise Exception(f"Failed to get concept with graph: {e}")
        finally:
            cursor.close()
            conn.close()
    
    def get_statistics(self) -> Dict:
        """
        Get knowledge base statistics
        
        Returns:
            Dict: System statistics
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Count concepts
            cursor.execute("SELECT COUNT(*) FROM knowledge_concepts")
            concept_count = cursor.fetchone()[0]
            
            # Count relationships
            cursor.execute("SELECT COUNT(*) FROM knowledge_graph")
            relationship_count = cursor.fetchone()[0]
            
            # Count by type
            cursor.execute("""
                SELECT CONCEPT_TYPE, COUNT(*) 
                FROM knowledge_concepts 
                GROUP BY CONCEPT_TYPE
            """)
            type_counts = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Count pending validations
            cursor.execute("""
                SELECT COUNT(*) FROM knowledge_validation 
                WHERE STATUS = 'PENDING'
            """)
            pending_validations = cursor.fetchone()[0]
            
            return {
                'total_concepts': concept_count,
                'total_relationships': relationship_count,
                'concepts_by_type': type_counts,
                'pending_validations': pending_validations
            }
            
        except Exception as e:
            raise Exception(f"Failed to get statistics: {e}")
        finally:
            cursor.close()
            conn.close()


# Quick start example
if __name__ == "__main__":
    # Initialize API
    kb = KnowledgeBaseAPI()
    
    # Create a concept
    print("Creating knowledge concept...")
    concept = kb.create_concept(
        concept_name="OceanBase CE 4.5.0",
        concept_type="FACT",
        description="OceanBase Community Edition v4.5.0 with VECTOR type support",
        category="database",
        confidence=0.95,
        tags=["oceanbase", "vector", "database"]
    )
    print(f"Created concept: {concept}")
    
    # Get statistics
    print("\nKnowledge base statistics:")
    stats = kb.get_statistics()
    print(json.dumps(stats, indent=2))
