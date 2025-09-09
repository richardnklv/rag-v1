"""
Main preprocessing script
Processes PDFs and EPUBs from the dataset and generates semantic chunks.
"""

import os
from batch_multi_format_processor import process_all_documents


def main():
    """Run the complete multi-format preprocessing pipeline."""
    # Set proper input and output paths
    pdf_input_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "arxiv_downloads")
    epub_input_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "project_gutenberg_books")
    output_path = os.path.join(os.path.dirname(__file__), "processed_chunks")
    
    print("🚀 Starting Multi-Format preprocessing pipeline...")
    print(f"PDF Input: {pdf_input_path}")
    print(f"EPUB Input: {epub_input_path}")
    print(f"Output: {output_path}")
    
    # Process both PDFs and EPUBs
    process_all_documents(
        pdf_input_path=pdf_input_path, 
        epub_input_path=epub_input_path, 
        output_path=output_path
    )
    print("✅ Multi-format preprocessing complete!")


if __name__ == "__main__":
    main()
