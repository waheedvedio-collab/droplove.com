import re, subprocess
BASE = "https://waheedvedio-collab.github.io/droplove.com"
content = subprocess.run(["curl","-sL",BASE+"/"], capture_output=True, text=True, timeout=30).stdout

# find all lang-option elements with href + data-lang
options = re.findall(r'lang-option[^>]*href="([^"]+)"[^>]*data-lang="([^"]+)"', content)
print("lang-option (href, lang):", options)

# general data-lang+href
matches = re.findall(r'href="([^"]+)"[^>]*data-lang="([^a-z]+)"', content)
print("general:", matches)

# Also try: find the language bar and extract all hrefs
idx = content.find("lang-bar")
if idx >= 0:
    chunk = content[idx:idx+5000]
    links = re.findall(r'href="([^"]+)"', chunk)
    print("lang-bar links:", sorted(set(links)))

# Count total languages in switcher
all_lang_hrefs = re.findall(r'href="(\./[a-z]{2}/)"', content)
print("All lang switcher hrefs on root:", sorted(set(all_lang_hrefs)))
