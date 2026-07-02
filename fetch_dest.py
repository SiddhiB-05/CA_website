import urllib.request
import re

url = "https://share.google/ICclOnbGncjzcvwXW"
req = urllib.request.Request(
    url,
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Safari/537.36'}
)

try:
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8')
    print("Fetched HTML length:", len(html))
    
    # Save raw HTML
    with open("C:/Users/biyan/.gemini/antigravity-ide/brain/56e4ec55-69e4-46f6-8f31-b3337826786c/scratch/dest_page.html", "w", encoding="utf-8") as f:
        f.write(html)
        
    # Get all spans or strings that look like text
    texts = re.findall(r'>([^<]{15,400})<', html)
    print("Found text count:", len(texts))
    with open("C:/Users/biyan/.gemini/antigravity-ide/brain/56e4ec55-69e4-46f6-8f31-b3337826786c/scratch/dest_text.txt", "w", encoding="utf-8") as f:
        for t in texts:
            f.write(t.strip() + "\n")
            
except Exception as e:
    print("Error:", e)
