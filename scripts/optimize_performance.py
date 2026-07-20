#!/usr/bin/env python3
"""ING-342 — Performance optimization for cala.it.

Applies:
  1. Non-blocking Google Fonts on all 54 HTML files
  2. fetchpriority="high" on LCP preload (index.html IT only)
  3. video preload="none" (index.html IT only) — saves 21 MB on mobile
  4. YouTube dns-prefetch (index.html IT only, has yt-facade)
  Run from repo root or scripts/: python3 scripts/optimize_performance.py
"""

import os
import re
import glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FONT_URL = (
    'https://fonts.googleapis.com/css2?family=Playfair+Display'
    ':ital,wght@0,400;0,500;0,700;1,400&family=Lato:wght@300;400;700'
    '&family=Cormorant+Garamond:ital,wght@0,300;1,300&display=swap'
)

# Matches both attribute orders: href first or rel first
FONT_BLOCKING_RE = re.compile(
    r'<link\b[^>]*?\bhref=["\']' + re.escape(FONT_URL) + r'["\'][^>]*?\brel=["\']stylesheet["\'][^>]*?>|'
    r'<link\b[^>]*?\brel=["\']stylesheet["\'][^>]*?\bhref=["\']' + re.escape(FONT_URL) + r'["\'][^>]*?>',
    re.IGNORECASE | re.DOTALL
)


def async_font_tag(indent='  '):
    return (
        f'{indent}<link rel="preload" as="style" href="{FONT_URL}"'
        f' onload="this.onload=null;this.rel=\'stylesheet\'">\n'
        f'{indent}<noscript><link rel="stylesheet" href="{FONT_URL}"></noscript>'
    )


def fix_fonts(html):
    m = FONT_BLOCKING_RE.search(html)
    if not m:
        return html, False
    pos = m.start()
    line_start = html.rfind('\n', 0, pos) + 1
    indent = re.match(r'(\s*)', html[line_start:]).group(1)
    replacement = async_font_tag(indent)
    new_html = FONT_BLOCKING_RE.sub(replacement, html, count=1)
    return new_html, new_html != html


def fix_lcp_preload(html):
    """Add fetchpriority=high to image preload hints that lack it."""
    new_html = re.sub(
        r'(<link\s+rel=["\']preload["\']\s+as=["\']image["\']\s+href=["\'][^"\']+["\'])(\s*>)',
        r'\1 fetchpriority="high"\2',
        html
    )
    return new_html, new_html != html


def fix_video_preload(html):
    """Switch hero video from preload=metadata to preload=none.
    main.js will re-enable it on desktop only."""
    new_html = re.sub(
        r'(<video\b[^>]+)\bpreload=["\']metadata["\']',
        r'\1preload="none"',
        html,
        flags=re.DOTALL
    )
    return new_html, new_html != html


def add_yt_prefetch(html):
    """Insert YouTube dns-prefetch before fonts preconnect block."""
    if 'ytimg.com' in html:
        return html, False  # already present
    YT_HINTS = (
        '<link rel="dns-prefetch" href="https://i.ytimg.com">\n'
        '  <link rel="dns-prefetch" href="https://www.youtube.com">\n'
        '  '
    )
    anchor = '<link rel="preconnect" href="https://fonts.googleapis.com">'
    if anchor not in html:
        return html, False
    new_html = html.replace(anchor, YT_HINTS + anchor, 1)
    return new_html, new_html != html


def process_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()

    original = html
    changes = []

    html, ch = fix_fonts(html)
    if ch:
        changes.append('non-blocking fonts')

    # IT index-specific fixes
    is_it_index = (
        os.path.basename(path) == 'index.html'
        and os.path.dirname(path) == ROOT
    )
    if is_it_index:
        html, ch = fix_lcp_preload(html)
        if ch:
            changes.append('fetchpriority=high on LCP preload')

        html, ch = fix_video_preload(html)
        if ch:
            changes.append('video preload=none')

        html, ch = add_yt_prefetch(html)
        if ch:
            changes.append('YouTube dns-prefetch')

    if html != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f'  UPDATED {os.path.relpath(path, ROOT)}: {", ".join(changes)}')
        return True

    return False


def main():
    pattern = os.path.join(ROOT, '**', '*.html')
    html_files = [f for f in sorted(glob.glob(pattern, recursive=True))
                  if '/.git/' not in f]

    updated = 0
    for path in html_files:
        if process_file(path):
            updated += 1

    print(f'\nDone. {updated}/{len(html_files)} files updated.')


if __name__ == '__main__':
    main()
