"""
Hybrid Search: BM25 + ChromaDB with Weighted Combination
"""

from lexical_matching.bm25 import bm25_search
from chroma.chroma_query import chroma_search

# WEIGHT FOR BM25 VS CHROMADB (0.0 = ALL CHROMADB, 1.0 = ALL BM25)
BM25_WEIGHT = 0.5

def normalize_bm25_scores(results):
    """Normalize BM25 scores to 0-1 range."""
    if not results:
        return {}
    
    scores = [r['score'] for r in results]
    max_score = max(scores)
    min_score = min(scores)
    
    normalized = {}
    for result in results:
        if max_score == min_score:
            normalized[result['filename']] = 1.0
        else:
            normalized[result['filename']] = (result['score'] - min_score) / (max_score - min_score)
    
    return normalized

def normalize_chroma_distances(results):
    """Normalize ChromaDB distances to 0-1 range (lower distance = higher score)."""
    if not results:
        return {}
    
    distances = [r['distance'] for r in results]
    max_distance = max(distances)
    min_distance = min(distances)
    
    normalized = {}
    for result in results:
        if max_distance == min_distance:
            normalized[result['filename']] = 1.0
        else:
            # Convert distance to similarity score (invert)
            similarity = 1 - ((result['distance'] - min_distance) / (max_distance - min_distance))
            normalized[result['filename']] = similarity
    
    return normalized

def combine_weighted_results(bm25_results, chroma_results, bm25_weight=BM25_WEIGHT):
    """Combine and rank results using weighted scores."""
    
    # Normalize scores
    bm25_normalized = normalize_bm25_scores(bm25_results)
    chroma_normalized = normalize_chroma_distances(chroma_results)
    
    # Get all unique documents
    all_docs = set(bm25_normalized.keys()) | set(chroma_normalized.keys())
    
    # Calculate weighted scores
    final_scores = {}
    chroma_weight = 1 - bm25_weight
    
    for doc in all_docs:
        bm25_score = bm25_normalized.get(doc, 0)
        chroma_score = chroma_normalized.get(doc, 0)
        
        final_scores[doc] = (bm25_score * bm25_weight) + (chroma_score * chroma_weight)
    
    # Sort by final score (highest first)
    ranked_docs = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
    
    return ranked_docs, final_scores

def hybrid_search(query, top_k=5, filename_filter=None, chunk_range=None, min_text_length=None):
    """
    Perform hybrid search using both BM25 and ChromaDB with weighted combination.
    
    Args:
        query (str): Search query
        top_k (int): Number of results from each method
        filename_filter (str): Optional filter to only include files containing this string
        chunk_range (tuple): Optional (min_chunk, max_chunk) to filter by chunk numbers
        min_text_length (int): Optional minimum text length to filter short chunks
        
    Returns:
        dict: Results from both search methods + weighted combination
    """
    # Get BM25 keyword results
    bm25_results = bm25_search(query, top_k * 2)  # Get more results for filtering
    
    # Get ChromaDB semantic results
    chroma_results = chroma_search(query, top_k * 2)  # Get more results for filtering
    
    # Apply metadata filters
    def apply_filters(results):
        filtered = results
        
        if filename_filter:
            filtered = [r for r in filtered if filename_filter.lower() in r['filename'].lower()]
        
        if chunk_range:
            min_chunk, max_chunk = chunk_range
            filtered = [r for r in filtered if min_chunk <= r['chunk_number'] <= max_chunk]
        
        if min_text_length:
            filtered = [r for r in filtered if len(r['text']) >= min_text_length]
        
        return filtered[:top_k]  # Return only top_k after filtering
    
    # Apply filters to both result sets
    bm25_filtered = apply_filters(bm25_results)
    chroma_filtered = apply_filters(chroma_results)
    
    # Combine with weights
    ranked_docs, final_scores = combine_weighted_results(bm25_filtered, chroma_filtered)
    
    return {
        "bm25": bm25_filtered,
        "chroma": chroma_filtered,
        "weighted_combination": ranked_docs[:top_k],
        "final_scores": final_scores
    }
