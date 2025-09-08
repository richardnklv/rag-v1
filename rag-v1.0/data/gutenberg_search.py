import os
import requests
from bs4 import BeautifulSoup
import time
import re

output_dir = "gutenberg_books"
os.makedirs(output_dir, exist_ok=True)

def search_gutenberg(query):
    """Search Project Gutenberg for books by keyword"""
    search_url = f"https://www.gutenberg.org/ebooks/search/?query={query.replace(' ', '+')}"
    
    try:
        response = requests.get(search_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        books = []
        # Find all book links
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if '/ebooks/' in href and href.count('/') == 2:
                book_id = href.split('/')[2]
                if book_id.isdigit():
                    title = link.get_text(strip=True)
                    books.append((book_id, title))
        
        return books[:5]  # Return first 5 results
    except Exception as e:
        print(f"Error searching for {query}: {e}")
        return []

def download_gutenberg_book(book_id, title):
    """Download a book from Project Gutenberg"""
    try:
        # Try different formats
        formats = [
            (f"https://www.gutenberg.org/files/{book_id}/{book_id}-pdf.pdf", '.pdf'),
            (f"https://www.gutenberg.org/ebooks/{book_id}.epub.noimages", '.epub'),
            (f"https://www.gutenberg.org/files/{book_id}/{book_id}-0.txt", '.txt'),
            (f"https://www.gutenberg.org/files/{book_id}/{book_id}.txt", '.txt')
        ]
        
        for url, ext in formats:
            response = requests.get(url, stream=True)
            
            if response.status_code == 200:
                # Clean filename
                safe_title = re.sub(r'[^\w\s-]', '', title)[:50]
                filename = f"{safe_title}_{book_id}{ext}"
                filepath = os.path.join(output_dir, filename)
                
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                print(f"✓ Downloaded: {filename}")
                return True
        
        print(f"✗ No downloadable format found for: {title}")
        return False
        
    except Exception as e:
        print(f"✗ Error downloading {title}: {e}")
        return False

# Search terms for mechanical engineering
search_terms = [
    "mechanical engineering",
    "machine design",
    "mechanical drawing", 
    "steam engine",
    "machine shop",
    "applied mechanics",
    "engineering drawing"
]

print("Searching Project Gutenberg for mechanical engineering books...")
downloaded = 0

for term in search_terms:
    print(f"\nSearching for: {term}")
    books = search_gutenberg(term)
    
    for book_id, title in books:
        print(f"Found: {title}")
        if download_gutenberg_book(book_id, title):
            downloaded += 1
        time.sleep(0.5)  # Be nice to the server
        
        if downloaded >= 20:  # Limit downloads
            break
    
    if downloaded >= 20:
        break

print(f"\nTotal books downloaded: {downloaded}")
print(f"Files saved to: {os.path.abspath(output_dir)}")
