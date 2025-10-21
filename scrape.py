import os
import requests
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
CX = os.getenv("GOOGLE_CX")  

DOWNLOAD_DIR = "university_pdfs"
NUM_RESULTS = 1
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

with open("universities.txt", "r", encoding="utf-8") as f:
    universities = [line.strip() for line in f if line.strip()]

def search_pdfs(university_name, num_results=2):
    pdf_urls = []
    params = {
        "key": API_KEY,
        "cx": CX,
        "q": f"{university_name} masters brochure 2025 filetype:pdf",
        "num": num_results
    }
    response = requests.get("https://www.googleapis.com/customsearch/v1", params=params)
    data = response.json()
    for item in data.get("items", []):
        link = item.get("link", "")
        if link.endswith(".pdf"):
            pdf_urls.append(link)
    return pdf_urls[:num_results]  

def download_pdfs(pdf_urls):
    for url in tqdm(pdf_urls, desc="Downloading PDFs"):
        try:
            response = requests.get(url)
            response.raise_for_status()
            filename = os.path.join(DOWNLOAD_DIR, url.split("/")[-1])
            with open(filename, "wb") as f:
                f.write(response.content)
        except Exception as e:
            print(f"Failed to download {url}: {e}")


for uni in universities:
    pdfs = search_pdfs(uni, NUM_RESULTS)
    download_pdfs(pdfs)

print("All PDFs downloaded!")
