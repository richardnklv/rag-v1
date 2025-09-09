"""
Test Hybrid Search
"""

from hybrid_search import hybrid_search

def test_antimatter_query():
    """Test hybrid search with antimatter query."""
    
    print("🔬 Testing Hybrid Search: BM25 + ChromaDB")
    print("=" * 50)
    
    query = "antimatter physics"
    print(f"🎯 Query: '{query}'")
    print("-" * 30)
    
    # Run hybrid search
    results = hybrid_search(query, top_k=3)
    
    # Display BM25 results
    print("\n📊 BM25 Keyword Results:")
    for i, result in enumerate(results["bm25"], 1):
        print(f"  {i}. {result['filename']} (score: {result['score']:.2f})")
        print(f"     {result['text'][:100]}...\n")
    
    # Display ChromaDB results
    print("🔍 ChromaDB Semantic Results:")
    for i, result in enumerate(results["chroma"], 1):
        print(f"  {i}. {result['filename']} (distance: {result['distance']:.3f})")
        print(f"     {result['text'][:100]}...\n")
    
    # Display weighted combination results
    print("⚖️ Weighted Combination Results:")
    for i, (filename, score) in enumerate(results["weighted_combination"], 1):
        print(f"  {i}. {filename} (final score: {score:.3f})")
        print(f"     Combined ranking based on BM25 + ChromaDB weights\n")

def test_filtered_search():
    """Test hybrid search with metadata filters."""
    
    print("\n" + "=" * 60)
    print("🔍 Testing Filtered Search")
    print("=" * 60)
    
    query = "antimatter physics"
    
    # Test filename filter
    print(f"\n🎯 Query: '{query}' | Filter: Only 'antimatter' files")
    print("-" * 50)
    
    results = hybrid_search(query, top_k=3, filename_filter="antimatter")
    
    print("📋 Filtered Results:")
    for i, (filename, score) in enumerate(results["weighted_combination"], 1):
        print(f"  {i}. {filename} (final score: {score:.3f})")
    
    # Test chunk range filter
    print(f"\n🎯 Query: '{query}' | Filter: Only chunks 1-3")
    print("-" * 50)
    
    results2 = hybrid_search(query, top_k=3, chunk_range=(1, 3))
    
    print("📋 Chunk-Filtered Results:")
    for i, (filename, score) in enumerate(results2["weighted_combination"], 1):
        print(f"  {i}. {filename} (final score: {score:.3f})")

if __name__ == "__main__":
    test_antimatter_query()
    test_filtered_search()
