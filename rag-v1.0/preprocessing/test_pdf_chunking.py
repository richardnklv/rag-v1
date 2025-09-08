"""
Test the complete preprocessing pipeline: PDF -> Normalized Text -> Semantic Chunks
"""

import os
import sys

# Add the preprocessing directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from normalization.pdf_loader import PyMuPDFPreprocessor
from chunking.simple_semantic_chunker import SemanticChunker


def test_pdf_to_chunks():
    """Complete pipeline: PDF -> Text -> Chunks"""
    
    print("PDF to Semantic Chunks Pipeline Test")
    print("=" * 50)
    
    # Step 1: Find PDF files
    data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data/arxiv_downloads")
    
    if not os.path.exists(data_path):
        print("No data folder found")
        return
    
    pdf_files = [f for f in os.listdir(data_path) if f.endswith('.pdf')]
    if not pdf_files:
        print("No PDF files found in data folder")
        return
    
    pdf_path = os.path.join(data_path, pdf_files[0])
    print(f"Processing: {pdf_files[0]}")
    
    # Step 2: PDF -> Normalized Text
    print("\nStep 1: PDF -> Normalized Text")
    preprocessor = PyMuPDFPreprocessor(data_directory=data_path)
    documents = preprocessor.process_pdfs(limit=1)  # Process just 1 PDF
    
    if not documents:
        print("Failed to extract text from PDF")
        return
    
    text = documents[0]['text']
    print(f"Extracted {len(text)} characters")
    print(f"Preview: {text[:200]}...")
    
    # Step 3: Text -> Semantic Chunks
    print("\nStep 2: Text -> Semantic Chunks")
    chunker = SemanticChunker(threshold=0.05)  # Lower threshold for technical papers
    chunks = chunker.chunk(text)
    
    print(f"Created {len(chunks)} semantic chunks")
    
    # Step 4: Show results
    print("\nChunking Results:")
    print("-" * 30)
    
    # Save full results to file
    output_file = "chunked_output.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"SEMANTIC CHUNKING RESULTS\n")
        f.write(f"Source: {pdf_files[0]}\n")
        f.write(f"Original text: {len(text)} characters\n")
        f.write(f"Created: {len(chunks)} semantic chunks\n")
        f.write("=" * 80 + "\n\n")
        
        for i, chunk in enumerate(chunks):
            f.write(f"CHUNK {i+1}/{len(chunks)}\n")
            f.write(f"Length: {len(chunk)} chars, {len(chunk.split())} words\n")
            f.write("-" * 50 + "\n")
            f.write(chunk.strip())
            f.write("\n\n" + "=" * 80 + "\n\n")
    
    print(f"Full chunked results saved to: {output_file}")
    
    for i, chunk in enumerate(chunks[:5]):  # Show first 5
        print(f"\nChunk {i+1}:")
        print(f"  Length: {len(chunk)} chars")
        print(f"  Words: {len(chunk.split())} words")
        print(f"  Preview: {chunk.strip()[:150]}...")
    
    if len(chunks) > 5:
        print(f"\n... and {len(chunks) - 5} more chunks")
        print(f"See {output_file} for complete results")
    
    return chunks


if __name__ == "__main__":
    test_pdf_to_chunks()
