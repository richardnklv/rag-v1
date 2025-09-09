"""
Simple BM25 Search
"""

import json
import os
from rank_bm25 import BM25Okapi

# Load documents once
documents = []
metadata = []

def _load_data():
    """Load chunks for BM25."""
    global documents, metadata
    
    if documents:  # Already loaded
        return
    
    chunks_path = os.path.join("..", "preprocessing", "processed_chunks")
    
    for json_file in os.listdir(chunks_path):
        if json_file.endswith('_chunks.json'):
            with open(os.path.join(chunks_path, json_file), 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for i, chunk in enumerate(data['chunks']):
                documents.append(chunk.lower().split())  # Tokenize
                metadata.append({
                    "filename": data['filename'],
                    "chunk_number": i + 1,
                    "text": chunk
                })

def bm25_search(query, top_k=5):
    """
    BM25 keyword search.
    
    Args:
        query (str): Search query
        top_k (int): Number of results
        
    Returns:
        list: Results with scores and metadata
    """
    _load_data()
    
    # Build index
    bm25 = BM25Okapi(documents)
    
    # Search
    tokenized_query = query.lower().split()
    scores = bm25.get_scores(tokenized_query)
    
    # Get top results
    results = []
    scored_docs = [(score, idx) for idx, score in enumerate(scores)]
    scored_docs.sort(reverse=True)
    
    for score, idx in scored_docs[:top_k]:
        if score > 0:
            results.append({
                "score": score,
                "text": metadata[idx]["text"],
                "filename": metadata[idx]["filename"],
                "chunk_number": metadata[idx]["chunk_number"]
            })
    
    return results
