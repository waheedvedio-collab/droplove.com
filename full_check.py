import subprocess, re
BASE = "https://waheedvedio-collab.github.io/droplove.com"

# 1. Check the discover.html page - it's a stub that redirects
print("=== discover.html content (root) ===")
r = subprocess.run(["curl","-s",f"{BASE}/discover.html"], capture_output=True, text=True, timeout=30)
content = r.stdout
has_refresh = 'http-equiv="refresh"' in content
print(f"  Is a stub with redirect: {has_refresh}")
print(f"  Content length: {len(content)}")
if has_refresh:
    refresh = re.search(r'content="0; url=([^"]+)"', content)
    print(f"  Redirects to: {refresh.group(1) if refresh else 'not found'}")

# 2. Check the index.html page content - verify hero images load
print("\n=== Index page asset references ===")
content = subprocess.run(["curl","-s",f"{BASE}/"], capture_output=True, text=True, timeout=30).stdout
imgs = re.findall(r'src="([^"]+)"', content)
print("  Image srcs:", imgs)
links = re.findall(r'href="([^"]+)"', content)
print("  All hrefs:", sorted(set(links)))

# 3. Check if CSS has RTL support
print("\n=== CSS RTL check ===")
css = subprocess.run(["curl","-s",f"{BASE}/assets/css/style.css"], capture_output=True, text=True, timeout=30).stdout
print(f"  CSS size: {len(css)} bytes")
rtl_mentions = re.findall(r'rtl', css, re.IGNORECASE)
print(f"  'rtl' mentions in CSS: {len(rtl_mentions)}")
# Check for [dir="rtl"] or html[dir=rtl]
rtl_selectors = re.findall(r'(?:dir=["\']?rtl["\']?|\[dir=)', css, re.IGNORECASE)
print(f"  RTL selectors in CSS: {len(rtl_selectors)}")
if rtl_selectors:
    for s in set(rtl_selectors):
        print(f"    {s}")

# 4. Check the nav links on register.html (full page)
print("\n=== register.html nav/header links ===")
content = subprocess.run(["curl","-s",f"{BASE}/register.html"], capture_output=True, text=True, timeout=30).stdout
header = re.search(r'<header[^>]*>(.*?)</header>', content, re.DOTALL)
if header:
    links = re.findall(r'href="([^"]+)"', header.group(1))
    print("  header links:", sorted(set(links)))

# 5. Check login.html links
print("\n=== login.html links ===")
content = subprocess.run(["curl","-s",f"{BASE}/login.html"], capture_output=True, text=True, timeout=30).stdout
all_links = re.findall(r'href="([^"]+)"', content)
print("  All links:", sorted(set(all_links)))

# 6. Check 404 page
print("\n=== 404.html links ===")
content = subprocess.run(["curl","-s",f"{BASE}/404.html"], capture_output=True, text=True, timeout=30).stdout
links = re.findall(r'href="([^"]+)"', content)
print("  Links:", sorted(set(links)))

# 7. Check admin.html 
print("\n=== admin.html links ===")
content = subprocess.run(["curl","-s",f"{BASE}/admin.html"], capture_output=True, text=True, timeout=30).stdout
links = re.findall(r'href="([^"]+)"', content)
print("  Links:", sorted(set(links)))

# 8. Check ar/index.html nav links (Arabic page nav)
print("\n=== ar/index.html full nav+header links ===")
content = subprocess.run(["curl","-s",f"{BASE}/ar/"], capture_output=True, text=True, timeout=30).stdout
header = re.search(r'<header[^>]*>(.*?)</header>', content, re.DOTALL)
if header:
    links = re.findall(r'href="([^"]+)"', header.group(1))
    print("  header links:", sorted(set(links)))
footer = re.search(r'<footer[^>]*>(.*?)</footer>', content, re.DOTALL | re.IGNORECASE)
if footer:
    links = re.findall(r'href="([^"]+)"', footer.group(1))
    print("  footer links:", sorted(set(links)))

# 9. Verify ko/nl are NOT in the language switcher
print("\n=== Language switcher on root includes ko/nl? ===")
content = subprocess.run(["curl","-s",f"{BASE}/"], capture_output=True, text=True, timeout=30).stdout
has_ko = "data-lang=\"ko\"" in content
has_nl = "data-lang=\"nl\"" in content
print(f"  ko in switcher: {has_ko}")
print(f"  nl in switcher: {has_nl}")
print(f"  ur in switcher: {'data-lang=\"ur\"' in content}")
print(f"  bn in switcher: {'data-lang=\"bn\"' in content}")
