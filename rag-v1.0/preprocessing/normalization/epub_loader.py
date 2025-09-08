import fitz  # PyMuPDF
import os
from typing import List, Dict


class PyMuPDFEpubPreprocessor:
    """
    Simple EPUB preprocessor using PyMuPDF for clean text extraction.
    """
    
    def __init__(self, data_directory: str):
        """
        Initialize preprocessor with data directory.
        
        Args:
            data_directory (str): Path to directory containing EPUB files
        """
        self.data_directory = data_directory
    
    def process_epubs(self, limit: int = None) -> List[Dict]:
        """
        Process EPUB files and extract clean text.
        
        Args:
            limit (int, optional): Maximum number of files to process
            
        Returns:
            List[Dict]: List of documents with text and metadata
        """
        # Get EPUB files
        epub_files = [f for f in os.listdir(self.data_directory) if f.endswith('.epub')]
        
        if limit:
            epub_files = epub_files[:limit]
        
        documents = []
        
        for filename in epub_files:
            epub_path = os.path.join(self.data_directory, filename)
            
            try:
                # Open EPUB with PyMuPDF
                doc = fitz.open(epub_path)
                
                # Extract text from all pages
                full_text = ""
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    text = page.get_text()
                    full_text += text + "\n\n"
                
                doc.close()
                
                # Create document with metadata
                document = {
                    'text': full_text.strip(),
                    'metadata': {
                        'file_name': filename,
                        'file_path': epub_path,
                        'text_length': len(full_text),
                        'processor': 'pymupdf_epub'
                    }
                }
                
                documents.append(document)
                print(f"✓ Processed {filename}: {len(full_text)} characters")
                
            except Exception as e:
                print(f"✗ Error processing {filename}: {e}")
        
        return documents
