"""
Load processed PDF chunks into ChromaDB
"""

import chromadb
import json
import os

def load_chunks_to_chromadb():
    """Load all processed chunks into ChromaDB."""
    
    # Use absolute path to eliminate path confusion bullshit
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, "chroma_db")
    
    # Create ChromaDB client with persistent storage
    client = chromadb.PersistentClient(path=db_path)
    collection = client.get_or_create_collection("scientific_papers")
    
    # Load processed chunks
    chunks_dir = "../../preprocessing/processed_chunks"
    all_ids = []
    all_documents = []
    all_metadatas = []
    
    print("Loading chunks from JSON files...")
    
    for json_file in os.listdir(chunks_dir):
        if json_file.endswith('_chunks.json'):
            print(f"Processing {json_file}")
            
            with open(os.path.join(chunks_dir, json_file), 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Add each chunk with unique ID
            for i, chunk in enumerate(data['chunks']):
                chunk_id = f"{data['filename']}_chunk_{i+1}"
                all_ids.append(chunk_id)
                all_documents.append(chunk)
                all_metadatas.append({
                    "filename": data['filename'],
                    "chunk_number": i+1,
                    "total_chunks": data['chunk_count']
                })
    
    # Add all chunks to ChromaDB
    print(f"\nAdding {len(all_documents)} chunks to ChromaDB...")
    
    collection.add(
        ids=all_ids,
        documents=all_documents,
        metadatas=all_metadatas
    )
    
    print(f"✅ Successfully added {len(all_documents)} chunks to ChromaDB!")
    print(f"Database saved to: {db_path}")
    
    # # Test with a simple query
    # print("\n🔍 Testing with sample query...")
    # results = collection.query(
    #     query_texts=["machine learning algorithms"],
    #     n_results=3
    # )
    
    # print("Top 3 results:")
    # for i, doc in enumerate(results['documents'][0]):
    #     metadata = results['metadatas'][0][i]
    #     print(f"  {i+1}. {metadata['filename']} - Chunk {metadata['chunk_number']}")
    #     print(f"     {doc[:100]}...")
    #     print()


if __name__ == "__main__":
    load_chunks_to_chromadb()
