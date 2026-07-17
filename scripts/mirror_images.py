#!/usr/bin/env python3
"""
Scarica tutte le immagini dal vecchio WordPress e aggiorna i riferimenti
in tutti i file CSS e HTML del sito statico.
"""
import os
import re
import urllib.request
import urllib.error
import hashlib
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).parent.parent
IMG_DIR = ROOT / "img"
IMG_DIR.mkdir(exist_ok=True)

EXTENSIONS = ('.jpg', '.jpeg', '.png', '.webp', '.gif', '.svg')

def extract_urls_from_files():
    """Estrae tutte le URL uniche di immagini dai file HTML e CSS."""
    urls = set()
    pattern = re.compile(
        r'https?://www\.caladeibalcani\.(it|com)/[^\s"\')\]>]+(?:' +
        '|'.join(re.escape(e) for e in EXTENSIONS) + r')',
        re.IGNORECASE
    )
    for ext in ('*.html', '*.css'):
        for fpath in ROOT.rglob(ext):
            text = fpath.read_text(encoding='utf-8', errors='ignore')
            urls.update(pattern.findall_all(text) if hasattr(pattern, 'findall_all') else pattern.findall(text))
    return urls

def extract_urls_from_files_v2():
    """Estrae tutte le URL uniche di immagini dai file HTML e CSS."""
    urls = set()
    pattern = re.compile(
        r'https?://www\.caladeibalcani\.(it|com)/[^\s"\')\]>]+'
    )
    ext_pattern = re.compile(r'\.(jpg|jpeg|png|webp|gif|svg)(\?[^\s"\')\]>]*)?$', re.IGNORECASE)

    for ext in ('*.html', '*.css'):
        for fpath in ROOT.rglob(ext):
            text = fpath.read_text(encoding='utf-8', errors='ignore')
            for match in pattern.finditer(text):
                url = match.group(0)
                # Rimuove parametri query e frammenti
                url = re.sub(r'["\'\)\]\s>].*$', '', url)
                if ext_pattern.search(url):
                    urls.add(url)
    return urls

def url_to_local_name(url):
    """Converte una URL in un nome file locale."""
    parsed = urlparse(url)
    path = parsed.path

    # Già nella cartella img/ del sito
    if path.startswith('/img/'):
        return path[len('/img/'):]

    # wp-content: usa solo il filename originale
    filename = os.path.basename(path)
    # Rimuove dimensioni tipo -768x512, -1024x683, -scaled
    # Ma manteniamo il nome originale per evitare collisioni
    return filename

def download_image(url, local_name):
    """Scarica un'immagine e la salva in img/. Ritorna True se ok."""
    dest = IMG_DIR / local_name
    if dest.exists():
        print(f"  ✓ già presente: {local_name}")
        return True

    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; SiteMirror/1.0)',
        'Referer': 'https://www.caladeibalcani.it/',
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as resp:
            content = resp.read()
        dest.write_bytes(content)
        size_kb = len(content) // 1024
        print(f"  ↓ scaricata: {local_name} ({size_kb} KB)")
        return True
    except Exception as e:
        print(f"  ✗ ERRORE {url}: {e}")
        return False

def build_url_map(urls):
    """
    Costruisce un dizionario url -> nome_locale.
    Gestisce collisioni di nomi aggiungendo un suffisso.
    """
    url_map = {}
    name_count = {}

    for url in sorted(urls):
        name = url_to_local_name(url)
        # Risolvi collisioni
        base, ext = os.path.splitext(name)
        count = name_count.get(name, 0)
        if count > 0:
            final_name = f"{base}_{count}{ext}"
        else:
            final_name = name
        name_count[name] = count + 1
        url_map[url] = final_name

    return url_map

def update_files(url_map):
    """Sostituisce tutte le URL remote con percorsi locali relativi nei file HTML e CSS."""
    updated = []

    for ext in ('*.html', '*.css'):
        for fpath in ROOT.rglob(ext):
            # Determina il prefisso relativo a seconda della profondità
            try:
                rel = fpath.relative_to(ROOT)
                depth = len(rel.parts) - 1  # livelli di directory sopra la root
                prefix = '../' * depth if depth > 0 else ''
            except ValueError:
                prefix = ''

            text = fpath.read_text(encoding='utf-8', errors='ignore')
            original = text

            for url, local_name in url_map.items():
                local_path = f"{prefix}img/{local_name}"
                text = text.replace(url, local_path)

            if text != original:
                fpath.write_text(text, encoding='utf-8')
                updated.append(str(fpath))
                print(f"  ✎ aggiornato: {rel}")

    return updated

def main():
    print("=== Mirror Immagini Cala dei Balcani ===\n")

    print("1. Estrazione URL immagini...")
    urls = extract_urls_from_files_v2()
    print(f"   Trovate {len(urls)} URL uniche\n")

    print("2. Costruzione mappa URL -> nome locale...")
    url_map = build_url_map(urls)

    print("3. Download immagini...")
    ok = 0
    fail = 0
    for url, local_name in sorted(url_map.items()):
        if download_image(url, local_name):
            ok += 1
        else:
            fail += 1
    print(f"\n   Scaricate: {ok} | Errori: {fail}\n")

    print("4. Aggiornamento riferimenti in HTML/CSS...")
    updated = update_files(url_map)
    print(f"\n   File aggiornati: {len(updated)}\n")

    print("=== Completato ===")
    if fail > 0:
        print(f"ATTENZIONE: {fail} immagini non scaricate (vedi errori sopra).")

if __name__ == '__main__':
    main()
