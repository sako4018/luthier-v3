#!/usr/bin/env python3
"""Generate the single-language pages from the bilingual sources in tools/src/.

The sources hold both languages (.t-bg / .t-en spans). This script writes the
Bulgarian pages to the repo root and the English pages to en/. Each output file
contains only one language, so search engines see clean, separate pages.

Edit the files in tools/src/, never the generated pages, then run:
    python3 tools/build-en.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "tools" / "src"
BASE = "https://bulgarian-violins.com/"

EN = {
    "index.html": (
        "Stepan Demirdjian — Violin Maker, Plovdiv",
        "Handmade violins and violas by luthier Stepan Demirdjian in Plovdiv, Bulgaria. Instruments made to order, repair and restoration of string instruments.",
    ),
    "about.html": (
        "About — Stepan Demirdjian, Violin Maker",
        "Stepan Demirdjian, luthier in Plovdiv, Bulgaria. A workshop for making, repairing and restoring violins and violas.",
    ),
    "instrument.html": (
        "Handmade Violins & Violas — Plovdiv, Bulgaria",
        "Handmade violins and violas after Stradivari, Guarneri and Amati, made to order by luthier Stepan Demirdjian in Plovdiv, Bulgaria.",
    ),
    "services.html": (
        "Violin Repair & Bow Rehair — Plovdiv, Bulgaria",
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


def keep_language(s, keep):
    """Drop the spans of the other language and unwrap the spans of `keep` ("en" or "bg")."""
    drop = "bg" if keep == "en" else "en"
    tag = re.compile(r'<span class="t-(en|bg)">|<span\b|</span>')
    out, i = [], 0
    while True:
        m = re.compile(r'<span class="t-(en|bg)">').search(s, i)
        if not m:
            out.append(s[i:])
            break
        out.append(s[i:m.start()])
        depth, j = 1, m.end()
        while depth:
            t = tag.search(s, j)
            if t.group(0) == "</span>":
                depth -= 1
            else:
                depth += 1
            j = t.end()
        inner = s[m.end():t.start()]
        if m.group(1) == keep:
            out.append(inner)
        i = j
    return "".join(out)


TEXT = {
    "bg": [
        ('>Skip to main content<', '>Към основното съдържание<'),
        ('aria-label="Switch language / Смени езика"', 'aria-label="Превключи на английски"'),
        ('alt="Stepan Demirdjian — home"', 'alt="Степан Демирджиян — начало"'),
        ('alt="Handmade violin on blue silk"', 'alt="Ръчно изработена цигулка върху синя коприна"'),
        ('alt="Violin, front view, isolated"', 'alt="Цигулка, изглед отпред"'),
        ('alt="Stepan Demirdjian at the workbench"', 'alt="Степан Демирджиян на работната маса"'),
        ('alt="Inspired by Stradivari, front"', 'alt="По модел на Страдивари, отпред"'),
        ('alt="Inspired by Stradivari, scroll"', 'alt="По модел на Страдивари, главичка"'),
        ('alt="Inspired by Stradivari, back"', 'alt="По модел на Страдивари, отзад"'),
        ('alt="Inspired by Guarneri, front"', 'alt="По модел на Гуарнери, отпред"'),
        ('alt="Inspired by Guarneri, back"', 'alt="По модел на Гуарнери, отзад"'),
        ('alt="Viola 16 inch, front"', 'alt="Виола 16 инча, отпред"'),
        ('alt="Viola 16 inch, back"', 'alt="Виола 16 инча, отзад"'),
        ('alt="Viola 15.5 inch, front"', 'alt="Виола 15.5 инча, отпред"'),
        ('alt="Viola 15.5 inch, back"', 'alt="Виола 15.5 инча, отзад"'),
        ('alt="Close-up of a handmade violin scroll"', 'alt="Главичка на ръчно изработена цигулка отблизо"'),
        ('aria-label="Previous testimonial"', 'aria-label="Предишен отзив"'),
        ('aria-label="Next testimonial"', 'aria-label="Следващ отзив"'),
        ('aria-label="Photo, full size"', 'aria-label="Снимка в пълен размер"'),
        ('aria-label="Close"', 'aria-label="Затвори"'),
        ('aria-label="Previous photo"', 'aria-label="Предишна снимка"'),
        ('aria-label="Next photo"', 'aria-label="Следваща снимка"'),
    ],
    "en": [
        ('aria-label="Switch language / Смени езика"', 'aria-label="Switch to Bulgarian"'),
    ],
}


def build_bg(page):
    s = keep_language((SRC / page).read_text(encoding="utf-8"), "bg")
    for a, b in TEXT["bg"]:
        s = s.replace(a, b)
    (ROOT / page).write_text(s, encoding="utf-8")
    print("wrote", page)


def build(page):
    title, desc = EN[page]
    path = "" if page == "index.html" else page
    s = (SRC / page).read_text(encoding="utf-8")

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

    s = re.sub(r'<meta name="keywords" content="[^"]*">\n', "", s)  # the keywords are Bulgarian
    s = keep_language(s, "en")
    for a, b in TEXT["en"]:
        s = s.replace(a, b)

    out = ROOT / "en" / page
    out.parent.mkdir(exist_ok=True)
    out.write_text(s, encoding="utf-8")
    print("wrote", out.relative_to(ROOT))


if __name__ == "__main__":
    for page in EN:
        build_bg(page)
        build(page)
