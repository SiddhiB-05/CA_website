with open("C:/Users/biyan/.gemini/antigravity-ide/brain/56e4ec55-69e4-46f6-8f31-b3337826786c/scratch/google_page_mobile.html", "r", encoding="utf-8") as f:
    html = f.read()

print("Biyani count:", html.lower().count("biyani"))
print("Nanded count:", html.lower().count("nanded"))
print("Dad count:", html.lower().count("dad"))
print("Sumit count:", html.lower().count("sumit"))
print("Minal count:", html.lower().count("minal"))
print("Shyam count:", html.lower().count("shyam"))

# Let's write out any lines or snippets containing 'biyani'
for m in re.finditer(r'biyani', html, re.I):
    start = max(0, m.start() - 100)
    end = min(len(html), m.end() + 150)
    print("SNIPPET:", html[start:end].replace("\n", " "))
