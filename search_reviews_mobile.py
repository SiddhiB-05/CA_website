import urllib.request
import re
import json

url = "https://www.google.com/search?kgmid=/g/11h09pnqq4&hl=en-IN&q=Biyani+Dad+%26+Co."
req = urllib.request.Request(
    url, 
    headers={'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1'}
)

try:
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8')
    
    print("Page length with mobile UA:", len(html))
    with open("C:/Users/biyan/.gemini/antigravity-ide/brain/56e4ec55-69e4-46f6-8f31-b3337826786c/scratch/google_page_mobile.html", "w", encoding="utf-8") as f:
        f.write(html)

    # Let's search for "Biyani" or specific reviews
    # Let's print out all blocks of text that look like reviews. 
    # Google reviews often contain quotes or stars.
    # Let's search for matches in the mobile HTML
    # We can look for spans or divs containing text with common words
    # Let's clean up html tags and print lines that have reviews
    text_blocks = re.findall(r'<div[^>]*>([^<]{20,500})</div>', html)
    print("Div matches found:", len(text_blocks))
    for t in text_blocks:
        t_clean = t.strip()
        if any(w in t_clean.lower() for w in ["best", "good", "perfect", "great", "excellent", "ca ", "chartered", "nanded"]):
            print("DIV:", t_clean[:150])

    span_blocks = re.findall(r'<span[^>]*>([^<]{20,500})</span>', html)
    print("Span matches found:", len(span_blocks))
    for s in span_blocks:
        s_clean = s.strip()
        if any(w in s_clean.lower() for w in ["best", "good", "perfect", "great", "excellent", "ca ", "chartered", "nanded"]):
            print("SPAN:", s_clean[:150])

except Exception as e:
    print("Error:", e)
