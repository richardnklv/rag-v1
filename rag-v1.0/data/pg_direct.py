import os
import requests
from bs4 import BeautifulSoup
import time
import re

output_dir = "project_gutenberg_books"
os.makedirs(output_dir, exist_ok=True)

def search_project_gutenberg(search_term):
    """Search Project Gutenberg directly"""
    search_url = f"https://www.gutenberg.org/ebooks/search/?query={search_term.replace(' ', '+')}&submit_search=Go%21"
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        books = []
        # Find book links in search results
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if '/ebooks/' in href and len(href.split('/')) >= 3:
                try:
                    book_id = href.split('/')[-1]
                    if book_id.isdigit():
                        title = link.get_text(strip=True)
                        if title and len(title) > 5:  # Filter out short/empty titles
                            books.append((book_id, title))
                except:
                    continue
        
        return books[:5]  # Return first 5 results
    except Exception as e:
        print(f"Error searching for {search_term}: {e}")
        return []

def download_gutenberg_book(book_id, title):
    """Download a book from Project Gutenberg"""
    try:
        # Try different download URLs
        download_urls = [
            f"https://www.gutenberg.org/files/{book_id}/{book_id}-pdf.pdf",
            f"https://www.gutenberg.org/files/{book_id}/{book_id}.pdf", 
            f"https://www.gutenberg.org/ebooks/{book_id}.epub.noimages",
            f"https://www.gutenberg.org/files/{book_id}/{book_id}-0.txt",
            f"https://www.gutenberg.org/files/{book_id}/{book_id}.txt"
        ]
        
        for url in download_urls:
            try:
                response = requests.get(url, stream=True)
                
                if response.status_code == 200:
                    # Determine file extension
                    if '.pdf' in url:
                        ext = '.pdf'
                    elif '.epub' in url:
                        ext = '.epub'
                    else:
                        ext = '.txt'
                    
                    # Clean filename
                    safe_title = re.sub(r'[^\w\s-]', '', title)[:50]
                    filename = f"{safe_title}_{book_id}{ext}"
                    filepath = os.path.join(output_dir, filename)
                    
                    with open(filepath, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    print(f"✓ Downloaded: {filename}")
                    return True
                    
            except Exception:
                continue
        
        print(f"✗ No downloadable format found for: {title}")
        return False
        
    except Exception as e:
        print(f"✗ Error downloading {title}: {e}")
        return False

# Search terms for mechanical engineering
search_terms = [
    "mechanical engineering",
    "machine design",
    "steam engine", 
    "mechanical drawing",
    "machine shop",
    "applied mechanics",
    "engineering drawing"
]

print("Searching Project Gutenberg for mechanical engineering books...")
downloaded = 0
max_downloads = 25

for term in search_terms:
    if downloaded >= max_downloads:
        break
        
    print(f"\nSearching for: {term}")
    books = search_project_gutenberg(term)
    
    for book_id, title in books:
        if downloaded >= max_downloads:
            break
            
        print(f"Found: {title}")
        if download_gutenberg_book(book_id, title):
            downloaded += 1
        
        time.sleep(1)  # Be nice to the server
    
    if downloaded >= max_downloads:
        break

print(f"\nTotal books downloaded: {downloaded}")
print(f"Files saved to: {os.path.abspath(output_dir)}")
