import os, re, glob
ROOT = os.path.abspath(".")
html_files = sorted(glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True))
print(f"Total HTML files: {len(html_files)}")

link_re = re.compile(r'''(href|src)\s*=\s*["']([^"']+)["']''')
internal = 0
external = 0
anchor = 0
broken = []

for html in html_files:
    rel = os.path.relpath(html, ROOT)
    with open(html, encoding="utf-8", errors="replace") as f:
        content = f.read()
    for m in link_re.finditer(content):
        attr, link = m.group(1), m.group(2)
        if link.startswith(("http://", "https://", "mailto:", "tel:", "javascript:", "#")):
            if link.startswith("#"):
                anchor += 1
            else:
                external += 1
            continue
        internal += 1
        base = os.path.dirname(html)
        cleaned = link.split("#")[0].split("?")[0]
        if cleaned == "":
            target = base
        else:
            target = os.path.normpath(os.path.join(base, cleaned))
        if not os.path.exists(target):
            broken.append((rel, link, attr))

print(f"--- Summary ---")
print(f"Internal links: {internal}")
print(f"External links: {external}")
print(f"Anchor/empty links: {anchor}")
print(f"Broken internal links: {len(broken)}")
print(f"--- Broken links (file -> link) ---")
for rel, link, attr in broken:
    print(f"  [{rel}] ({attr}) {link}")
