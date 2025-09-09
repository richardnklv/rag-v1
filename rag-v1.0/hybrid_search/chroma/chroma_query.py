"""
Simple ChromaDB Query Function
Uses the same logic as test_chromadb.py but as a reusable function.
"""

import chromadb
import os

def chroma_search(query, top_k=5):
    """
    Search ChromaDB for relevant chunks using the same logic as test_chromadb.py.
    
    Args:
        query (str): Search query
        top_k (int): Number of results to return
        
    Returns:
        list: Results with metadata and distances
    """
    # Use absolute path to eliminate path confusion bullshit
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, "chroma_db")
    
    # Connect to existing database with absolute path
    client = chromadb.PersistentClient(path=db_path)
    collection = client.get_or_create_collection("scientific_papers")
    
    # Check how many documents we have
    count = collection.count()
    print(f"Available collections: ['scientific_papers']")
    print(f"Database contains: {count} chunks")
    
    if count == 0:
        print("No collections found in database!")
        return []
    
    # Search for most relevant chunks (same as test_chromadb.py)
    results = collection.query(
        query_texts=[query],
        n_results=top_k
    )
    
    # Format results in the expected format for hybrid search
    formatted_results = []
    if results['documents'][0]:
        for i, (doc, metadata, distance) in enumerate(zip(
            results['documents'][0],
            results['metadatas'][0], 
            results['distances'][0]
        )):
            formatted_results.append({
                "text": doc,
                "filename": metadata['filename'],
                "chunk_number": metadata['chunk_number'],
                "distance": distance
            })
    
    return formatted_results
