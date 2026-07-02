import urllib.request
import urllib.parse
import re

query = 'Biyani Dad & Co Nanded reviews'
url = 'https://html.duckduckgo.com/html/?q=' + urllib.parse.quote(query)
req = urllib.request.Request(
    url, 
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
)

try:
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8')
    print("DDG Page length:", len(html))
    
    # Extract search snippets
    snippets = re.findall(r'<a class="result__snippet"[^>]*>(.*?)</a>', html, re.S)
    print("Found snippets:", len(snippets))
    for i, s in enumerate(snippets[:10]):
        clean_s = re.sub('<[^<]+?>', '', s).strip()
        print(f"{i+1}. {clean_s}")
except Exception as e:
    print("Error:", e)
