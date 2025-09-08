from epub_loader import PyMuPDFEpubPreprocessor

def test_epub_preprocessor():
    """Test the PyMuPDF EPUB preprocessor with sample EPUB files."""
    
    # Initialize preprocessor
    preprocessor = PyMuPDFEpubPreprocessor("../data/project_gutenberg_books")
    
    # Process first 2 EPUB files
    print("Testing PyMuPDF EPUB Preprocessor...")
    documents = preprocessor.process_epubs(limit=2)
    
    print(f"\nProcessed {len(documents)} documents")
    
    # Display results
    for i, doc in enumerate(documents):
        print(f"\n--- Document {i+1} ---")
        print(f"File: {doc['metadata']['file_name']}")
        print(f"Length: {doc['metadata']['text_length']} characters")
        print(f"Preview: {doc['text'][:200]}...")
        print("-" * 50)

if __name__ == "__main__":
    test_epub_preprocessor()
