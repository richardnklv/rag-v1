import os
import requests
import time
import re

output_dir = "gutenberg_books"
os.makedirs(output_dir, exist_ok=True)

def search_gutendx(search_term, max_results=10):
    """Search for books using Gutendx API"""
    url = f"https://gutendx.com/books/?search={search_term.replace(' ', '%20')}"
    
    try:
        response = requests.get(url)
        data = response.json()
        return data.get('results', [])[:max_results]
    except Exception as e:
        print(f"Error searching for {search_term}: {e}")
        return []

def download_book(book_data):
    """Download a book from the formats available"""
    book_id = book_data['id']
    title = book_data['title']
    formats = book_data.get('formats', {})
    
    # Priority: PDF > EPUB > TXT
    download_formats = [
        ('application/pdf', '.pdf'),
        ('application/epub+zip', '.epub'),
        ('text/plain; charset=us-ascii', '.txt'),
        ('text/plain', '.txt')
    ]
    
    for mime_type, ext in download_formats:
        if mime_type in formats:
            url = formats[mime_type]
            try:
                print(f"Downloading: {title}")
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
                    
            except Exception as e:
                print(f"✗ Error downloading {title}: {e}")
                continue
    
    print(f"✗ No downloadable format found for: {title}")
    return False

# Search terms specifically for mechanical engineering
search_terms = [
    "mechanical engineering",
    "machine design", 
    "steam engine",
    "mechanical drawing",
    "engineering drawing",
    "machine shop",
    "applied mechanics",
    "engineering mechanics",
    "mechanical principles"
]

print("Searching Gutendx for mechanical engineering books...")
downloaded = 0
max_downloads = 30

for term in search_terms:
    if downloaded >= max_downloads:
        break
        
    print(f"\nSearching for: {term}")
    books = search_gutendx(term, max_results=5)
    
    for book in books:
        if downloaded >= max_downloads:
            break
            
        if download_book(book):
            downloaded += 1
        
        time.sleep(0.5)  # Be nice to the server

print(f"\nTotal books downloaded: {downloaded}")
print(f"Files saved to: {os.path.abspath(output_dir)}")
