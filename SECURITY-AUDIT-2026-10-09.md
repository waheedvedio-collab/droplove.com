# SECURITY AUDIT REPORT — DrofLove.com GitHub Pages Deployment

**Date**: 2026-10-09
**Auditor**: Sanjay (Cyber Security Engineer)
**Target**: https://waheedvedio-collab.github.io/droplove.com/
**GitHub Repo**: waheedvedio-collab/droplove.com
**Source Code**: D:\WEBSITE\hostingers\_site (static export)

---

## EXECUTIVE SUMMARY

The DrofLove.com static export has been deployed to GitHub Pages and is serving live content. The deployment is functionally working — all 14 language homepages, public pages, and auth-gated redirect stubs return HTTP 200. **However, a critical security gap exists: the `.htaccess` security hardening (CSP, X-Frame-Options, X-Content-Type-Options, etc.) does NOT apply on GitHub Pages static hosting.** This means the site is missing all application-level security headers.

**Key issue count**: 1 CRITICAL, 2 MEDIUM, 1 LOW

| # | Issue | Severity | Status |
|---|-------|----------|--------|
| 1 | Missing security headers (CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy) on GitHub Pages | CRITICAL | VERIFIED |
| 2 | CSRF token embedded in static HTML (information leakage) | MEDIUM | VERIFIED |
| 3 | Language mismatch: task expects ko/nl, site has ur/bn | LOW | VERIFIED |
| 4 | Footer language selector form non-functional on static hosting | MEDIUM | VERIFIED |

---

## DETAILED FINDINGS

### FINDING 1: Missing Security Headers on GitHub Pages (CRITICAL)

**Severity**: CRITICAL
**Confidence**: CONFIRMED
**Affected component**: All pages served on GitHub Pages (https://waheedvedio-collab.github.io/droplove.com/)
**Source**: .htaccess (lines 10-20) defines security headers that only work on Apache

**Evidence**:
The `.htaccess` file at `D:\WEBSITE\hostingers\.htaccess` defines the following security headers:
```
X-Content-Type-Options: nosniff
X-Frame-Options: SAMEORIGIN
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'; ...
Cross-Origin-Embedder-Policy: require-corp
Cross-Origin-Opener-Policy: same-origin
Cross-Origin-Resource-Policy: same-origin
```

However, HTTP response headers on the live GitHub Pages site show **only** `Strict-Transport-Security` (set by GitHub's CDN). All other security headers are **MISSING**:

```
HTTP/1.1 200 OK
Server: GitHub.com
Content-Type: text/html; charset=utf-8
Strict-Transport-Security: max-age=31556952  ← only this one
Access-Control-Allow-Origin: *
```

Missing headers:
- `X-Frame-Options: SAMEORIGIN` — site can be clickjacked
- `X-Content-Type-Options: nosniff` — MIME-type sniffing attacks possible
- `Referrer-Policy` — referrer leaks to external resources
- `Permissions-Policy` — no control over browser features (camera, mic, geolocation)
- `Content-Security-Policy` — **NO CSP** — XSS attacks are not mitigated
- `Cross-Origin-Embedder-Policy`, `Cross-Origin-Opener-Policy`, `Cross-Origin-Resource-Policy` — no cross-origin isolation

**Impact**: Without CSP, any XSS vulnerability in the static JavaScript (`assets/js/app.js`) would allow arbitrary script execution with no browser-level mitigation. Without X-Frame-Options, the site can be embedded in malicious iframes for clickjacking attacks.

**Attack surface**: All public-facing pages on GitHub Pages

**Reproduction**:
```bash
curl -sI "https://waheedvedio-collab.github.io/droplove.com/" | grep -iE "(content-security|x-frame|x-content|referrer|permissions)"
# Returns: (nothing — all headers missing)
```

**Recommended fix**: Add security headers via GitHub Pages configuration. Options:
1. Add `<meta>` tags to the HTML `<head>` for headers that support meta equivalents:
   - `<meta http-equiv="Content-Security-Policy" content="default-src 'self'; img-src 'self' data: https:; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; script-src 'self' 'unsafe-inline'; connect-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'self'">`
   - `<meta http-equiv="X-Content-Type-Options" content="nosniff">`
   - `<meta http-equiv="Referrer-Policy" content="strict-origin-when-cross-origin">`
   - Note: `X-Frame-Options` can be set via CSP `frame-ancestors` directive
2. Alternatively, serve via a CDN (Cloudflare, etc.) that can inject headers

**Validation**: After adding meta tags, verify with:
```bash
curl -s "https://waheedvedio-collab.github.io/droplove.com/" | grep -i "http-equiv"
```

**Status**: OPEN — fix not yet implemented

---

### FINDING 2: CSRF Token Embedded in Static HTML (MEDIUM)

**Severity**: MEDIUM
**Confidence**: CONFIRMED
**Affected component**: `index.html`, `login.html`, and all other pages containing `<meta name="csrf-token">`
**Source**: View templates (views/*.php)

**Evidence**:
Every HTML page in the static export contains a CSRF token meta tag:
```html
<meta name="csrf-token" content="2cc6edf594f909b970285594d27cedfeb7cfb4ed0925619f8de0fbf3f826778c">
```

The token differs per page (baked at export time, not generated dynamically):
- Homepage: `2cc6edf594f909b970285594d27cedfeb7cfb4ed0925619f8de0fbf3f826778c`
- Login page: `fd800d3c6d8cb723390ea4c1f7b92b0be2bb2bced7a026c43ea5b5a6d1dc51d5`

Since the site is static-hosted on GitHub Pages, there is no server-side session validation. The CSRF token is informational only — any form submission would go to the live PHP application at `droflove.com`, not to GitHub Pages.

**Impact**: Low practical impact on GitHub Pages (no server-side processing), but the token is visible to anyone viewing page source, which could be leveraged in a more complex attack scenario if the live app reuses the same token mechanism.

**Reproduction**:
```bash
curl -s "https://waheedvedio-collab.github.io/droplove.com/" | grep csrf-token
```

**Recommended fix**: Remove the `<meta name="csrf-token">` tag from static export pages. CSRF protection is handled by the live PHP application, not by the static landing pages. The token is only meaningful when the form POSTs to a server that validates it.

**Validation**: After removal, verify no `csrf-token` meta tags exist in HTML.

**Status**: OPEN — fix not yet implemented

---

### FINDING 3: Language Discrepancy — ko/nl Missing (LOW)

**Severity**: LOW
**Confidence**: CONFIRMED
**Affected component**: Language directory structure in static export
**Source**: Task specification vs. config.php LANGS definition

**Evidence**:
The task body specifies 14 languages: `en, fr, ar, es, de, it, pt, tr, ru, zh, ja, ko, hi, nl`

The site's `config.php` (line 39-47) and the actual static export define: `en, fr, es, de, it, pt, ru, hi, zh, ja, tr, ar, ur, bn`

| Language | Task expects | Site has | Status |
|----------|-------------|----------|--------|
| ko (Korean) | Yes | **No** | 404 |
| nl (Dutch) | Yes | **No** | 404 |
| ur (Urdu) | No | Yes | Extra |
| bn (Bengali) | No | Yes | Extra |

The site header itself states "14 languages" and lists: English, Français, Español, Deutsch, Italiano, Português, Русский, हिन्दी, 中文, 日本語, Türkce, العربية, اردو, বাংলা.

This is a content/spec mismatch, not a technical bug. The site is internally consistent (its own 14 languages all work).

**Reproduction**:
```bash
curl -sI "https://waheedvedio-collab.github.io/droplove.com/ko/"   # HTTP 404
curl -sI "https://waheedvedio-collab.github.io/droplove.com/nl/"   # HTTP 404
```

**Recommended fix**: If ko (Korean) and nl (Dutch) are required, add them to the `LANGS` array in `config.php` and the export script's `LANGUAGES` list. If ur/bn were intentionally substituted, update the task spec.

**Status**: INFO — needs decision on whether to add ko/nl

---

### FINDING 4: Footer Language Selector Non-functional on Static Hosting (MEDIUM)

**Severity**: MEDIUM
**Confidence**: CONFIRMED
**Affected component**: Footer language form in all HTML pages
**Source**: `views/footer.php` rendered as static HTML

**Evidence**:
The footer contains a language switcher form:
```html
<form method="get" action="./" class="lang-form">
  <select name="lang" class="lang-select" onchange="this.form.submit()">
    <option value="en" selected>English</option>
    ...
  </select>
</form>
```

On the live PHP application, submitting this form triggers `?lang=fr` which the server processes to switch languages. On GitHub Pages (static hosting), this form submits to `./` with `?lang=fr`, but:
1. There is no server-side PHP to process the `?lang` parameter
2. GitHub Pages returns the default English `index.html`, not the French version
3. The form action `./` on non-root pages resolves to `../` which may cause unexpected navigation

The same issue affects the header language dropdown (which uses `<a href="...">` links — these DO work on static hosting because the export script converts `?lang=fr` to `./fr/`).

**Impact**: Users on static pages cannot switch languages via the footer form. The header language links work correctly.

**Reproduction**:
1. Visit https://waheedvedio-collab.github.io/droplove.com/
2. Select "Français" from the footer dropdown
3. The page reloads but stays in English (no server to process `?lang=fr`)

**Recommended fix**: Convert the footer language form to use the same `<a href>` link approach as the header language dropdown, or add JavaScript to intercept the form submission and redirect to the correct language subdirectory.

**Status**: OPEN — fix not yet implemented

---

## VERIFICATION RESULTS

### Public Pages (HTTP status codes on live GitHub Pages)

| Page | Status | Notes |
|------|--------|-------|
| / | 200 | Homepage loaded |
| /login.html | 200 | Loaded |
| /register.html | 200 | Loaded |
| /terms.html | 200 | Loaded |
| /privacy.html | 200 | Loaded |
| /contact.html | 200 | Loaded |
| /404.html | 200 | Custom 404 page served |
| /nonexistent | 404 | Correctly returns 404 with custom page |

### Auth-Gated Pages (HTTP status codes)

| Page | Status | Notes |
|------|--------|-------|
| /discover.html | 200 | Redirect stub → `./` |
| /dashboard.html | 200 | Redirect stub → `./` |
| /admin.html | 200 | Redirect stub → `./` |
| /messages.html | 200 | Redirect stub → `./` |
| /profile.html | 200 | Redirect stub → `./` |
| /edit_profile.html | 200 | Redirect stub → `./` |

All auth-gated pages return HTTP 200 (not 404) with redirect stubs — **VERIFIED CORRECT**.

### All 14 Languages (homepage status)

| Language | Code | Status |
|----------|------|--------|
| English | en | 200 (root) |
| French | fr | 200 |
| Spanish | es | 200 |
| German | de | 200 |
| Italian | it | 200 |
| Portuguese | pt | 200 |
| Russian | ru | 200 |
| Hindi | hi | 200 |
| Chinese | zh | 200 |
| Japanese | ja | 200 |
| Turkish | tr | 200 |
| Arabic | ar | 200 |
| Urdu | ur | 200 |
| Bengali | bn | 200 |

All 14 languages load successfully — **VERIFIED CORRECT**.

### Sensitive File Exposure Check

| File | Expected | Actual | Status |
|------|----------|--------|--------|
| config.php | 404 | 404 | SAFE |
| db.php | 404 | 404 | SAFE |
| dbcheck.php | 404 | 404 | SAFE |
| admin.php | 404 | 404 | SAFE |
| helpers.php | 404 | 404 | SAFE |
| .env | 404 | 404 | SAFE |
| data/vk_match.db | 404 | 404 | SAFE |
| data/used_keys.txt | 404 | 404 | SAFE |
| .git/config | 404 | 404 | SAFE |
| .git/HEAD | 404 | 404 | SAFE |
| .htaccess | 404 | 404 | SAFE |
| .dev/* (all dev scripts) | 404 | 404 | SAFE |

**All sensitive files are properly blocked. No sensitive file leakage detected.**

### .htaccess Redirect Functionality

The `.htaccess` file in the source directory contains Apache directives (RewriteRule, etc.) but:
- The `.htaccess` file is **NOT tracked** in the git repository (confirmed via `git ls-files`)
- GitHub Pages does **NOT** support `.htaccess` files or Apache mod_rewrite
- The `.htaccess` redirects are therefore **not functional** on GitHub Pages

However, the export script (`export.py`) handles URL conversion at build time:
- `/login.php` → `/login.html` (all links rewritten)
- `/?lang=fr` → `/fr/` (language switcher links rewritten)
- Auth-gated pages get static redirect stubs with `<meta http-equiv="refresh">`

**The redirect strategy is sound except for the footer language form (see Finding 4).**

---

## REGRESSION CHECK

Compared to the previous audit (t_cdd11323, COMBINED-REPORT-2026-10-09):

| Previous Issue | Previous Status | Current Status | Notes |
|----------------|----------------|----------------|-------|
| dbcheck.php returns 404 stub | VERIFIED FIXED | VERIFIED | Not in static export, returns 404 |
| config.php accessible | VERIFIED FIXED | VERIFIED | Returns 404 on GitHub Pages |
| .git/config accessible | Was local only test | VERIFIED | Not in git repo, returns 404 on Pages |
| CSRF protection | Was on live app | PARTIAL | Token in static HTML (Finding 2) |
| Security headers | Was .htaccess-based | BROKEN | .htaccess doesn't work on GitHub Pages |
| Language switching bug (footer form action="/") | VERIFIED FIXED | PARTIAL | Root fixed, but footer form still non-functional (Finding 4) |
| Missing ko, nl languages | N/A (was ur/bn) | VERIFIED | Discrepancy with task spec |

---

## RECOMMENDATIONS

1. **[CRITICAL] Add security headers via `<meta>` tags** in the HTML templates (or use a `_headers` file if using a CDN proxy). At minimum add CSP and X-Content-Type-Options meta tags to the page `<head>`.

2. **[MEDIUM] Remove CSRF token from static HTML** — it serves no purpose on static hosting and leaks information.

3. **[MEDIUM] Fix footer language selector** — convert the GET form to use `<a href>` links matching the header language dropdown, or add JS to redirect to `{lang}/` subdirectories.

4. **[LOW] Resolve language discrepancy** — either add ko/nl to the language set, or confirm that ur/bn are the intended 14 languages and update the task specification.

5. **[INFO] Document the .htaccess limitation** — add a note that `.htaccess` security hardening only applies on the Apache/Hostinger deployment, not on GitHub Pages static hosting.
