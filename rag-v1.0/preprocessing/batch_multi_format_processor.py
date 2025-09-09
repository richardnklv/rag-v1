"""
Multi-Format Batch Processor
Processes both PDFs and EPUBs using existing loaders and semantic chunker.
"""

import os
import sys
import json

# Add the preprocessing directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from normalization.pdf_loader import PyMuPDFPreprocessor
from normalization.epub_loader import PyMuPDFEpubPreprocessor
from chunking.simple_semantic_chunker import SemanticChunker


def process_all_documents(pdf_input_path=None, epub_input_path=None, output_path=None):
    """Process both PDFs and EPUBs using existing components."""
    
    # Setup paths with defaults
    if pdf_input_path is None:
        pdf_input_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data/arxiv_downloads")
    
    if epub_input_path is None:
        epub_input_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data/project_gutenberg_books")
    
    if output_path is None:
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "processed_chunks")
    
    os.makedirs(output_path, exist_ok=True)
    
    print("🚀 Processing Multi-Format Documents...")
    print(f"PDF Input: {pdf_input_path}")
    print(f"EPUB Input: {epub_input_path}")
    print(f"Output: {output_path}")
    
    # Initialize components
    chunker = SemanticChunker()
    
    # Process PDFs
    print("\n📄 Processing PDFs...")
    pdf_preprocessor = PyMuPDFPreprocessor(data_directory=pdf_input_path)
    pdf_documents = pdf_preprocessor.process_pdfs(limit=50)  # Limit for faster processing
    
    print(f"✅ Loaded {len(pdf_documents)} PDF documents")
    
    # Process EPUBs
    print("\n📚 Processing EPUBs...")
    epub_preprocessor = PyMuPDFEpubPreprocessor(data_directory=epub_input_path)
    epub_documents = epub_preprocessor.process_epubs(limit=20)  # Limit for faster processing
    
    print(f"✅ Loaded {len(epub_documents)} EPUB documents")
    
    # Combine all documents
    all_documents = pdf_documents + epub_documents
    print(f"\n📊 Total documents to process: {len(all_documents)}")
    
    # Process each document
    total_chunks = 0
    
    for i, doc in enumerate(all_documents, 1):
        filename = doc['filename']
        text = doc['text']
        
        print(f"\n🔄 Processing {i}/{len(all_documents)}: {filename}")
        
        # Get file extension to determine format
        file_ext = os.path.splitext(filename)[1].lower()
        
        # Chunk the document
        try:
            chunks = chunker.chunk_text(text)
            print(f"   Generated {len(chunks)} chunks")
            
            # Save each chunk
            for j, chunk in enumerate(chunks, 1):
                chunk_data = {
                    "filename": filename,
                    "format": file_ext[1:].upper(),  # Remove dot and uppercase
                    "chunk_number": j,
                    "total_chunks": len(chunks),
                    "text": chunk,
                    "char_count": len(chunk)
                }
                
                # Create filename for this chunk
                chunk_filename = f"{os.path.splitext(filename)[0]}_chunk_{j:03d}.json"
                chunk_path = os.path.join(output_path, chunk_filename)
                
                # Save chunk
                with open(chunk_path, 'w', encoding='utf-8') as f:
                    json.dump(chunk_data, f, indent=2, ensure_ascii=False)
            
            total_chunks += len(chunks)
            
        except Exception as e:
            print(f"   ❌ Error processing {filename}: {e}")
            continue
    
    print(f"\n✅ Processing complete!")
    print(f"📊 Summary:")
    print(f"   - PDFs processed: {len(pdf_documents)}")
    print(f"   - EPUBs processed: {len(epub_documents)}")
    print(f"   - Total documents: {len(all_documents)}")
    print(f"   - Total chunks created: {total_chunks}")
    print(f"   - Output directory: {output_path}")


def main():
    """Run the multi-format processing pipeline."""
    process_all_documents()


if __name__ == "__main__":
    main()
