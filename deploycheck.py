import subprocess, sys

BASE = "https://waheedvedio-collab.github.io/droplove.com"

LANGUAGES = ["en", "fr", "ar", "es", "de", "it", "pt", "tr", "ru", "zh", "ja", "ko", "hi", "nl"]

PAGES_MAIN = ["", "index.html", "contact.html", "login.html", "register.html",
              "privacy.html", "terms.html", "404.html", "dashboard.html",
              "discover.html", "messages.html", "profile.html", "edit_profile.html", "admin.html"]

def curl_url(url):
    try:
        r = subprocess.run(
            ["curl", "-sIL", "-o", "/dev/null", "-w", "%{http_code}|%{url_effective}", url],
            capture_output=True, text=True, timeout=30
        )
        parts = r.stdout.strip().split("|")
        code = parts[0] if parts else "?"
        # Follow redirects: get final status
        r2 = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-L", "-w", "%{http_code}|%{url_effective}", url],
            capture_output=True, text=True, timeout=30
        )
        parts2 = r2.stdout.strip().split("|")
        final_code = parts2[0] if parts2 else "?"
        final_url = parts2[1] if len(parts2) > 1 else url
        return code, final_code, final_url
    except Exception as e:
        return "ERR", "ERR", str(e)

# Test root pages
print("=== ROOT PAGES (no language) ===")
for page in PAGES_MAIN:
    url = f"{BASE}/{page}"
    head_code, final_code, final_url = curl_url(url)
    status = "OK" if final_code == "200" else "FAIL"
    print(f"  [{status}] {final_code}  {url}" + (f" -> {final_url}" if final_url != url else ""))

# Test language homepages
print("\n=== LANGUAGE ROOTS (homepage per language) ===")
for lang in LANGUAGES:
    url = f"{BASE}/{lang}/"
    head_code, final_code, final_url = curl_url(url)
    status = "OK" if final_code == "200" else "MISSING"
    print(f"  [{status}] {final_code}  {url}" + (f" -> {final_url}" if final_url != url else ""))

# Test a few key pages in a few languages
print("\n=== KEY PAGES IN AR (RTL) ===")
for page in ["contact.html", "login.html", "register.html", "privacy.html", "terms.html"]:
    url = f"{BASE}/ar/{page}"
    head_code, final_code, final_url = curl_url(url)
    status = "OK" if final_code == "200" else "FAIL"
    print(f"  [{status}] {final_code}  {url}" + (f" -> {final_url}" if final_url != url else ""))

# Test assets
print("\n=== ASSETS ===")
for asset in ["assets/css/style.css", "assets/js/app.js", "assets/img/favicon.svg",
              "assets/img/og-image.svg", "assets/img/avatar-placeholder.svg",
              "assets/img/hero-tile-1.svg", "assets/img/hero-tile-2.svg"]:
    url = f"{BASE}/{asset}"
    head_code, final_code, final_url = curl_url(url)
    status = "OK" if final_code == "200" else "FAIL"
    print(f"  [{status}] {final_code}  {url}")
