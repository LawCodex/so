#!/usr/bin/env python3
"""Somalia: Provisional Constitution (2012) and the laws published in the document library of the
Federal Parliament of Somalia (parliament.gov.so, WordPress REST API post type dlp_document).
Only PDFs with a usable text layer are converted (no Somali OCR model is available).

Usage: python3 so_fetch.py [--no-download]"""
import html
import json
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import so_text as T  # noqa

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(os.path.dirname(REPO), "_raw", "so")
RETRIEVED = os.environ.get("LC_RETRIEVED", "2026-10-13")
API = "https://parliament.gov.so/wp-json/wp/v2/dlp_document?per_page=100&page=%d&_fields=id,title,link,date,download_url,filename"
DL = "--no-download" not in sys.argv
KEEP = re.compile(r"^(\d+\s+)?(Sharciga|Wax ka bed[ae]l|Xeerka|Ansixinta Sharciga|Ansixint wax ka badelka Sharciga|Provisional Constitution|Dastuur|Axdiga|\d{4}_somali_constitution|1949_constitution)", re.I)
SO = {"iyo", "ee", "ka", "ku", "waa", "oo", "ah", "u", "la", "sharciga", "qodobka", "in", "ay", "loo"}
EN = {"the", "of", "and", "shall", "to", "in", "or", "be", "any", "by", "this", "article"}


NICE = {"1990 somali constitution english": "Constitution of the Somali Democratic Republic, 1990 (English)",
        "1960 somali constitution english": "Constitution of the Somali Republic, 1960 (English)",
        "1949 constitution un annexure": "Constitution of 1949 (UN Trusteeship Agreement annex)",
        "Provisional Constitution 2012": "Provisional Constitution of the Federal Republic of Somalia, 2012",
        "Dastuurka ku meelgaarka": "Dastuurka Ku-meelgaarka ah ee Jamhuuriyadda Federaalka Soomaaliya (2012)"}


def listing():
    p = os.path.join(RAW, "docs.json")
    if DL or not os.path.exists(p):
        out = []
        for pg in (1, 2, 3, 4):
            q = os.path.join(RAW, "list-%d.json" % pg)
            if not T.fetch(API % pg, q, delay=3):
                break
            d = json.load(open(q))
            if not isinstance(d, list) or not d:
                break
            out += d
        json.dump(out, open(p, "w"), ensure_ascii=False, indent=1)
    return json.load(open(p))


def lang_of(text):
    w = Counter(re.findall(r"[a-z]+", text.lower()))
    return "so" if sum(w[x] for x in SO) > sum(w[x] for x in EN) else "en"


def main():
    n = Counter()
    for d in listing():
        title = re.sub(r"\s+", " ", html.unescape(d["title"]["rendered"])).strip()
        if not KEEP.match(title) or not d.get("download_url", "").lower().endswith(".pdf"):
            continue
        pdf = os.path.join(RAW, "pdf", "%s.pdf" % d["id"])
        if DL:
            T.fetch(d["download_url"], pdf, delay=3, check_pdf=True)
        if not os.path.exists(pdf) or not T.pdf_ok(pdf):
            print("MISSING", title)
            n["missing"] += 1
            continue
        pages, _ = T.pdf_text(pdf, "eng", ocr=False)
        txt = "\n".join(pages)
        good = [p for p in pages if len(p.strip()) > 150]
        if len(good) < max(1, 0.6 * len(pages)) or T.text_quality(txt) < 0.75:
            print("SKIP (scanned / no text layer)", title)
            n["scanned"] += 1
            continue
        lang = lang_of(txt)
        clean = re.sub(r"^\d+\s+", "", title).replace("_", " ").strip()
        clean = re.sub(r"\s+(SOM|ENG)$", "", clean)
        clean = re.sub(r"\s+", " ", clean)
        clean = NICE.get(clean, clean)
        is_const = bool(re.match(r"^(Dastuurka|Axdiga|Provisional Constitution|Constitution)", clean, re.I))
        m = re.search(r"\b(19[4-9]\d|20[0-2]\d)\b", clean)
        year = m.group(1) if m else None
        lines = [x for x in T.clean_pages(pages) if not re.search(r"\.{6,}\s*\d*$", x)]
        if lang == "en":
            lines = T.drop_toc(lines, starts=(r"^Preamble$", r"^PREAMBLE$", r"^In the [Nn]ame of", r"^We,? the [Pp]eople", r"^AN ACT\b", r"^An Act\b"))
            body = [("### " + x) if re.match(r"^Article\s+\d+\.?$", x) else x for x in T.structure(lines, "en", art_word="Article")]
        else:
            body = [("### " + x) if re.match(r"^Qodobka\s+\d+", x) and len(x) < 120 else x
                    for x in T.structure(lines, "en", art_word="Qodobka")]
        meta = {"title": clean, "type": "constitution" if is_const else "act", "jurisdiction": "so", "language": lang,
                "year": int(year) if year else None, "status": "unknown", "source": d["download_url"],
                "source_page": d["link"], "retrieved": RETRIEVED}
        if is_const:
            meta["status"] = "in_force" if ("Provisional Constitution" in clean or "Ku-meelgaarka ah ee Jamhuuriyadda" in clean) else "repealed"
            path = os.path.join(REPO, lang, "constitution", T.slug(clean) + ".md")
        else:
            path = os.path.join(REPO, lang, "laws", T.slug(clean) + ".md")
        T.write_md(path, meta, clean, body)
        n[lang] += 1
        print("ok", lang, clean)
    print(dict(n))


if __name__ == "__main__":
    main()
