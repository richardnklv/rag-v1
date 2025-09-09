import pymupdf4llm
import os
from typing import List, Dict


class PyMuPDFPreprocessor:
    """
    Simple PDF preprocessor using pymupdf4llm for clean markdown extraction.
    """
    
    def __init__(self, data_directory: str):
        """
        Initialize preprocessor with data directory.
        
        Args:
            data_directory (str): Path to directory containing PDF files
        """
        self.data_directory = data_directory
    
    def process_pdfs(self, limit: int = None) -> List[Dict]:
        """
        Process PDF files and extract clean markdown text.
        
        Args:
            limit (int, optional): Maximum number of files to process
            
        Returns:
            List[Dict]: List of documents with text and metadata
        """
        # Get PDF files
        pdf_files = [f for f in os.listdir(self.data_directory) if f.endswith('.pdf')]
        
        if limit:
            pdf_files = pdf_files[:limit]
        
        documents = []
        
        for filename in pdf_files:
            pdf_path = os.path.join(self.data_directory, filename)
            
            try:
                # Extract markdown text
                markdown_text = pymupdf4llm.to_markdown(pdf_path)
                
                # Create document with metadata
                document = {
                    'text': markdown_text,
                    'metadata': {
                        'file_name': filename,
                        'file_path': pdf_path,
                        'text_length': len(markdown_text),
                        'processor': 'pymupdf4llm'
                    }
                }
                
                documents.append(document)
                print(f"✓ Processed {filename}: {len(markdown_text)} characters")
                
            except Exception as e:
                print(f"✗ Error processing {filename}: {e}")
        
        return documents
    
    def process_single_pdf(self, pdf_path: str) -> List[Dict]:
        """
        Process a single PDF file and extract clean markdown text.
        
        Args:
            pdf_path (str): Full path to the PDF file
            
        Returns:
            List[Dict]: List containing single document with text and metadata
        """
        try:
            # Extract markdown text
            markdown_text = pymupdf4llm.to_markdown(pdf_path)
            
            # Create document with metadata
            document = {
                'text': markdown_text,
                'metadata': {
                    'file_name': os.path.basename(pdf_path),
                    'file_path': pdf_path,
                    'text_length': len(markdown_text),
                    'processor': 'pymupdf4llm'
                }
            }
            
            return [document]
            
        except Exception as e:
            print(f"✗ Error processing {os.path.basename(pdf_path)}: {e}")
            return []
