import subprocess, re

BASE = "https://waheedvedio-collab.github.io/droplove.com"

def fetch(url):
    r = subprocess.run(["curl", "-sL", url], capture_output=True, text=True, timeout=30)
    return r.stdout

# 1. Full language switcher options on /ar/ (click the dropdown)
print("=== Language switcher options on /ar/ (all lang-option links) ===")
content = fetch(f"{BASE}/ar/")
options = re.findall(r'class="lang-option"\s+href="([^"]+)"\s+data-lang="([^"]+)"', content)
for href, lang in options:
    print(f"  {lang}: {href}")

# Also find all lang-option links
options2 = re.findall(r'href="([^"]+)"\s+data-lang="([^"]+)"', content)
print("  (regex2)")
for href, lang in options2:
    print(f"  {lang}: {href}")

# 2. Find ALL data-lang values and their hrefs
print("\n=== All data-lang links on /ar/ ===")
matches = re.findall(r'data-lang="([a-z]+)".*?href="([^"]+)"', content, re.DOTALL)
for lang, href in matches:
    print(f"  {lang}: {href}")

# Try the other order
matches = re.findall(r'href="([^"]+)"[^>]*data-lang="([a-z]+)"', content, re.DOTALL)
for href, lang in matches:
    print(f"  {lang}: {href}")

# 3. Check nav links on /ar/ (header)
print("\n=== Header nav links on /ar/ ===")
header = re.search(r'<header[^>]*>(.*?)</header>', content, re.DOTALL | re.IGNORECASE)
if header:
    links = re.findall(r'href="([^"]+)"', header.group(1))
    print("Header links:", sorted(set(links)))
else:
    # Find all relative links
    links = re.findall(r'href="([^"]+)"', content)
    rel = sorted(set(l for l in links if l.startswith(('./','#'))))
    print("All relative links:", rel[:30])

# 4. Check the nav on root
print("\n=== Full nav (header+footer) on root / ===")
content = fetch(f"{BASE}/")
header = re.search(r'<header[^>]*>(.*?)</header>', content, re.DOTALL | re.IGNORECASE)
if header:
    links = re.findall(r'href="([^"]+)"', header.group(1))
    print("Header links:", sorted(set(links)))
footer = re.search(r'<footer[^>]*>(.*?)</footer>', content, re.DOTALL | re.IGNORECASE)
if footer:
    links = re.findall(r'href="([^"]+)"', footer.group(1))
    print("Footer links:", sorted(set(links)))

# 5. Count total language options in switcher (root)
print("\n=== Full language switcher on root / ===")
content = fetch(f"{BASE}/")
# Find the lang-bar or dropdown
start = content.find('lang-trigger')
if start >= 0:
    s = max(0, start - 50)
    # Get a larger chunk
    chunk = content[start:start+3000]
    links = re.findall(r'href="([^"]+)"', chunk)
    print("Switcher links nearby:", sorted(set(links)))

# 6. Verify the exact HTML lang / dir attributes
print("\n=== html tag attributes per language ===")
for lang in ["en", "fr", "ar", "es", "de", "ja", "zh", "hi", "ur"]:
    content = fetch(f"{BASE}/{lang}/" if lang != "en" else "skip")
    if lang != "en":
        html_tag = re.search(r'<html[^>]*>', content)
        if html_tag:
            print(f"  {lang}: {html_tag.group()}")
        else:
            print(f"  {lang}: no html tag found")

# 7. Check en/ specifically - the empty directory
print("\n=== en/ directory check ===")
code = subprocess.run(["curl","-s","-o","/dev/null","-w","%{http_code}", "-L", f"{BASE}/en/"], capture_output=True, text=True, timeout=15).stdout
print(f"  en/: {code} (directory exists but is EMPTY - 0 files)")

# 8. Check if there are any 404s besides ko/nl/en
print("\n=== All 14 required langs status ===")
LANGUAGES = ["en", "fr", "ar", "es", "de", "it", "pt", "tr", "ru", "zh", "ja", "ko", "hi", "nl"]
for lang in LANGUAGES:
    url = f"{BASE}/{lang}/"
    code = subprocess.run(["curl","-s","-o","/dev/null","-w","%{http_code}","-L",url], capture_output=True, text=True, timeout=15).stdout
    print(f"  {lang}: {code}")
