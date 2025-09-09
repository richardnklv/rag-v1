"""
Simple PDF Batch Processor
Uses existing PDF loader and semantic chunker to process all PDFs.
"""

import os
import sys
import json

# Add the preprocessing directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from normalization.pdf_loader import PyMuPDFPreprocessor
from chunking.simple_semantic_chunker import SemanticChunker


def process_all_pdfs(input_path=None, output_path=None):
    """Process all PDFs using existing components."""
    
    # Setup paths with defaults
    if input_path is None:
        input_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data/arxiv_downloads")
    
    if output_path is None:
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "processed_chunks")
    
    os.makedirs(output_path, exist_ok=True)
    
    # Use existing components
    preprocessor = PyMuPDFPreprocessor(data_directory=input_path)
    chunker = SemanticChunker()
    
    # Get all PDFs
    pdf_files = [f for f in os.listdir(input_path) if f.endswith('.pdf')]
    print(f"Found {len(pdf_files)} PDFs to process")
    
    # Process each PDF
    all_results = []
    
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"[{i}/{len(pdf_files)}] Processing {pdf_file}")
        
        try:
            # Step 1: PDF -> Text (using existing pdf_loader)
            pdf_path = os.path.join(input_path, pdf_file)
            documents = preprocessor.process_single_pdf(pdf_path)
            text = documents[0]['text']
            
            # Step 2: Text -> Chunks (using existing semantic_chunker)
            chunks = chunker.chunk(text)
            
            # Save chunks for this PDF
            result = {
                'filename': pdf_file,
                'text_length': len(text),
                'chunk_count': len(chunks),
                'chunks': chunks
            }
            
            # Save individual file
            output_file = os.path.join(output_path, f"{pdf_file.replace('.pdf', '')}_chunks.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            all_results.append(result)
            print(f"  → {len(chunks)} chunks generated")
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    # Save summary
    summary = {
        'total_pdfs_processed': len(all_results),
        'total_chunks': sum(r['chunk_count'] for r in all_results),
        'files': [{'filename': r['filename'], 'chunks': r['chunk_count']} for r in all_results]
    }
    
    summary_file = os.path.join(output_path, "processing_summary.json")
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\nDone! Processed {len(all_results)} PDFs")
    print(f"Total chunks: {summary['total_chunks']}")
    print(f"Output directory: {output_path}")


if __name__ == "__main__":
    process_all_pdfs()
