"""
EPUB-Only Batch Processor
Processes EPUBs to add second format support without touching existing PDF chunks.
"""

import os
import sys
import json

# Add the preprocessing directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from normalization.epub_loader import PyMuPDFEpubPreprocessor
from chunking.simple_semantic_chunker import SemanticChunker


def process_epubs_only(epub_input_path=None, output_path=None, limit=10):
    """Process only EPUBs to add second format support."""
    
    # Setup paths with defaults
    if epub_input_path is None:
        epub_input_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data/project_gutenberg_books")
    
    if output_path is None:
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "processed_chunks")
    
    os.makedirs(output_path, exist_ok=True)
    
    print("📚 Processing EPUBs only (keeping existing PDFs)...")
    print(f"EPUB Input: {epub_input_path}")
    print(f"Output: {output_path}")
    print(f"Limit: {limit} EPUBs")
    
    # Initialize components
    chunker = SemanticChunker()
    epub_preprocessor = PyMuPDFEpubPreprocessor(data_directory=epub_input_path)
    
    # Process EPUBs
    epub_documents = epub_preprocessor.process_epubs(limit=limit)
    print(f"✅ Loaded {len(epub_documents)} EPUB documents")
    
    # Process each EPUB
    total_chunks = 0
    
    for i, doc in enumerate(epub_documents, 1):
        filename = doc['metadata']['file_name']  # EPUB loader uses metadata.file_name
        text = doc['text']
        
        print(f"\n🔄 Processing {i}/{len(epub_documents)}: {filename}")
        
        # Chunk the document
        try:
            chunks = chunker.chunk(text)  # Use 'chunk' method not 'chunk_text'
            print(f"   Generated {len(chunks)} chunks")
            
            # Create document data in the SAME FORMAT as existing PDFs
            document_data = {
                "filename": filename,
                "text_length": len(text),
                "chunk_count": len(chunks),
                "chunks": chunks  # Just the text chunks, same as PDFs
            }
            
            # Create filename for this document (same format as PDFs)
            doc_filename = f"{os.path.splitext(filename)[0]}_chunks.json"
            doc_path = os.path.join(output_path, doc_filename)
            
            # Save document with all chunks (same format as PDFs)
            with open(doc_path, 'w', encoding='utf-8') as f:
                json.dump(document_data, f, indent=2, ensure_ascii=False)
            
            total_chunks += len(chunks)
            
        except Exception as e:
            print(f"   ❌ Error processing {filename}: {e}")
            continue
    
    print(f"\n✅ EPUB processing complete!")
    print(f"📊 Summary:")
    print(f"   - EPUBs processed: {len(epub_documents)}")
    print(f"   - Total new chunks created: {total_chunks}")
    print(f"   - Output directory: {output_path}")


if __name__ == "__main__":
    process_epubs_only()
