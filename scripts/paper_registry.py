"""
Paper Registry — immutable paper identity for the math recovery pipeline.

arxiv_id alone is doing foreign-key work across every experiment. This module
formalizes it: version, categories, title, authors, date, canonical URLs.

Metadata sources, in priority order (verified against live arxiv HTML):
  1. The arXiv stamp printed in the paper text:
       "arXiv:2006.11239v2 [cs.LG] 26 Jun 2020"
     This is authoritative for id/version/primary category/date.
  2. <h1 class="ltx_title"> for the title.
  3. <span class="ltx_personname"> for authors.
  4. The arxiv API (export.arxiv.org) as an optional enrichment.

NOTE: arxiv HTML carries only two <meta> tags (content-type, viewport) —
there is no citation_* metadata. Do not look for it.
"""
import re, json, sys, urllib.request
from pathlib import Path


# arXiv stamp: "arXiv:2006.11239v2 [cs.LG] 26 Jun 2020"
STAMP_RE = re.compile(
    r"arXiv:\s*(?P<id>\d{4}\.\d{4,5})"
    r"(?:v(?P<version>\d+))?"
    r"\s*\[(?P<primary>[a-zA-Z\-]+\.[A-Za-z\-]+)\]"
    r"(?:\s*(?P<date>\d{1,2}\s+[A-Z][a-z]{2}\s+\d{4}))?"
)

# The stamp sometimes prints all categories: "[cs.LG, stat.ML]"
STAMP_CATS_RE = re.compile(
    r"arXiv:\s*\d{4}\.\d{4,5}(?:v\d+)?\s*\[(?P<cats>[^\]]+)\]"
)


def _text(html):
    from bs4 import BeautifulSoup
    return BeautifulSoup(html, "html.parser")


def extract_paper_identity(html, arxiv_id=None):
    """
    Extract the immutable paper identity from arxiv HTML.

    Returns dict with: arxiv_id, version, primary_category, categories,
    title, authors, date, canonical_abs, canonical_html, stamp (raw).
    Missing fields are None — never guessed.
    """
    soup = _text(html)

    ident = {
        "arxiv_id": arxiv_id,
        "version": None,
        "primary_category": None,
        "categories": [],
        "title": None,
        "authors": [],
        "date": None,
        "canonical_abs": None,
        "canonical_html": None,
        "stamp": None,
    }

    # --- 1. the arXiv stamp (authoritative for id/version/category/date)
    full_text = soup.get_text(" ", strip=True)
    m = STAMP_RE.search(full_text)
    if m:
        ident["stamp"] = m.group(0)
        ident["arxiv_id"] = m.group("id")
        ident["version"] = f"v{m.group('version')}" if m.group("version") else None
        ident["primary_category"] = m.group("primary")
        ident["categories"] = [m.group("primary")]
        if m.group("date"):
            ident["date"] = m.group("date")

    # multi-category stamp overrides the single-category list
    mc = STAMP_CATS_RE.search(full_text)
    if mc:
        cats = [c.strip() for c in mc.group("cats").split(",") if c.strip()]
        if cats:
            ident["categories"] = cats
            if not ident["primary_category"]:
                ident["primary_category"] = cats[0]

    # fall back to the supplied id if the stamp was absent
    if not ident["arxiv_id"]:
        ident["arxiv_id"] = arxiv_id

    # --- 2. title
    t = soup.find(["h1"], class_=lambda c: isinstance(c, str) and "ltx_title" in c)
    if t:
        ident["title"] = t.get_text(" ", strip=True)
    elif soup.title:
        ident["title"] = soup.title.get_text(strip=True)

    # --- 3. authors
    for sp in soup.find_all("span", class_=lambda c: isinstance(c, str) and "ltx_personname" in c):
        name = sp.get_text(" ", strip=True)
        if name:
            ident["authors"].append(name)

    # --- 4. canonical URLs
    if ident["arxiv_id"]:
        ident["canonical_abs"] = f"https://arxiv.org/abs/{ident['arxiv_id']}"
        ident["canonical_html"] = f"https://arxiv.org/html/{ident['arxiv_id']}"

    return ident


def enrich_from_api(arxiv_id, timeout=20):
    """
    Optional: pull full category list + published/updated dates from the
    arxiv API. Returns dict of extra fields, or {} on failure.
    """
    url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "paper-registry/1.0"})
        xml = urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "replace")
    except Exception as e:
        return {"api_error": f"{type(e).__name__}"}

    out = {}
    prim = re.search(r'<arxiv:primary_category[^>]*term="([^"]+)"', xml)
    if prim:
        out["primary_category"] = prim.group(1)
    cats = re.findall(r'<category[^>]*term="([^"]+)"', xml)
    if cats:
        out["categories"] = cats
    pub = re.search(r"<published>([^<]+)</published>", xml)
    if pub:
        out["published"] = pub.group(1)
    upd = re.search(r"<updated>([^<]+)</updated>", xml)
    if upd:
        out["updated"] = upd.group(1)
    return out


def build_registry(corpus_dir=None, use_api=False):
    """
    Build the registry from the local HTML corpus (and optionally the API).

    Returns {arxiv_id: identity_dict}
    """
    registry = {}
    if not corpus_dir:
        return registry

    for f in sorted(Path(corpus_dir).glob("*.json")):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        aid = d.get("arxiv_id") or f.stem

        # the corpus stores structure{title,authors}, not the raw HTML
        ident = {
            "arxiv_id": aid,
            "version": d.get("version"),
            "primary_category": None,
            "categories": [],
            "title": (d.get("structure") or {}).get("title"),
            "authors": (d.get("structure") or {}).get("authors", []),
            "date": None,
            "canonical_abs": f"https://arxiv.org/abs/{aid}",
            "canonical_html": f"https://arxiv.org/html/{aid}",
            "stamp": None,
            "equation_count": d.get("equation_count"),
            "source_file": str(f),
        }
        if use_api:
            ident.update(enrich_from_api(aid))
        registry[aid] = ident

    return registry


if __name__ == "__main__":
    corpus = "DATASETS/arxiv_html_corpus"
    reg = build_registry(corpus, use_api=("--api" in sys.argv))

    out = Path("DATASETS/paper_registry.json")
    out.write_text(json.dumps(reg, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"PAPER REGISTRY — {len(reg)} papers")
    print("=" * 78)
    for aid, p in reg.items():
        cats = ",".join(p.get("categories") or []) or "?"
        print(f"  {aid:12s} {p.get('version') or '?':4s} [{cats:16s}] "
              f"eq={p.get('equation_count') or 0:5d}  {(p.get('title') or '')[:44]}")
    print()
    print(f"wrote {out}")
