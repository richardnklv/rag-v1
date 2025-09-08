import os
import urllib.request
import xml.etree.ElementTree as ET

# Define arXiv categories and search queries

categories = [
    # "physics.app-ph",    # Applied Physics
    # "physics.ins-det",   # Instrumentation and Detectors
    # "eess.SY",           # Systems and Control (Electrical Engineering)
    # "physics.gen-ph",    # General Physics
    # "cs.RO",             # Robotics (Computer Science)
    "physics.optics"     # Optics (for laser design and optical schematics)
]

max_results = 20  # Number of papers per category (adjust as needed)
output_dir = "arxiv_downloads"
os.makedirs(output_dir, exist_ok=True)

def download_arxiv_pdfs(category, max_results=20, keyword=None):
    if keyword:
        print(f"Downloading {max_results} papers from {category} with keyword '{keyword}'...")
        url = f"http://export.arxiv.org/api/query?search_query=cat:{category}+AND+all:{keyword}&start=0&max_results={max_results}"
    else:
        print(f"Downloading {max_results} papers from {category}...")
        url = f"http://export.arxiv.org/api/query?search_query=cat:{category}&start=0&max_results={max_results}"
    response = urllib.request.urlopen(url)
    xml_data = response.read().decode('utf-8')
    root = ET.fromstring(xml_data)
    for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
        pdf_url = None
        for link in entry.findall('{http://www.w3.org/2005/Atom}link'):
            if link.attrib.get('title') == 'pdf':
                pdf_url = link.attrib['href']
                break
        if pdf_url:
            title = entry.find('{http://www.w3.org/2005/Atom}title').text
            safe_title = "".join(c if c.isalnum() else "_" for c in title)[:50]
            pdf_path = os.path.join(output_dir, f"{safe_title}.pdf")
            try:
                print(f"Downloading: {title}")
                urllib.request.urlretrieve(pdf_url, pdf_path)
            except Exception as e:
                print(f"Failed to download {pdf_url}: {e}")


# Download general papers from all categories
for cat in categories:
    download_arxiv_pdfs(cat, max_results)

# Download laser design and optical schematic papers from optics
download_arxiv_pdfs("physics.optics", max_results=20, keyword="laser design")
download_arxiv_pdfs("physics.optics", max_results=20, keyword="optical schematic")