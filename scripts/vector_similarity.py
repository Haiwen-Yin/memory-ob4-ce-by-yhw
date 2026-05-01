#!/usr/bin/env python3
"""
OceanBase CE Memory System - Vector Similarity Calculator

Calculates cosine similarity between vectors using NumPy.
This script provides the application-layer vector search capability
for OceanBase CE 4.x memory system where native VECTOR type is not available.

Usage:
    python3 vector_similarity.py --query "text to search" --threshold 0.7
    
Or import as module:
    from scripts.vector_similarity import cosine_similarity, find_similar_nodes
"""

import sys
import json
import argparse
from typing import List, Dict, Any, Optional


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors.
    
    Args:
        vec_a: First vector as list of floats
        vec_b: Second vector as list of floats
    
    Returns:
        Cosine similarity score (0.0 to 1.0)
    """
    try:
        import numpy as np
        
        a = np.array(vec_a, dtype=np.float64)
        b = np.array(vec_b, dtype=np.float64)
        
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        similarity = dot_product / (norm_a * norm_b)
        return round(float(similarity), 6)
    except ImportError:
        # Fallback without numpy - basic implementation
        def sum_sq(lst):
            return sum(x*x for x in lst)
        
        dot_prod = sum(a*b for a, b in zip(vec_a, vec_b))
        norm_a = sum_sq(vec_a)**0.5
        norm_b = sum_sq(vec_b)**0.5
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return round(dot_prod / (norm_a * norm_b), 6)


def embedding_to_text(embedding: List[float]) -> str:
    """Convert embedding list to TEXT representation for storage."""
    return json.dumps([round(x, 6) for x in embedding], separators=(',', ':'))


def text_to_embedding(text: str) -> List[float]:
    """Parse TEXT representation back to embedding list."""
    return [float(x) for x in json.loads(text)]


def find_similar_nodes(
    target_embedding: List[float],
    threshold: float = 0.7,
    max_results: int = 10,
    ob_host: str = "localhost",
    ob_user: str = "root@sys",
    ob_pass: str = "",
    ob_port: int = 2881
) -> List[Dict[str, Any]]:
    """
    Find nodes similar to target embedding using application-layer calculation.
    
    Args:
        target_embedding: Target vector as list of floats
        threshold: Minimum similarity score to include (default: 0.7)
        max_results: Maximum number of results to return (default: 10)
        ob_host: OceanBase host address
        ob_user: OceanBase user@tenant format
        ob_pass: OceanBase password
        ob_port: OceanBase port (default: 2881)
    
    Returns:
        List of similar nodes with their similarity scores
    
    Note: This requires oceanbase client to be installed and configured.
    """
    # Step 1: Fetch all embeddings from OceanBase CE
    cmd = f"obclient -h{ob_host} -P{ob_port} -u{ob_user} -p{ob_pass} " \
          f"-e \"SELECT node_id, node_type, embedding FROM memory_nodes WHERE embedding IS NOT NULL\""
    
    try:
        import subprocess
        result = subprocess.run(
            cmd.split(),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            print(f"Error querying OceanBase: {result.stderr}", file=sys.stderr)
            return []
    except Exception as e:
        print(f"Failed to connect to OceanBase: {e}", file=sys.stderr)
        return []
    
    # Step 2: Parse and calculate similarities in Python
    similar_nodes = []
    for line in result.stdout.strip().split('\n'):
        if not line or line.startswith('+') or 'node_id' in line.lower():
            continue
        
        parts = line.split('|')
        if len(parts) >= 3 and parts[2]:
            try:
                node_id = int(parts[0])
                node_type = parts[1]
                embedding = text_to_embedding(parts[2].strip())
                
                similarity = cosine_similarity(target_embedding, embedding)
                
                if similarity >= threshold:
                    similar_nodes.append({
                        'node_id': node_id,
                        'node_type': node_type,
                        'similarity': round(similarity, 4)
                    })
            except (ValueError, TypeError):
                continue
    
    # Step 3: Sort by similarity descending and return top N results
    similar_nodes.sort(key=lambda x: x['similarity'], reverse=True)
    
    return similar_nodes[:max_results]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Calculate vector similarity for OceanBase CE memory system'
    )
    parser.add_argument('--vec-a', type=str, help='First vector (JSON array or comma-separated)')
    parser.add_argument('--vec-b', type=str, help='Second vector (JSON array or comma-separated)')
    parser.add_argument('--search', action='store_true', help='Search mode - find similar nodes in OceanBase')
    parser.add_argument('--threshold', type=float, default=0.7, help='Similarity threshold (default: 0.7)')
    
    args = parser.parse_args()
    
    def parse_vector(text):
        if text.startswith('['):
            return json.loads(text)
        return [float(x.strip()) for x in text.split(',')]
    
    if args.vec_a and args.vec_b:
        vec_a = parse_vector(args.vec_a)
        vec_b = parse_vector(args.vec_b)
        
        similarity = cosine_similarity(vec_a, vec_b)
        print(f"Cosine Similarity: {similarity}")
        
    elif args.search:
        # Search mode requires target_embedding to be provided separately
        print("Search mode requires --target-embedding option")
        sys.exit(1)
    
    else:
        parser.print_help()
