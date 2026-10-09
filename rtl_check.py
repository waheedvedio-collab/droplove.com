import subprocess, re, html as html_module

BASE = "https://waheedvedio-collab.github.io/droplove.com"

def fetch(url):
    r = subprocess.run(["curl", "-sL", url], capture_output=True, text=True, timeout=30)
    return r.stdout

# 1. Check RTL: does ar/index.html have dir="rtl" or lang="ar"?
print("=== RTL CHECK: ar/index.html ===")
content = fetch(f"{BASE}/ar/")
rtl_attrs = re.findall(r'html[^>]*', content[:500])
print("html tag:", rtl_attrs[0] if rtl_attrs else "NOT FOUND")
# look for dir=rtl
if 'dir="rtl"' in content or "dir='rtl'" in content:
    print("RTL attribute: FOUND (dir=rtl)")
else:
    print("RTL attribute: MISSING dir='rtl'")

# check textdirection in CSS/body
print("body class/styles with rtl:", re.findall(r'dir[="\']?rtl', content)[:3])

# 2. Check language switcher links on homepage
print("\n=== LANGUAGE SWITCHER LINKS on / (root index) ===")
content = fetch(f"{BASE}/")
# find all language links
lang_links = re.findall(r'href=["\'](\./[a-z]{2}/)["\']', content)
lang_links = sorted(set(lang_links))
for l in lang_links:
    print(f"  {l}")

print("\n=== LANGUAGE SWITCHER LINKS on /ar/ ===")
content = fetch(f"{BASE}/ar/")
lang_links = re.findall(r'href=["\']([^"\']*[a-z]{2}/)["\']', content)
lang_links = sorted(set(lang_links))
for l in lang_links:
    print(f"  {l}")

# 3. Check asset paths in ar/index.html
print("\n=== ASSET PATHS in ar/index.html ===")
content = fetch(f"{BASE}/ar/")
asset_paths = re.findall(r'(?:href|src)=["\'](\.\.?[^"\']*assets[^"\']*)["\']', content)
for a in sorted(set(asset_paths)):
    print(f"  {a}")

# 4. Check what en/ resolves to
print("\n=== en/ redirect chain ===")
r = subprocess.run(["curl", "-sIL", "-o", "/dev/null", "-w", "%{http_code}|%{url_effective}\\n", f"{BASE}/en/"], capture_output=True, text=True)
print(f"  HEAD: {r.stdout.strip()}")

# 5. Check the nav links inside ar/index.html (main nav)
print("\n=== NAV LINKS in ar/index.html ===")
content = fetch(f"{BASE}/ar/")
nav_section = re.findall(r'<nav[^>]*>(.*?)</nav>', content, re.DOTALL)
if nav_section:
    links = re.findall(r'href=["\']([^"\']+)["\']', nav_section[0])
    for l in sorted(set(links)):
        print(f"  {l}")
else:
    # try finding main nav by class
    nav_by_class = re.findall(r'class="[^"]*(?:nav|menu)[^"]*"[^>]*>(.*?)</(?:ul|div|nav)>', content, re.DOTALL)
    all_links = re.findall(r'href=["\']([^"\']+)["\']', content)
    main_links = [l for l in all_links if not l.startswith(('http','#','mailto','tel','.','//')) or l.startswith('./')]
    print("  (no <nav> tag found, showing relative links):")
    for l in sorted(set(main_links)):
        print(f"  {l}")

# 6. Check contact.html form rendering
print("\n=== CONTACT PAGE form check (root) ===")
content = fetch(f"{BASE}/contact.html")
has_form = '<form' in content
has_input = re.findall(r'<input[^>]*name=[\"\']([^\"\']+)[\"\']', content)
has_csrf = 'csrf' in content.lower()
print(f"  Has form: {has_form}")
print(f"  Input names: {has_input}")
print(f"  Has CSRF token: {has_csrf}")

# 7. Check the stub pages - what they show
print("\n=== STUB PAGE content check (dashboard.html) ===")
content = fetch(f"{BASE}/dashboard.html")
print(f"  Content length: {len(content)}")
print(f"  Has redirect meta: {'http-equiv=\"refresh\"' in content}")
print(f"  Shows 'sign in' message: {'sign in' in content.lower()}")
print(f"  Title: {re.search(r'<title>(.*?)</title>', content)}")

# 8. Check all 14 langs on contact.html
print("\n=== contact.html availability by language ===")
LANGUAGES = ["en", "fr", "ar", "es", "de", "it", "pt", "tr", "ru", "zh", "ja", "ko", "hi", "nl"]
for lang in LANGUAGES:
    url = f"{BASE}/{lang}/contact.html"
    code = subprocess.run(["curl", "-s", "-o", "/dev/null", "-L", "-w", "%{http_code}", url], capture_output=True, text=True, timeout=20).stdout.strip()
    print(f"  [{code}] {lang}/contact.html")
