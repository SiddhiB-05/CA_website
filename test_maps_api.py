import urllib.request
import json
import re

url = "https://www.google.com/maps/preview/review/list?authuser=0&hl=en&gl=in&pb=!1m1!1s0x3bd1d72723d21633:0x5cd28803af317c!2m2!1i1!2i10!3m1!5b1"
req = urllib.request.Request(
    url,
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
)

try:
    with urllib.request.urlopen(req) as response:
        content = response.read().decode('utf-8')
    print("Content length:", len(content))
    
    # Google's JSON response has anti-XSS prefix )]}'\n
    if content.startswith(")]}'"):
        content = content[4:].strip()
        
    # Let's save the first 2000 chars of JSON to verify
    print("First 500 chars of JSON:", content[:500])
    
    # Parse the JSON. Google Maps review list JSON has nested arrays.
    data = json.loads(content)
    # The reviews are usually in data[2] or nested deeply.
    # Let's dump the structure or look for string reviews.
    reviews = []
    # Let's find all text blocks in the JSON that look like reviews
    def find_strings(item):
        if isinstance(item, str):
            if len(item) > 10 and not item.startswith("//") and not item.startswith("http"):
                reviews.append(item)
        elif isinstance(item, list):
            for sub in item:
                find_strings(sub)
        elif isinstance(item, dict):
            for k, v in item.items():
                find_strings(v)
                
    find_strings(data)
    print("All string fields found in JSON count:", len(reviews))
    for r in reviews[:15]:
        print("-", r[:100])
        
except Exception as e:
    print("Error:", e)
