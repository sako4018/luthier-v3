#!/usr/bin/env python3
"""Generate the English pages in en/ from the Bulgarian pages in the repo root.

The root pages are the source: they hold both languages (.t-bg / .t-en spans)
and are served in Bulgarian. This script copies each one to en/, switches it to
English and fixes paths, canonical/og URLs, titles and descriptions.

Run after every change to a root page:  python3 tools/build-en.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://bulgarian-violins.com/"

EN = {
    "index.html": (
        "Stepan Demirdjian — Violin Maker in Plovdiv, Bulgaria | Handmade Violins & Violas",
        "Handmade violins and violas by luthier Stepan Demirdjian in Plovdiv, Bulgaria. Instruments made to order, repair and restoration of string instruments.",
    ),
    "about.html": (
        "About — Stepan Demirdjian, Violin Maker in Plovdiv, Bulgaria",
        "Stepan Demirdjian, luthier in Plovdiv, Bulgaria. A workshop for making, repairing and restoring violins and violas.",
    ),
    "instrument.html": (
        "Handmade Violins & Violas — Stepan Demirdjian, Luthier, Bulgaria",
        "Handmade violins and violas after Stradivari, Guarneri and Amati, made to order by luthier Stepan Demirdjian in Plovdiv, Bulgaria.",
    ),
    "services.html": (
        "Violin Repair, Bow Rehair & Restoration — Luthier in Plovdiv, Bulgaria",
        "Violin, viola and cello repair and restoration, bow rehairing and setup by luthier Stepan Demirdjian in Plovdiv, Bulgaria.",
    ),
}

HEAD_SCRIPT_BG = "<script>try{if(localStorage.getItem('lang')==='en')location.replace('/en'+location.pathname+location.search+location.hash)}catch(e){}</script>"
HEAD_SCRIPT_EN = "<script>try{if(localStorage.getItem('lang')==='bg')location.replace(location.pathname.replace(/^\\/en(\\/|$)/,'/')+location.search+location.hash)}catch(e){}</script>"


def sub1(pattern, repl, s, page):
    s, n = re.subn(pattern, lambda m: repl, s, count=1)
    if n != 1:
        raise SystemExit(f"{page}: pattern not found: {pattern}")
    return s


def build(page):
    title, desc = EN[page]
    path = "" if page == "index.html" else page
    s = (ROOT / page).read_text(encoding="utf-8")

    s = sub1(r'<html lang="bg" data-lang="bg">', '<html lang="en" data-lang="en">', s, page)
    if HEAD_SCRIPT_BG not in s:
        raise SystemExit(f"{page}: language redirect script not found")
    s = s.replace(HEAD_SCRIPT_BG, HEAD_SCRIPT_EN)

    s = sub1(r"<title>.*?</title>", f"<title>{title}</title>", s, page)
    s = sub1(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{desc}">', s, page)
    s = sub1(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{title}">', s, page)
    s = sub1(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{desc}">', s, page)
    s = sub1(r'<meta property="og:locale" content="[^"]*">', '<meta property="og:locale" content="en_GB">', s, page)
    s = sub1(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{BASE}en/{path}">', s, page)
    s = sub1(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{BASE}en/{path}">', s, page)

    # Relative asset paths: en/ is one level deeper. Page links (index.html etc.) stay relative so they remain in en/.
    s = s.replace('src="photos/', 'src="../photos/')
    s = s.replace('href="photos/', 'href="../photos/')
    s = s.replace('href="styles.css"', 'href="../styles.css"')
    s = s.replace("'photos/' +", "'../photos/' +")

    out = ROOT / "en" / page
    out.parent.mkdir(exist_ok=True)
    out.write_text(s, encoding="utf-8")
    print("wrote", out.relative_to(ROOT))


if __name__ == "__main__":
    for page in EN:
        build(page)
