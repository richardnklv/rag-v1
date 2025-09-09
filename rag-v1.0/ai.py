import os
import sys
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Change to hybrid_search directory to fix path issues
script_dir = os.path.dirname(os.path.abspath(__file__))
hybrid_search_dir = os.path.join(script_dir, 'hybrid_search')
os.chdir(hybrid_search_dir)

# Add paths
sys.path.append('.')
sys.path.append('..')

from hybrid_search import hybrid_search

def call_openrouter_api(prompt):
    """Call OpenRouter API directly - fuck LlamaIndex"""
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "gryphe/mythomax-l2-13b",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 512
        }
    )
    
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        raise Exception(f"OpenRouter error: {response.status_code} - {response.text}")

def expand_query(original_query, num_variations=3):
    """
    Generate multiple query variations using OpenRouter for better retrieval.
    
    Args:
        original_query (str): The original user query
        num_variations (int): Number of query variations to generate
        
    Returns:
        list: List of expanded/rewritten queries including the original
    """
    expansion_prompt = f"""
You are a query expansion expert for technical document search. Given a user query, generate {num_variations} alternative phrasings that would help find relevant technical documents.

Original query: "{original_query}"

Generate {num_variations} alternative queries that:
1. Use different technical terminology
2. Include related concepts or synonyms
3. Rephrase for different search angles
4. Keep the same intent but vary the approach

Format: Return ONLY the alternative queries, one per line, no numbering or extra text.
"""
    
    try:
        response = call_openrouter_api(expansion_prompt)
        expanded_queries = [original_query]  # Always include original
        
        # Parse the response and add variations
        for line in response.strip().split('\n'):
            line = line.strip()
            if line and line not in expanded_queries:
                expanded_queries.append(line)
                
        return expanded_queries[:num_variations + 1]  # Limit to requested number + original
        
    except Exception as e:
        print(f"⚠️ Query expansion failed: {e}")
        return [original_query]  # Fallback to original query

def rag_query(user_query, top_k=3, use_query_expansion=True):
    """
    Complete RAG pipeline: Retrieve relevant chunks + Generate answer.
    
    Args:
        user_query (str): User's question
        top_k (int): Number of chunks to retrieve
        use_query_expansion (bool): Whether to use query expansion
        
    Returns:
        dict: Contains search results and generated answer
    """
    print(f"🔍 Processing query: '{user_query}'")
    
    # Step 1: Query expansion (optional)
    if use_query_expansion:
        print("🔄 Expanding query for better retrieval...")
        expanded_queries = expand_query(user_query, num_variations=2)
        print(f"📝 Generated {len(expanded_queries)} query variations:")
        for i, q in enumerate(expanded_queries):
            print(f"  {i+1}. {q}")
    else:
        expanded_queries = [user_query]
    
    # Step 2: Search with all query variations and combine results
    all_results = {'bm25': [], 'chroma': [], 'weighted_combination': [], 'final_scores': {}}
    
    for query in expanded_queries:
        search_results = hybrid_search(query, top_k=top_k)
        
        # Merge results (avoiding duplicates)
        for bm25_result in search_results['bm25']:
            if not any(r['filename'] == bm25_result['filename'] for r in all_results['bm25']):
                all_results['bm25'].append(bm25_result)
                
        for chroma_result in search_results['chroma']:
            if not any(r['filename'] == chroma_result['filename'] for r in all_results['chroma']):
                all_results['chroma'].append(chroma_result)
        
        # Merge weighted combinations and final scores
        for filename, score in search_results['weighted_combination']:
            if filename not in all_results['final_scores']:
                all_results['final_scores'][filename] = score
                all_results['weighted_combination'].append((filename, score))
            else:
                # Take the best score if filename appears multiple times
                if score > all_results['final_scores'][filename]:
                    all_results['final_scores'][filename] = score
                    # Update in weighted_combination
                    all_results['weighted_combination'] = [(f, s) if f != filename else (f, score) 
                                                         for f, s in all_results['weighted_combination']]
    
    # Re-sort weighted combination by score
    all_results['weighted_combination'].sort(key=lambda x: x[1], reverse=True)
    
    # Step 3: Build context from combined weighted results
    context_chunks = []
    for filename, _ in all_results['weighted_combination'][:top_k]:  # Use _ for unused score
        # Find the actual chunk text from either BM25 or ChromaDB results
        chunk_text = None
        
        # Check BM25 results first
        for result in all_results['bm25']:
            if result['filename'] == filename:
                chunk_text = result['text']
                break
        
        # If not found in BM25, check ChromaDB results
        if chunk_text is None:
            for result in all_results['chroma']:
                if result['filename'] == filename:
                    chunk_text = result['text']
                    break
        
        if chunk_text:
            context_chunks.append(f"Source: {filename}\n{chunk_text}")
    
    # Step 3: Create context for LLM
    context = "\n\n---\n\n".join(context_chunks)
    
    # Step 4: Build prompt
    prompt = f"""Based on the following scientific documents, answer the user's question accurately and concisely.

CONTEXT:
{context}

QUESTION: {user_query}

INSTRUCTIONS:
- Use only information from the provided context
- Cite the source documents when possible
- If the context doesn't contain enough information, say so
- Be precise and scientific in your response

ANSWER:"""

    print(f"📚 Retrieved {len(context_chunks)} relevant chunks")
    
    # Step 4.5: Create source attribution with confidence scores - FIXED VERSION
    def create_source_attribution(search_results, top_k):
        """Create source attribution using the SAME normalized scores from hybrid_search."""
        attribution = []
        
        # Get the already-normalized scores from hybrid_search
        bm25_normalized = {}
        chroma_normalized = {}
        
        # Extract normalized scores from hybrid_search results (these are already calculated correctly)
        for result in search_results['bm25']:
            # Re-normalize BM25 scores using the same logic as hybrid_search
            bm25_scores = [r['score'] for r in search_results['bm25']]
            if bm25_scores:
                max_score = max(bm25_scores)
                min_score = min(bm25_scores)
                if max_score == min_score:
                    bm25_normalized[result['filename']] = 1.0
                else:
                    bm25_normalized[result['filename']] = (result['score'] - min_score) / (max_score - min_score)
        
        for result in search_results['chroma']:
            # Re-normalize ChromaDB distances using the same logic as hybrid_search
            chroma_distances = [r['distance'] for r in search_results['chroma']]
            if chroma_distances:
                max_distance = max(chroma_distances)
                min_distance = min(chroma_distances)
                if max_distance == min_distance:
                    chroma_normalized[result['filename']] = 1.0
                else:
                    similarity = 1 - ((result['distance'] - min_distance) / (max_distance - min_distance))
                    chroma_normalized[result['filename']] = similarity
        
        # Process each source in weighted combination (these scores are already correct!)
        for filename, weighted_score in search_results['weighted_combination'][:top_k]:
            source_info = {
                "source": filename,
                "weighted_confidence": round(weighted_score, 3),  # This is already the correct weighted score
                "methods": []
            }
            
            # Add BM25 confidence if available
            if filename in bm25_normalized:
                source_info["methods"].append({
                    "method": "BM25_keyword",
                    "confidence": round(bm25_normalized[filename], 3)
                })
            
            # Add ChromaDB confidence if available  
            if filename in chroma_normalized:
                source_info["methods"].append({
                    "method": "ChromaDB_semantic",
                    "confidence": round(chroma_normalized[filename], 3)
                })
            
            attribution.append(source_info)
        
        return attribution
    
    source_attribution = create_source_attribution(all_results, top_k)
    
    # Step 5: Generate answer using direct OpenRouter API
    try:
        answer = call_openrouter_api(prompt)
        
        return {
            "query": user_query,
            "expanded_queries": expanded_queries if use_query_expansion else [user_query],
            "answer": answer,
            "search_results": all_results,
            "context_used": context_chunks,
            "sources": [filename for filename, _ in all_results['weighted_combination'][:top_k]],
            "source_attribution": source_attribution  # NEW: Source attribution with confidence scores
        }
    
    except Exception as e:
        return {
            "query": user_query,
            "expanded_queries": expanded_queries if use_query_expansion else [user_query],
            "error": f"Error generating response: {e}",
            "search_results": all_results
        }

def main():
    """Test the complete RAG system."""
    
    # Test queries
    test_queries = [
        "Can you give me a brief explanation of antimatter theory?",
        "What are the key principles of quantum physics?",
        "How do particle accelerators work?"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        result = rag_query(query)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"🎯 Query: {result['query']}")
            
            # NEW: Display expanded queries if used
            if len(result.get('expanded_queries', [])) > 1:
                print(f"🔄 Query Expansion:")
                for i, expanded in enumerate(result['expanded_queries']):
                    marker = "📝" if i == 0 else "🔀"
                    label = "Original" if i == 0 else f"Variation {i}"
                    print(f"     {marker} {label}: {expanded}")
            
            print(f"📝 Answer: {result['answer']}")
            print(f"📚 Sources: {', '.join(result['sources'])}")
            
            # NEW: Display source attribution with confidence scores
            print(f"\n🔍 Source Attribution with Confidence Scores:")
            for i, source in enumerate(result['source_attribution'], 1):
                print(f"  {i}. {source['source']}")
                print(f"     Weighted Confidence: {source['weighted_confidence']}")
                for method in source['methods']:
                    print(f"     • {method['method']}: {method['confidence']}")
                print()

if __name__ == "__main__":
    main()