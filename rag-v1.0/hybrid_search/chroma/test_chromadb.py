"""
Simple ChromaDB Test
Test the vector database with a specific query about antimatter.
"""

import chromadb
import os

def test_chromadb():
    """Test ChromaDB with antimatter query."""
    
    print("🔍 Testing ChromaDB...")
    
    # Use absolute path to eliminate path confusion bullshit
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, "chroma_db")
    
    # Connect to existing database
    client = chromadb.PersistentClient(path=db_path)
    collection = client.get_or_create_collection("scientific_papers")
    
    # Check how many documents we have
    count = collection.count()
    print(f"📊 Database contains: {count} chunks")
    
    if count == 0:
        print("❌ No documents found! Run load_to_chromadb.py first.")
        return
    
    # Test query about antimatter
    query = "explain to me antimatter in 3 sentences in much detail"
    print(f"\n🎯 Query: '{query}'")
    print("-" * 50)
    
    # Search for most relevant chunks
    results = collection.query(
        query_texts=[query],
        n_results=5  # Get top 5 matches
    )
    
    # Display results
    if results['documents'][0]:
        print(f"✅ Found {len(results['documents'][0])} relevant chunks:\n")
        
        for i, (doc, metadata, distance) in enumerate(zip(
            results['documents'][0],
            results['metadatas'][0], 
            results['distances'][0]
        )):
            print(f"📄 Result {i+1}:")
            print(f"   File: {metadata['filename']}")
            print(f"   Chunk: {metadata['chunk_number']}")
            print(f"   Similarity: {1-distance:.3f}")  # Convert distance to similarity
            print(f"   Content: {doc[:200]}...")
            print()
    else:
        print("❌ No results found!")
    
    # Test another query
    print("\n" + "="*60)
    query2 = "quantum physics experiments"
    print(f"🎯 Second Query: '{query2}'")
    print("-" * 50)
    
    results2 = collection.query(
        query_texts=[query2],
        n_results=3
    )
    
    if results2['documents'][0]:
        print(f"✅ Found {len(results2['documents'][0])} relevant chunks:\n")
        
        for i, (doc, metadata) in enumerate(zip(
            results2['documents'][0],
            results2['metadatas'][0]
        )):
            print(f"📄 Result {i+1}: {metadata['filename']} - {doc[:100]}...")
    
    print(f"\n🎉 ChromaDB is working perfectly!")


if __name__ == "__main__":
    test_chromadb()
