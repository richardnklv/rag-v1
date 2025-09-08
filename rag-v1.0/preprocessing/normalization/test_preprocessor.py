from pdf_loader import PyMuPDFPreprocessor

def test_preprocessor():
    """Test the PyMuPDF preprocessor with sample PDFs."""
    
    # Initialize preprocessor
    preprocessor = PyMuPDFPreprocessor("../data/arxiv_downloads")
    
    # Process first 2 PDFs
    print("Testing PyMuPDF Preprocessor...")
    documents = preprocessor.process_pdfs(limit=2)
    
    print(f"\nProcessed {len(documents)} documents")
    
    # Display results
    for i, doc in enumerate(documents):
        print(f"\n--- Document {i+1} ---")
        print(f"File: {doc['metadata']['file_name']}")
        print(f"Length: {doc['metadata']['text_length']} characters")
        print(f"Preview: {doc['text'][:200]}...")
        print("-" * 50)

if __name__ == "__main__":
    test_preprocessor()
