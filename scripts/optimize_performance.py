#!/usr/bin/env python3
"""
ING-342 — Performance optimization: WebP, CSS/JS minification, HTML updates.
Run once from repo root: python3 scripts/optimize_performance.py
"""

import os
import re
from pathlib import Path
from PIL import Image

REPO = Path(__file__).parent.parent
IMG_DIR = REPO / 'img'
CSS_SRC = REPO / 'css' / 'style.css'
CSS_MIN = REPO / 'css' / 'style.min.css'
JS_SRC  = REPO / 'js' / 'main.js'
JS_MIN  = REPO / 'js' / 'main.min.js'


# ── 1. Convert all JPG/PNG → WebP ───────────────────────────────────────────

print("=== 1/4  Converting images to WebP ===")
converted = 0
skipped   = 0
saved_kb  = 0

for p in sorted(IMG_DIR.iterdir()):
    if p.suffix.lower() not in ('.jpg', '.jpeg', '.png'):
        continue
    webp = p.with_suffix('.webp')
    if webp.exists():
        skipped += 1
        continue
    try:
        with Image.open(p) as img:
            if img.mode in ('RGBA', 'LA', 'P'):
                bg = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                if img.mode in ('RGBA', 'LA'):
                    bg.paste(img, mask=img.split()[-1])
                img = bg
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            img.save(webp, 'WEBP', quality=82, method=4)
        orig = p.stat().st_size
        new  = webp.stat().st_size
        saved_kb += (orig - new) // 1024
        converted += 1
        print(f"  {p.name}: {orig//1024}KB → {new//1024}KB  (-{100*(orig-new)//orig}%)")
    except Exception as exc:
        print(f"  ERROR {p.name}: {exc}")

print(f"  Done: {converted} converted, {skipped} already existed, {saved_kb}KB saved\n")


# ── 2. Minify CSS ────────────────────────────────────────────────────────────

print("=== 2/4  Minifying CSS ===")

def minify_css(src: str) -> str:
    # Remove block comments
    out = re.sub(r'/\*[\s\S]*?\*/', '', src)
    # Collapse tabs/spaces to single space (preserve newlines briefly)
    out = re.sub(r'[ \t]+', ' ', out)
    # Remove space around CSS punctuation (not inside strings — simple but good enough)
    out = re.sub(r' *([\{\};,>~+]) *', r'\1', out)
    # Colon: only between property and value, not inside url() or image-set()
    # Safe: remove space after : except inside parentheses — too complex, skip colon squeeze
    # Instead just compress newlines
    out = re.sub(r'\n+', '', out)
    # Remove trailing semicolons before }
    out = out.replace(';}', '}')
    return out.strip()

css_src_text = CSS_SRC.read_text('utf-8')
CSS_MIN.write_text(minify_css(css_src_text), 'utf-8')
print(f"  style.css: {CSS_SRC.stat().st_size//1024}KB → {CSS_MIN.stat().st_size//1024}KB\n")


# ── 3. Update CSS: add image-set() WebP for background-image JPG/PNG refs ───

print("=== 3/4  Updating CSS background-image to image-set() ===")

def add_webp_imageset(line: str) -> str:
    """
    Transforms:
      url('../img/foo.jpg')
    into:
      image-set(url('../img/foo.webp') type("image/webp"),url('../img/foo.jpg') type("image/jpeg"))
    Skips URLs that are already WebP or remote.
    """
    def replace_url(m):
        raw = m.group(1)
        low = raw.lower()
        if low.startswith('http') or low.endswith('.webp'):
            return m.group(0)
        base, ext = os.path.splitext(raw)
        webp = base + '.webp'
        fmt  = 'image/jpeg' if ext.lower() in ('.jpg', '.jpeg') else 'image/png'
        return (
            f'image-set(url("{webp}") type("image/webp"),'
            f'url("{raw}") type("{fmt}"))'
        )
    # Only transform url() calls that hold an image path
    return re.sub(r"url\(['\"]([^'\"]+\.(jpg|jpeg|png))['\"]?\)", replace_url, line,
                  flags=re.IGNORECASE)

css_lines   = css_src_text.split('\n')
updated     = []
bg_count    = 0
for line in css_lines:
    if 'background-image:' in line and re.search(r"url\(['\"]?[^)]+\.(jpg|jpeg|png)['\"]?\)",
                                                   line, re.IGNORECASE):
        # Don't double-transform
        if 'image-set(' not in line:
            new_line = add_webp_imageset(line)
            updated.append(new_line)
            bg_count += 1
            print(f"  ✓ {line.strip()[:70]}")
            continue
    updated.append(line)

new_css_src = '\n'.join(updated)
CSS_SRC.write_text(new_css_src, 'utf-8')
# Re-minify with updated content
CSS_MIN.write_text(minify_css(new_css_src), 'utf-8')
print(f"  {bg_count} background-image declarations updated; re-minified style.min.css\n")


# ── 4. Minify JS ─────────────────────────────────────────────────────────────

print("=== (JS) Minifying JS ===")

def minify_js(src: str) -> str:
    # Remove block comments
    out = re.sub(r'/\*[\s\S]*?\*/', '', src)
    lines_out = []
    for ln in out.split('\n'):
        stripped = ln.strip()
        if not stripped or stripped.startswith('//'):
            continue
        lines_out.append(stripped)
    return '\n'.join(lines_out)

JS_MIN.write_text(minify_js(JS_SRC.read_text('utf-8')), 'utf-8')
print(f"  main.js: {JS_SRC.stat().st_size//1024}KB → {JS_MIN.stat().st_size//1024}KB\n")


# ── 5. Update HTML files ─────────────────────────────────────────────────────

print("=== 4/4  Updating HTML files ===")

HTML_FILES = sorted(REPO.rglob('*.html'))

# CSS/JS path pairs: (old, new) — handle both root and subdirectory variants
CSS_PAIRS = [
    ('href="css/style.css"',    'href="css/style.min.css"'),
    ("href='css/style.css'",    "href='css/style.min.css'"),
    ('href="../css/style.css"', 'href="../css/style.min.css"'),
    ("href='../css/style.css'", "href='../css/style.min.css'"),
]
JS_PAIRS = [
    ('src="js/main.js"',    'src="js/main.min.js"'),
    ("src='js/main.js'",    "src='js/main.min.js'"),
    ('src="../js/main.js"', 'src="../js/main.min.js"'),
    ("src='../js/main.js'", "src='../js/main.min.js'"),
]

def wrap_imgs_in_picture(html: str) -> tuple[str, int]:
    """
    Wraps <img src="…img/….jpg"> in <picture><source webp>…</picture>.
    Skips images already inside <picture> and non-local / non-JPG/PNG refs.
    """
    result   = []
    i        = 0
    wrapped  = 0
    length   = len(html)

    while i < length:
        pic_pos = html.find('<picture', i)
        img_pos = html.find('<img ', i)

        if img_pos == -1:
            result.append(html[i:])
            break

        if pic_pos != -1 and pic_pos < img_pos:
            # Consume the entire <picture>…</picture> block unchanged
            pic_end = html.find('</picture>', pic_pos)
            if pic_end == -1:
                result.append(html[i:])
                break
            result.append(html[i: pic_end + len('</picture>')])
            i = pic_end + len('</picture>')
            continue

        # Parse the <img …> tag, respecting quoted attributes
        end = img_pos + 5
        in_q = None
        while end < length:
            c = html[end]
            if c in ('"', "'") and in_q is None:
                in_q = c
            elif c == in_q:
                in_q = None
            elif c == '>' and in_q is None:
                end += 1
                break
            end += 1

        tag = html[img_pos:end]
        src_m = re.search(r'\bsrc=["\']([^"\']+)["\']', tag)
        if src_m:
            src = src_m.group(1)
            low = src.lower()
            if (('img/' in src or src.startswith('/img/'))
                    and low.endswith(('.jpg', '.jpeg', '.png'))
                    and not src.startswith('http')):
                base, _ = os.path.splitext(src)
                webp_src = base + '.webp'
                result.append(html[i:img_pos])
                result.append(
                    f'<picture>'
                    f'<source srcset="{webp_src}" type="image/webp">'
                    f'{tag}'
                    f'</picture>'
                )
                i = end
                wrapped += 1
                continue

        result.append(html[i:end])
        i = end

    return ''.join(result), wrapped

total_files   = 0
total_wrapped = 0

for html_file in HTML_FILES:
    text     = html_file.read_text('utf-8')
    original = text

    # Update CSS/JS refs
    for old, new in CSS_PAIRS + JS_PAIRS:
        text = text.replace(old, new)

    # Wrap <img> tags
    text, wrapped = wrap_imgs_in_picture(text)
    total_wrapped += wrapped

    if text != original:
        html_file.write_text(text, 'utf-8')
        total_files += 1
        print(f"  {html_file.relative_to(REPO)} — {wrapped} imgs wrapped")

print(f"\n  {total_files} HTML files updated, {total_wrapped} <img> tags wrapped in <picture>\n")
print("=== All done! ===")
