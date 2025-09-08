"""
Test the simple semantic    # Initialize chunker - no size constraints, pure semantic
    chunker = SimpleSemanticChunker(
        similarity_threshold=0.3  # Lower threshold = fewer breaks, better topic grouping
    )er - no LlamaIndex dependencies
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chunking.simple_semantic_chunker import SemanticChunker


def test_simple_chunker():
    """Test the dependency-free semantic chunker."""
    
    print("Testing Simple Semantic Chunker")
    print("=" * 50)
    
    # Test text with clear topic boundaries
    test_text = """
    Artificial intelligence is transforming modern technology. Machine learning algorithms can process vast datasets efficiently. 
    Neural networks learn complex patterns through training. Deep learning has achieved breakthrough results in many domains.
    
    Environmental conservation is crucial for our planet's future. Deforestation threatens biodiversity worldwide. 
    Renewable energy sources offer sustainable alternatives. Solar and wind power are becoming more cost-effective.
    
    Financial markets reflect economic uncertainty today. Stock prices fluctuated significantly during trading. 
    Cryptocurrency values remain highly volatile. Investors seek stable investment opportunities.
    """
    
    # Initialize chunker
    chunker = SemanticChunker(threshold=0.2)
    
    # Create semantic chunks
    chunks = chunker.chunk(test_text)
    
    # Display results
    print(f"\nCreated {len(chunks)} semantic chunks:")
    print("-" * 40)
    
    for i, chunk in enumerate(chunks):
        print(f"\nChunk {i + 1}:")
        print(f"  Characters: {len(chunk)}")
        print(f"  Words: {len(chunk.split())}")
        print(f"  Preview: {chunk.strip()[:150]}...")
    
    return chunks


def test_with_single_topic():
    """Test chunker with single topic text."""
    
    print("\n" + "=" * 50)
    print("Testing Single Topic (Should have fewer breaks)")
    print("=" * 50)
    
    single_topic_text = """
    Machine learning is a powerful branch of artificial intelligence. It enables computers to learn patterns from data. 
    Supervised learning uses labeled examples for training. Unsupervised learning finds hidden structures in data.
    Reinforcement learning optimizes actions through rewards. Deep learning uses neural networks with multiple layers.
    These techniques have revolutionized computer vision and natural language processing.
    """
    
    chunker = SemanticChunker(threshold=0.2)
    chunks = chunker.chunk(single_topic_text)
    
    print(f"\nSingle topic result: {len(chunks)} chunks")
    for i, chunk in enumerate(chunks):
        print(f"  Chunk {i + 1}: {len(chunk)} chars")


if __name__ == "__main__":
    test_simple_chunker()
    test_with_single_topic()
