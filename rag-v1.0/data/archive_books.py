
# Updated script: Use internetarchive package for focused, practical engineering books/manuals
import os
import internetarchive

search_terms = [
    "shigley mechanical engineering design",
    "naval architecture", 
    "ship construction",
    "marine engineering",
    "aircraft design",
    "engineering drawing",
    "machine design handbook",
    "mechanical engineering textbook",
    "engineering mechanics",
    "fluid mechanics",
    "thermodynamics",
    "heat transfer",
    "materials science",
    "structural analysis",
    "machine elements"
]

output_dir = "archive_books"
os.makedirs(output_dir, exist_ok=True)

downloaded_count = 0
max_downloads = 50  # Limit to prevent too many downloads

for term in search_terms:
    if downloaded_count >= max_downloads:
        break
    print(f"Searching for: {term}")
    results = internetarchive.search_items(f'title:("{term}") AND mediatype:texts', fields=['identifier', 'title'])
    
    count = 0
    for result in results:
        if count >= 3:  # Download up to 3 books per search term
            break
        if downloaded_count >= max_downloads:
            break
            
        identifier = result['identifier']
        title = result.get('title', identifier)
        print(f"Downloading: {title}")
        try:
            item = internetarchive.get_item(identifier)
            # Check if item has any downloadable files first
            files = item.get_files()
            pdf_files = [f for f in files if f.name.lower().endswith('.pdf')]
            
            if pdf_files:
                response = item.download(formats='PDF', destdir=output_dir, ignore_existing=True, verbose=True)
                print(f"✓ Successfully downloaded: {title}")
                downloaded_count += 1
                count += 1
            else:
                # Try downloading any available text file formats
                text_files = [f for f in files if f.name.lower().endswith(('.txt', '.epub', '.mobi', '.djvu'))]
                if text_files:
                    response = item.download(formats=['TXT', 'EPUB', 'MOBI', 'DJVU'], destdir=output_dir, ignore_existing=True, verbose=True)
                    print(f"✓ Downloaded (non-PDF): {title}")
                    downloaded_count += 1
                    count += 1
                else:
                    print(f"✗ No downloadable files found for: {title}")
        except Exception as e:
            print(f"✗ Failed to download {title}: {e}")

print(f"\nTotal books downloaded: {downloaded_count}")
print(f"Files saved to: {os.path.abspath(output_dir)}")
