import os
import requests
from bs4 import BeautifulSoup
import time

# ACTUAL Mechanical Engineering books from Project Gutenberg
engineering_book_ids = [
    13083,  # Mechanical Drawing
    13728,  # Machine Shop Practice
    40218,  # Mechanical Engineering
    23657,  # The Elements of Machine Design
    32822,  # Modern Machine-Shop Practice
    31299,  # Machine Design
    23979,  # Mechanical Drawing and Design
    15119,  # Modern Machine Shop Construction
    25818,  # Machine Shop Practice (Volume I)
    34493,  # Applied Mechanics
    31531,  # Mechanical Drawing Self-Taught
    23460,  # Steam-Engine Principles and Practice
    30155,  # Hydraulic and Other Tables
    28089,  # Machine Shop Work
    33828,  # Elements of Mechanical Drawing
]

output_dir = "gutenberg_books"
os.makedirs(output_dir, exist_ok=True)

def download_gutenberg_book(book_id):
    """Download a book from Project Gutenberg"""
    try:
        # Try PDF first, then EPUB, then TXT
        formats = [
            f"https://www.gutenberg.org/files/{book_id}/{book_id}-pdf.pdf",
            f"https://www.gutenberg.org/ebooks/{book_id}.epub.noimages",
            f"https://www.gutenberg.org/files/{book_id}/{book_id}-0.txt"
        ]
        
        for url in formats:
            print(f"Trying to download from: {url}")
            response = requests.get(url, stream=True)
            
            if response.status_code == 200:
                # Determine file extension
                if 'pdf' in url:
                    ext = '.pdf'
                elif 'epub' in url:
                    ext = '.epub'
                else:
                    ext = '.txt'
                
                filename = f"book_{book_id}{ext}"
                filepath = os.path.join(output_dir, filename)
                
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                print(f"✓ Downloaded: {filename}")
                return True
        
        print(f"✗ No downloadable format found for book {book_id}")
        return False
        
    except Exception as e:
        print(f"✗ Error downloading book {book_id}: {e}")
        return False

print("Downloading engineering books from Project Gutenberg...")
downloaded = 0

for book_id in engineering_book_ids:
    if download_gutenberg_book(book_id):
        downloaded += 1
    time.sleep(1)  # Be nice to the server

print(f"\nTotal books downloaded: {downloaded}")
print(f"Files saved to: {os.path.abspath(output_dir)}")
