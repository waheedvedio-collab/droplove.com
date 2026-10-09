import re, subprocess
BASE = "https://waheedvedio-collab.github.io/droplove.com"

# Get root index
content = subprocess.run(["curl","-sL",BASE+"/"], capture_output=True, text=True, timeout=30).stdout

# Find all lang-option blocks
blocks = re.findall(r'<a\s+class="lang-option[^"]*"\s+href="([^"]+)"[^>]*data-lang="([^"]+)"', content)
print("=== Language switch options on root / ===")
for href, lang in blocks:
    print(f"  {lang}: {href}")

# Check ko and nl
print("\n=== Missing languages ===")
for lang in ["ko", "nl"]:
    code = subprocess.run(["curl","-s","-o","/dev/null","-w","%{http_code}",f"{BASE}/{lang}/"], capture_output=True, text=True, timeout=15).stdout
    print(f"  {lang}/: HTTP {code} (lang/{lang}.php doesn't exist in source)")

# Check en/ - empty directory
print("\n=== en/ directory ===")
r = subprocess.run(["curl","-sIL",f"{BASE}/en/"], capture_output=True, text=True, timeout=15)
print(f"  HTTP status: {r.stdout.splitlines()[0] if r.stdout else 'N/A'}")

# Check nav on root
print("\n=== All nav-related hrefs on root / ===")
nav_match = re.search(r'<nav class="main-nav"[^>]*>(.*?)</nav>', content, re.DOTALL)
if nav_match:
    links = re.findall(r'href="([^"]+)"', nav_match.group(1))
    print("  main-nav links:", links)

# Header actions
header_actions = re.search(r'class="header-actions"[^>]*>(.*?)(?:</div>\s*</div>)', content, re.DOTALL)
if header_actions:
    links = re.findall(r'href="([^"]+)"', header_actions.group(1))
    print("  header-actions links:", links)

# Footer
footer_match = re.search(r'<footer[^>]*>(.*?)</footer>', content, re.DOTALL | re.IGNORECASE)
if footer_match:
    links = re.findall(r'href="([^"]+)"', footer_match.group(1))
    print("  footer links:", sorted(set(links)))
else:
    print("  No <footer> tag found")

# Hero CTA buttons
print("\n=== Hero CTA buttons on root / ===")
hero = re.search(r'class="hero[^"]*"[^>]*>(.*?)(?:</section>|</div>\s*</div>)', content, re.DOTALL | re.IGNORECASE)
if hero:
    buttons = re.findall(r'href="([^"]+)"', hero.group(1))
    print("  hero buttons:", buttons)

# discover.html nav links
print("\n=== discover.html nav links ===")
content = subprocess.run(["curl","-sL",BASE+"/discover.html"], capture_output=True, text=True, timeout=30).stdout
nav_match = re.search(r'<nav class="main-nav"[^>]*>(.*?)</nav>', content, re.DOTALL)
if nav_match:
    links = re.findall(r'href="([^"]+)"', nav_match.group(1))
    print("  main-nav links:", links)
else:
    all_rel = re.findall(r'href="(\./[^"]+)"', content)
    print("  relative links:", sorted(set(all_rel)))
