import subprocess, re

BASE = "https://waheedvedio-collab.github.io/droplove.com"

def fetch(url):
    r = subprocess.run(["curl", "-sL", url], capture_output=True, text=True, timeout=30)
    return r.stdout

# 1. Find the language switcher HTML block on root index
print("=== Language switcher block on root / ===")
content = fetch(f"{BASE}/")
# Find a block containing multiple lang links
idx = content.find('./ar/')
if idx >= 0:
    start = max(0, idx - 500)
    end = min(len(content), idx + 500)
    print(content[start:end])

print()

# 2. Find language switcher on /ar/
print("=== Language switcher block on /ar/ ===")
content = fetch(f"{BASE}/ar/")
# find the footer or switcher
switcher = re.search(r'class="[^"]*lang[^"]*"[^>]*>(.*?)</(?:ul|div|section)>', content, re.DOTALL | re.IGNORECASE)
if switcher:
    print(switcher.group()[:600])
else:
    # find all href links containing language codes
    lang_refs = re.findall(r'href="([^"]*[a-z]{2}/?)"', content)
    print("Language refs found:", sorted(set(lang_refs)))

print()

# 3. Check ALL href links in root nav (main navigation)
print("=== ALL nav links on root / (relative) ===")
content = fetch(f"{BASE}/")
# Find main nav - look for header or nav
header = re.search(r'<header[^>]*>(.*?)</header>', content, re.DOTALL | re.IGNORECASE)
if header:
    links = re.findall(r'href="([^"]+)"', header.group(1))
    print("Header links:", sorted(set(links)))
else:
    links = re.findall(r'href="([^"]+)"', content)
    rel_links = [l for l in links if l.startswith(('./','#'))]
    print("All relative links (first 30):", sorted(set(rel_links))[:30])

# 4. Check what languages are listed in the language switcher
print("\n=== All language links found across site ===")
for lang in ["en","fr","ar","es","de","it","pt","tr","ru","zh","ja","ko","hi","nl","bn","ur"]:
    url = f"{BASE}/{lang}/"
    code = subprocess.run(["curl","-s","-o","/dev/null","-w","%{http_code}","-L",url], capture_output=True, text=True, timeout=15).stdout.strip()
    print(f"  {lang}: {code}")

# 5. Check the footer language switcher specifically
print("\n=== Footer / language switcher HTML (root) ===")
content = fetch(f"{BASE}/")
# find footer
footer = re.search(r'<footer[^>]*>(.*?)</footer>', content, re.DOTALL | re.IGNORECASE)
if footer:
    links = re.findall(r'href="([^"]+)"', footer.group(1))
    print("Footer links:", sorted(set(links)))
else:
    # look for a language selector
    match = re.search(r'(?:lang|language)[^"]*"[^>]*>(.*?)</(?:select|ul|div)', content, re.DOTALL | re.IGNORECASE)
    if match:
        links = re.findall(r'href="([^"]+)"', match.group(1)[:1000])
        print("Switcher links:", sorted(set(links)))
    else:
        print("No footer found")
        # search for language-related elements
        for m in re.finditer(r'(?:hreflang|lang-switcher|language-switcher)', content, re.IGNORECASE):
            s = max(0, m.start()-100)
            e = min(len(content), m.start()+200)
            print("  context:", content[s:e])
