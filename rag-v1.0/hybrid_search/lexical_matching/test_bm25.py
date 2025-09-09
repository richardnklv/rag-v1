"""
Test BM25 Keyword Search
Test the BM25 search functionality with various queries.
"""

from bm25 import bm25_search


def test_bm25_search():
    """Test BM25 search with different queries."""
    
    print("🔍 Testing BM25 Keyword Search")
    print("=" * 50)
    
    # Test queries
    test_queries = [
        "antimatter physics",
        "machine learning algorithms", 
        "quantum mechanics",
        "detector design",
        "electron beam"
    ]
    
    for query in test_queries:
        print(f"\n🎯 Query: '{query}'")
        print("-" * 40)
        
        try:
            results = bm25_search(query, top_k=3)
            
            if results:
                print(f"✅ Found {len(results)} results:")
                
                for i, result in enumerate(results, 1):
                    print(f"\n  📄 Result {i}:")
                    print(f"     Score: {result['score']:.3f}")
                    print(f"     File: {result['filename']}")
                    print(f"     Chunk: {result['chunk_number']}")
                    print(f"     Preview: {result['text'][:100]}...")
            else:
                print("❌ No results found")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n{'='*50}")
    print("🎉 BM25 testing complete!")


def compare_queries():
    """Compare different query styles."""
    
    print("\n🔬 Comparing Query Styles")
    print("=" * 50)
    
    # Compare exact vs. related terms
    query_pairs = [
        ("antimatter", "antiparticle positron"),
        ("detector", "sensor measurement"),
        ("physics", "physical science")
    ]
    
    for exact_query, related_query in query_pairs:
        print(f"\nExact: '{exact_query}' vs Related: '{related_query}'")
        print("-" * 60)
        
        exact_results = bm25_search(exact_query, top_k=2)
        related_results = bm25_search(related_query, top_k=2)
        
        print(f"Exact matches: {len(exact_results)}")
        for r in exact_results:
            print(f"  - {r['filename']} (score: {r['score']:.2f})")
        
        print(f"Related matches: {len(related_results)}")
        for r in related_results:
            print(f"  - {r['filename']} (score: {r['score']:.2f})")


if __name__ == "__main__":
    test_bm25_search()
    compare_queries()
