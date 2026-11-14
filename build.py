#!/usr/bin/env python3
"""Builds the site from content/ and static/ into dist/.

Usage:  python3 build.py                 builds the home page (hub) into dist/
        python3 build.py --site fiction  builds the fiction site into dist-fiction/
Needs only Python 3.8+ and the standard library.
"""
import html
import json
import re
import shutil
import sys
from datetime import date, datetime
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
STATIC = ROOT / "static"


def _mode():
    a = sys.argv[1:]
    if "--site" in a:
        i = a.index("--site") + 1
        m = a[i] if i < len(a) else ""
        if m not in ("hub", "law", "fiction"):
            raise SystemExit("Usage: python3 build.py [--site hub|law|fiction]")
        return m
    return "hub"


MODE = _mode()   # "hub" is vishnuprasadv.com, "law" and "fiction" are the subdomain sites
DIST = ROOT / {"hub": "dist", "law": "dist-law", "fiction": "dist-fiction"}[MODE]
LP = "" if MODE == "law" else "/law"   # where law pages sit inside the site being built

SITE = json.loads((ROOT / "site.json").read_text(encoding="utf-8"))
if MODE in ("law", "fiction"):
    SITE.update(json.loads((ROOT / f"site-{MODE}.json").read_text(encoding="utf-8")))
FICTION_URL = SITE.get("fiction_url", "").rstrip("/")   # address of the fiction site
LAW_URL = SITE.get("law_url", "").rstrip("/")           # address of the law site
HOME_URL = SITE.get("home_url", "")                     # the logo on the law and fiction sites links here
BASE = SITE.get("base_path", "").rstrip("/")   # e.g. "/repo-name" for a GitHub project site
URL = SITE.get("site_url", "").rstrip("/")     # e.g. "https://example.com"
SITE.setdefault("description", "")
SITE.setdefault("nav", [])
FICTION_ON = False   # becomes True when at least one fiction piece is published

# Self-hosted fonts. Drop these files into static/fonts/ and they are used automatically.
FONT_FILES = [
    ("Fraunces", "Fraunces-Variable.woff2", "normal", "100 900"),
    ("Fraunces", "Fraunces-Italic-Variable.woff2", "italic", "100 900"),
    ("Source Serif 4", "SourceSerif4-Variable.woff2", "normal", "200 900"),
    ("Source Serif 4", "SourceSerif4-Italic-Variable.woff2", "italic", "200 900"),
    ("Inter", "Inter-Variable.woff2", "normal", "100 900"),
]


# ---------------------------------------------------------------- helpers

def esc(s):
    return html.escape(str(s), quote=True)


def href(path):
    return BASE + path


def abs_url(path):
    return URL + BASE + path


def fmt_date(d):
    return f"{d.day} {d:%B %Y}"


def _scalar(raw):
    raw = raw.strip()
    if len(raw) >= 2 and raw[0] == '"' and raw[-1] == '"':
        try:
            return json.loads(raw)
        except ValueError:
            return raw[1:-1]
    if len(raw) >= 2 and raw[0] == "'" and raw[-1] == "'":
        return raw[1:-1].replace("''", "'")
    return raw


def parse_front_matter(front):
    """Reads the simple 'key: value' YAML that editors write.

    Handles quoted values, long values folded over several lines, and block scalars (| and >).
    """
    meta, key, style, chunks = {}, None, "", []

    def commit():
        if key is None:
            return
        if style.startswith("|"):
            meta[key] = "\n".join(chunks).strip()
        elif style.startswith(">"):
            meta[key] = " ".join(c for c in chunks if c).strip()
        else:
            meta[key] = _scalar(" ".join(chunks))

    for line in front.splitlines():
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if m:
            commit()
            key, rest = m.group(1), m.group(2).strip()
            if re.match(r"^[|>][+-]?$", rest):
                style, chunks = rest, []
            else:
                style, chunks = "", [rest]
        elif key is not None and line.strip():
            chunks.append(line.strip())
    commit()
    return meta


def parse(path):
    """Return (front-matter dict, body text) for a markdown file."""
    text = path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    meta = {}
    m = re.match(r"^---\n(.*?)\n---[ \t]*(?:\n|$)(.*)$", text, re.S)
    if m:
        meta, text = parse_front_matter(m.group(1)), m.group(2)
    return meta, text.strip()


# ---------------------------------------------------------------- markdown

def _site_url(url):
    """Prefix site-relative addresses with base_path; return None for unsafe schemes."""
    if re.match(r"^[a-z][a-z0-9+.\-]*:", url, re.I):
        return url if url.lower().startswith(("http://", "https://", "mailto:")) else None
    if url.startswith("/") and not url.startswith("//"):
        return BASE + url
    return url


def _attr(s):
    return s.replace('"', "&quot;")


def _emphasis(s):
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w_])__(.+?)__(?![\w_])", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", s)
    s = re.sub(r"(?<![\w_])_(?!_)(.+?)(?<!_)_(?![\w_])", r"<em>\1</em>", s)
    return s


def inline(s):
    stash = []

    def keep(markup):
        stash.append(markup)
        return f"\x00{len(stash) - 1}\x00"

    s = re.sub(r"`([^`]+)`", lambda m: keep("<code>" + html.escape(m.group(1), quote=False) + "</code>"), s)
    s = html.escape(s, quote=False)

    def image(m):
        src = _site_url(m.group(2))
        if src is None:
            return ""
        return keep(f'<img src="{_attr(src)}" alt="{_attr(m.group(1))}" loading="lazy">')

    def link(m):
        url = _site_url(m.group(2))
        label = _emphasis(m.group(1))
        if url is None:
            return label
        rel = ' rel="noopener noreferrer"' if url.lower().startswith("http") else ""
        return keep(f'<a href="{_attr(url)}"{rel}>{label}</a>')

    s = re.sub(r'!\[([^\]]*)\]\(([^)\s]+)(?:\s+"[^"]*")?\)', image, s)
    s = re.sub(r'\[([^\]]+)\]\(([^)\s]+)(?:\s+"[^"]*")?\)', link, s)
    s = _emphasis(s)
    while "\x00" in s:
        s = re.sub(r"\x00(\d+)\x00", lambda m: stash[int(m.group(1))], s)
    return s


def markdown(src):
    """Markdown subset: headings, paragraphs, lists, quotes, rules, code, images, links, bold, italics."""
    out, para, ul, ol, quote, code = [], [], [], [], [], None

    def flush():
        nonlocal para, ul, ol, quote
        if para:
            out.append("<p>" + inline(" ".join(para)) + "</p>")
        if ul:
            out.append("<ul>" + "".join(f"<li>{inline(i)}</li>" for i in ul) + "</ul>")
        if ol:
            out.append("<ol>" + "".join(f"<li>{inline(i)}</li>" for i in ol) + "</ol>")
        if quote:
            out.append("<blockquote><p>" + inline(" ".join(quote)) + "</p></blockquote>")
        para, ul, ol, quote = [], [], [], []

    for line in src.splitlines():
        s = line.strip()
        if s.startswith("```"):
            if code is None:
                flush()
                code = []
            else:
                out.append("<pre><code>" + html.escape("\n".join(code), quote=False) + "</code></pre>")
                code = None
            continue
        if code is not None:
            code.append(line)
            continue
        if not s:
            flush()
            continue
        m = re.match(r"^(#{1,4})\s+(.*)$", s)
        if m:
            flush()
            n = max(2, len(m.group(1)))  # the page title is the only h1
            out.append(f"<h{n}>{inline(m.group(2))}</h{n}>")
            continue
        if re.match(r"^(-{3,}|\*{3,}|_{3,})$", s):
            flush()
            out.append("<hr>")
            continue
        m = re.match(r"^[-*+]\s+(.*)$", s)
        if m:
            if para or ol or quote:
                flush()
            ul.append(m.group(1))
            continue
        m = re.match(r"^\d+[.)]\s+(.*)$", s)
        if m:
            if para or ul or quote:
                flush()
            ol.append(m.group(1))
            continue
        m = re.match(r"^>\s?(.*)$", s)
        if m:
            if para or ul or ol:
                flush()
            quote.append(m.group(1))
            continue
        if ul or ol or quote:
            flush()
        para.append(s)
    if code is not None:
        out.append("<pre><code>" + html.escape("\n".join(code), quote=False) + "</code></pre>")
    flush()
    return "\n".join(out)


# ---------------------------------------------------------------- content

def load_articles():
    items = []
    for path in sorted((CONTENT / "articles").glob("*.md")):
        meta, body = parse(path)
        if meta.get("draft", "").lower() == "true":
            continue
        if "title" not in meta:
            raise SystemExit(f"{path.name}: front matter needs a 'title'")
        d = None
        if meta.get("date"):
            try:
                d = datetime.strptime(meta["date"].strip()[:10], "%Y-%m-%d").date()
            except ValueError:
                raise SystemExit(f"{path.name}: date must look like 2026-11-13")
        summary = meta.get("summary", "")
        upd = None
        if meta.get("updated"):
            try:
                upd = datetime.strptime(meta["updated"].strip()[:10], "%Y-%m-%d").date()
            except ValueError:
                raise SystemExit(f"{path.name}: updated must look like 2026-11-13")
        search_desc = meta.get("description", "") or summary
        if len(search_desc) > 160:
            print(f"Note: {path.name}: search description is {len(search_desc)} characters; "
                  "Google usually shows about 155. Add a shorter 'description' to control it.")
        slug = re.sub(r"[^a-z0-9]+", "-", path.stem.lower()).strip("-")
        if any(i["slug"] == slug for i in items):
            raise SystemExit(f"{path.name}: another article already has the address {slug}")
        try:
            weight = int(meta.get("weight", 100))
        except ValueError:
            weight = 100
        items.append({
            "slug": slug,
            "title": meta["title"],
            "topic": meta.get("topic", ""),
            "summary": summary,
            "description": search_desc,
            "updated": upd,
            "blurb": meta.get("blurb", summary),
            "date": d,
            "weight": weight,
            "body": body,
        })
    items.sort(key=lambda a: (-(a["date"].toordinal() if a["date"] else 0), a["weight"], a["slug"]))
    return items


# ---------------------------------------------------------------- fiction content

FORM_LABEL = {"chapter": "Chapter", "story": "Short story", "poem": "Poem"}


def _slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", str(s).lower()).strip("-")


def _fdate(meta, key, fname):
    if not meta.get(key):
        return None
    try:
        return datetime.strptime(meta[key].strip()[:10], "%Y-%m-%d").date()
    except ValueError:
        raise SystemExit(f"{fname}: {key} must look like 2026-11-13")


def _aliases(path, title):
    """Every spelling an editor might store when it points a piece at a series."""
    return {_slugify(path.stem), _slugify(title), path.stem.lower(), path.name.lower(),
            f"content/series/{path.name}".lower(), title.strip().lower()}


def _lookup(value):
    v = str(value).strip().lower()
    return {v, _slugify(v), v.rsplit("/", 1)[-1], _slugify(re.sub(r"\.md$", "", v.rsplit("/", 1)[-1]))}


def load_fiction():
    """Reads content/series and content/pieces. Returns (series, standalone, pieces)."""
    sdir, pdir = CONTENT / "series", CONTENT / "pieces"
    series, hidden = [], set()
    for path in sorted(sdir.glob("*.md")) if sdir.is_dir() else []:
        meta, body = parse(path)
        if "title" not in meta:
            raise SystemExit(f"{path.name}: front matter needs a 'title'")
        al = _aliases(path, meta["title"])
        if meta.get("draft", "").lower() == "true":
            hidden |= al
            continue
        slug = _slugify(path.stem)
        if any(s["slug"] == slug for s in series):
            raise SystemExit(f"{path.name}: another series already has the address /{slug}/")
        try:
            weight = int(meta.get("weight", 100))
        except ValueError:
            weight = 100
        series.append({"slug": slug, "title": meta["title"], "summary": meta.get("summary", ""),
                       "description": meta.get("description", "") or meta.get("summary", ""),
                       "status": meta.get("status", ""), "weight": weight, "body": body,
                       "aliases": al, "pieces": []})

    pieces, standalone = [], []
    for path in sorted(pdir.glob("*.md")) if pdir.is_dir() else []:
        meta, body = parse(path)
        if meta.get("draft", "").lower() == "true":
            continue
        if "title" not in meta:
            raise SystemExit(f"{path.name}: front matter needs a 'title'")
        ref = meta.get("series", "").strip()
        owner = None
        if ref:
            keys = _lookup(ref)
            if keys & hidden:
                continue
            owner = next((s for s in series if keys & s["aliases"]), None)
            if owner is None:
                raise SystemExit(f"{path.name}: the series '{ref}' does not exist. "
                                 "Check the Series field, or leave it empty for a standalone piece.")
        form = (meta.get("form", "") or ("chapter" if owner else "story")).lower()
        if form not in FORM_LABEL:
            raise SystemExit(f"{path.name}: form must be chapter, story or poem")
        try:
            order = int(meta.get("order", 0) or 0)
        except ValueError:
            raise SystemExit(f"{path.name}: order must be a whole number such as 1 or 2")
        slug = _slugify(path.stem)
        item = {"slug": slug, "title": meta["title"], "form": form, "series": owner, "order": order,
                "date": _fdate(meta, "date", path.name), "updated": _fdate(meta, "updated", path.name),
                "summary": meta.get("summary", ""), "body": body}
        item["description"] = meta.get("description", "") or item["summary"]
        item["url"] = f"/{owner['slug']}/{slug}/" if owner else f"/{slug}/"
        pieces.append(item)
        (owner["pieces"] if owner else standalone).append(item)

    taken = {s["slug"] for s in series}
    for a in standalone:
        if a["slug"] in taken:
            raise SystemExit(f"{a['slug']}: a series and a standalone piece share the address /{a['slug']}/")
        taken.add(a["slug"])
    series = [s for s in series if s["pieces"]]
    for s in series:
        seen = set()
        for c in s["pieces"]:
            if c["slug"] in seen:
                raise SystemExit(f"{s['slug']}: two pieces share the address {c['url']}")
            seen.add(c["slug"])
        s["pieces"].sort(key=lambda c: (c["order"], c["date"].toordinal() if c["date"] else 0, c["slug"]))
        s["date"] = max((c["date"] for c in s["pieces"] if c["date"]), default=None)
    series.sort(key=lambda s: (s["weight"], -(s["date"].toordinal() if s["date"] else 0), s["title"]))
    standalone.sort(key=lambda a: (-(a["date"].toordinal() if a["date"] else 0), a["slug"]))
    return series, standalone, [c for s in series for c in s["pieces"]] + standalone


# ---------------------------------------------------------------- layout

def nav_links(current, cls):
    parts = []
    for n in SITE["nav"]:
        if n.get("when") == "fiction" and not FICTION_ON:
            continue
        if n.get("url"):
            parts.append(f'<a href="{esc(n["url"].replace("{fiction_url}", FICTION_URL).replace("{law_url}", LAW_URL))}">{esc(n["label"])}</a>')
            continue
        aria = ' aria-current="page"' if n["path"] == current else ""
        parts.append(f'<a href="{href(n["path"])}"{aria}>{esc(n["label"])}</a>')
    return f'<nav class="{cls}" aria-label="Main">' + "".join(parts) + "</nav>"


def layout(title, desc, body, path, current=None, kind="website", noindex=False, jsonld=None, published=None,
           theme=None):
    name = SITE["name"]
    theme = theme or ("fiction" if MODE == "fiction" else None)
    full_title = name if not title else f"{title} | {name}"
    head = [
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f"<title>{esc(full_title)}</title>",
        f'<meta name="description" content="{esc(desc)}">',
        f'<meta property="og:title" content="{esc(full_title)}">',
        f'<meta property="og:description" content="{esc(desc)}">',
        f'<meta property="og:type" content="{kind}">',
        f'<meta property="og:site_name" content="{esc(name)}">',
        '<meta name="twitter:card" content="summary">',
        f'<link rel="icon" href="{href("/favicon.svg")}" type="image/svg+xml">',
        f'<link rel="icon" href="{href("/favicon.ico")}" sizes="48x48">',
        f'<link rel="apple-touch-icon" href="{href("/apple-touch-icon.png")}">',
        f'<link rel="stylesheet" href="{href("/style.css")}">',
    ]
    if noindex:
        head.append('<meta name="robots" content="noindex">')
    if URL:
        head.append(f'<link rel="canonical" href="{abs_url(path)}">')
        head.append(f'<meta property="og:url" content="{abs_url(path)}">')
        head.append(f'<link rel="alternate" type="application/atom+xml" title="{esc(name)}" href="{abs_url("/feed.xml")}">')
    if published:
        head.append(f'<meta property="article:published_time" content="{published.isoformat()}">')
    if jsonld and URL:
        blob = json.dumps(jsonld, ensure_ascii=False).replace("</", "<\\/")
        head.append(f'<script type="application/ld+json">{blob}</script>')
    header = (
        '<header class="wrap masthead">'
        f'<a class="brand" href="{esc(HOME_URL) if (HOME_URL and MODE != "hub") else href("/")}"><img class="brand-mark" src="{href("/logo.svg")}" alt="" width="34" height="34"><span>{esc(name)}</span></a>'
        + nav_links(current, "nav")
        + "</header>"
    )
    footer = (
        '<footer class="site-footer"><div class="wrap footer-inner"><div>'
        f'<div class="footer-name">{esc(name)}</div>'
        f'<p>{esc(SITE.get("tagline", ""))} {esc(SITE.get("location", ""))}.</p>'
        f'<p class="footer-fine">{esc(SITE.get("disclaimer", ""))}</p></div>'
        + nav_links(current, "footer-nav")
        + "</div></footer>"
    )
    return (
        f'<!doctype html>\n<html lang="{esc(SITE.get("lang", "en"))}">\n<head>\n'
        + "\n".join(head)
        + '\n</head>\n<body' + (f' class="{theme}"' if theme else "") + '>\n<a class="skip" href="#main">Skip to content</a>\n'
        + header + "\n" + body + "\n" + footer + "\n</body>\n</html>\n"
    )


def person_ld():
    p = {"@type": "Person", "name": SITE["name"], "url": SITE.get("author_url") or (LAW_URL + "/about/" if MODE == "hub" else abs_url("/about/")),
         "jobTitle": "Advocate",
         "knowsAbout": ["Privacy law", "Data protection", "Consent management", "GDPR", "UK GDPR",
                        "CCPA and CPRA", "India's Digital Personal Data Protection Act 2023",
                        "Data processing agreements", "Cross-border data transfers", "EU AI Act"],
         "address": {"@type": "PostalAddress", "addressLocality": "Kozhikode", "addressRegion": "Kerala", "addressCountry": "IN"}}
    if SITE.get("linkedin"):
        p["sameAs"] = [SITE["linkedin"]]
    return p


def entry_html(a):
    parts = []
    if a["date"]:
        parts.append(esc(fmt_date(a["date"])))
    if a["topic"]:
        parts.append(f'<span class="topic">{esc(a["topic"])}</span>')
    meta = "<br>".join(parts)
    return (
        f'<a class="entry" href="{href(LP + "/" + a["slug"] + "/")}">'
        f'<div class="entry-meta">{meta}</div>'
        f'<div><h3>{esc(a["title"])}</h3><p>{esc(a["blurb"])}</p></div></a>'
    )


# ---------------------------------------------------------------- pages

def _go(url):
    return url if re.match(r"https?://", url) else href(url)


def card_items(rows):
    li = "".join(
        f'<li><a href="{_go(url)}"><span class="ci-title">{esc(title)}</span>'
        f'<span class="ci-meta">{esc(meta)}</span></a></li>' for url, title, meta in rows)
    return f'<div class="card-list"><p class="label">Latest</p><ul>{li}</ul></div>'


def home_card(cls, label, path, text, rows):
    return (f'<div class="card {cls}"><h2><a class="card-link" href="{_go(path)}">{esc(label)}'
            '<span class="arrow" aria-hidden="true">&rarr;</span></a></h2>'
            f'<p class="card-text">{esc(text)}</p>{card_items(rows)}</div>')


def page_home(articles, pieces=()):
    m, _ = parse(CONTENT / "home.md")
    limit = int(SITE.get("home_articles", 5))
    both = FICTION_ON
    kicker = m.get("kicker_both", "") if both and m.get("kicker_both") else m.get("kicker", "")
    title = m.get("title_both") if both and m.get("title_both") else m["title"]
    intro = m.get("intro_both") if both and m.get("intro_both") else m.get("intro", "")
    hero = (
        '<main id="main"><section class="wrap hero">'
        f'<p class="eyebrow">{esc(kicker)}</p>'
        f'<h1 class="display xl">{esc(title)}</h1>'
        f'<p class="intro">{esc(intro)}</p></section>'
    )
    lm, _ = parse(CONTENT / "law.md")
    count = int(SITE.get("home_card_items", 3))
    law_rows = [(f"{LAW_URL}/{a['slug']}/", a["title"],
                 " · ".join(x for x in (fmt_date(a["date"]) if a["date"] else "", a["topic"]) if x))
                for a in articles[:count]]
    cards = home_card("card-law", "Law", LAW_URL + "/", lm.get("card") or lm.get("intro", ""), law_rows)
    if both:
        fm, _ = parse(CONTENT / "fiction.md")
        newest = sorted(pieces, key=lambda c: -(c["date"].toordinal() if c["date"] else 0))[:count]

        def where(c):
            if c["series"]:
                return f"{c['series']['title']}, chapter {c['series']['pieces'].index(c) + 1}"
            return FORM_LABEL[c["form"]]
        fic_rows = [(FICTION_URL + c["url"], c["title"],
                     " · ".join(x for x in (fmt_date(c["date"]) if c["date"] else "", where(c)) if x))
                    for c in newest]
        cards += home_card("card-fiction", "Fiction", FICTION_URL + "/", fm.get("card") or fm.get("intro", ""), fic_rows)
    body = hero + '<section class="wrap"><div class="cards">' + cards + "</div></section></main>"
    return layout("", SITE["description"], body, "/", current="/",
                  jsonld={"@context": "https://schema.org", "@type": "WebSite", "name": SITE["name"],
                          "url": abs_url("/"), "description": SITE["description"],
                          "inLanguage": SITE.get("lang", "en"), "author": person_ld()})


def page_law(articles):
    m, _ = parse(CONTENT / "law.md")
    body = (
        '<main id="main"><section class="wrap page-head">'
        f'<p class="eyebrow">{esc(m.get("kicker", "Law"))}</p>'
        f'<h1 class="display">{esc(m["title"])}</h1>'
        f'<p class="intro">{esc(m.get("intro", ""))}</p></section>'
        '<section class="wrap list-section"><div class="entries">'
        + "".join(entry_html(a) for a in articles)
        + f'</div><p class="list-note">{esc(SITE.get("disclaimer", ""))}</p></section></main>'
    )
    return layout("Law", m.get("intro", SITE["description"]), body, LP + "/", current=LP + "/")


def page_article(a, articles):
    i = articles.index(a)
    nxt = ""
    if len(articles) > 1:
        other = articles[(i + 1) % len(articles)]
        nxt = (
            f'<a class="nextcard" href="{href(LP + "/" + other["slug"] + "/")}">'
            f'<span class="label">More in law</span><strong>{esc(other["title"])}</strong></a>'
        )
    eyebrow = "Law"
    if a["topic"]:
        eyebrow += f" · {esc(a['topic'])}"
    if a["date"]:
        eyebrow += f' <span>· <time datetime="{a["date"].isoformat()}">{esc(fmt_date(a["date"]))}</time></span>'
    if a["updated"] and a["updated"] != a["date"]:
        eyebrow += f' <span>· Updated <time datetime="{a["updated"].isoformat()}">{esc(fmt_date(a["updated"]))}</time></span>'
    lede = f'<p class="lede">{esc(a["summary"])}</p>' if a["summary"] else ""
    body = (
        '<main id="main"><article class="article">'
        f'<a class="back" href="{href(LP + "/")}">Back to law</a>'
        f'<p class="eyebrow">{eyebrow}</p>'
        f'<h1>{esc(a["title"])}</h1>{lede}'
        f'<div class="prose">{markdown(a["body"])}</div>'
        '<p class="note">General information, not legal advice. Check the current text of each law '
        "and any regulator guidance for your situation.</p>"
        f"{nxt}</article></main>"
    )
    desc = a["description"] or SITE["description"]
    article_ld = {
        "@type": "Article",
        "headline": a["title"], "description": desc,
        "inLanguage": SITE.get("lang", "en"), "author": person_ld(),
        "mainEntityOfPage": abs_url(f"{LP}/{a['slug']}/"),
    }
    if a["topic"]:
        article_ld["articleSection"] = a["topic"]
    if a["date"]:
        article_ld["datePublished"] = a["date"].isoformat()
        article_ld["dateModified"] = (a["updated"] or a["date"]).isoformat()
    crumbs = {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": abs_url("/")},
            {"@type": "ListItem", "position": 2, "name": "Law", "item": abs_url(LP + "/")},
            {"@type": "ListItem", "position": 3, "name": a["title"], "item": abs_url(f"{LP}/{a['slug']}/")},
        ],
    }
    ld = {"@context": "https://schema.org", "@graph": [article_ld, crumbs]}
    return layout(a["title"], desc, body,
                  f"{LP}/{a['slug']}/", current=LP + "/", kind="article",
                  jsonld=ld, published=a["date"])


def poem_html(src):
    stanzas = re.split(r"\n\s*\n", src.strip())
    out = []
    for st in stanzas:
        lines = [re.sub(r"(\\| {2,})$", "", ln.rstrip()).strip() for ln in st.splitlines()]
        out.append("<p>" + "<br>\n".join(inline(ln) for ln in lines if ln) + "</p>")
    return "\n".join(out)


def fiction_entry(url, meta_parts, title, blurb):
    meta = "<br>".join(meta_parts)
    return (f'<a class="entry" href="{href(url)}"><div class="entry-meta">{meta}</div>'
            f'<div><h3>{esc(title)}</h3><p>{esc(blurb)}</p></div></a>')


def page_fiction(series, standalone):
    m, _ = parse(CONTENT / "fiction.md")
    parts = []
    if series:
        rows = []
        for s in series:
            n = len(s["pieces"])
            meta = [esc(s["status"])] if s["status"] else []
            meta.append(f"{n} {'piece' if n == 1 else 'pieces'}")
            rows.append(fiction_entry(f"/{s['slug']}/", meta, s["title"], s["summary"]))
        parts.append('<section class="wrap list-section"><h2 class="label section-label">Series</h2>'
                     '<div class="entries">' + "".join(rows) + "</div></section>")
    if standalone:
        rows = []
        for a in standalone:
            meta = [esc(fmt_date(a["date"]))] if a["date"] else []
            meta.append(f'<span class="topic">{esc(FORM_LABEL[a["form"]])}</span>')
            rows.append(fiction_entry(a["url"], meta, a["title"], a["summary"]))
        parts.append('<section class="wrap list-section"><h2 class="label section-label">Stories and poems</h2>'
                     '<div class="entries">' + "".join(rows) + "</div></section>")
    if not parts:
        parts.append('<section class="wrap list-section"><p class="intro">The first pieces will appear here soon.</p></section>')
    body = (
        '<main id="main"><section class="wrap page-head">'
        f'<p class="eyebrow">{esc(m.get("kicker", "Fiction"))}</p>'
        f'<h1 class="display">{esc(m["title"])}</h1>'
        f'<p class="intro">{esc(m.get("intro", ""))}</p></section>'
        + "".join(parts)
        + f'<div class="wrap"><p class="list-note">{esc(SITE.get("fiction_notice", ""))}</p></div></main>'
    )
    ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": "Fiction",
          "url": abs_url("/"), "inLanguage": SITE.get("lang", "en"), "author": person_ld()}
    return layout("Fiction", m.get("intro", SITE["description"]), body, "/", current="/",
                  jsonld=ld, theme="fiction")


def _crumbs(*trail):
    items = [{"@type": "ListItem", "position": i + 1, "name": n, "item": abs_url(u)}
             for i, (n, u) in enumerate((("Fiction", "/"),) + trail)]
    return {"@type": "BreadcrumbList", "itemListElement": items}


def page_series(s):
    first = s["pieces"][0]
    status = f" · {esc(s['status'])}" if s["status"] else ""
    rows = []
    for i, c in enumerate(s["pieces"], 1):
        meta = [f"{esc(FORM_LABEL[c['form']])} {i}"]
        if c["date"]:
            meta.append(esc(fmt_date(c["date"])))
        rows.append(fiction_entry(c["url"], meta, c["title"], c["summary"]))
    lede = f'<p class="lede">{esc(s["summary"])}</p>' if s["summary"] else ""
    synopsis = f'<div class="prose">{markdown(s["body"])}</div>' if s["body"] else ""
    body = (
        '<main id="main"><article class="article series-head">'
        f'<a class="back" href="{href("/")}">All fiction</a>'
        f'<p class="eyebrow">Fiction{status}</p><h1>{esc(s["title"])}</h1>{lede}{synopsis}'
        f'<p><a class="readbtn" href="{href(first["url"])}">Start reading: {esc(first["title"])}</a></p></article>'
        '<section class="wrap list-section"><h2 class="label section-label">Contents</h2>'
        '<div class="entries">' + "".join(rows) + "</div></section></main>"
    )
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "CreativeWorkSeries", "name": s["title"], "description": s["description"] or SITE["description"],
         "url": abs_url(f"/{s['slug']}/"), "inLanguage": SITE.get("lang", "en"), "author": person_ld(),
         "genre": "Fiction", "hasPart": [{"@type": "CreativeWork", "name": c["title"], "position": i,
                                          "url": abs_url(c["url"])} for i, c in enumerate(s["pieces"], 1)]},
        _crumbs((s["title"], f"/{s['slug']}/"))]}
    return layout(s["title"], s["description"] or SITE["description"], body, f"/{s['slug']}/",
                  current="/", jsonld=ld, theme="fiction")


def page_piece(a, standalone):
    s = a["series"]
    eyebrow = "Fiction"
    if s:
        i = s["pieces"].index(a)
        eyebrow += f" · {esc(s['title'])} · {esc(FORM_LABEL[a['form']])} {i + 1} of {len(s['pieces'])}"
        back = f'<a class="back" href="{href("/" + s["slug"] + "/")}">Back to {esc(s["title"])}</a>'
        prev = s["pieces"][i - 1] if i > 0 else None
        nxt = s["pieces"][i + 1] if i + 1 < len(s["pieces"]) else None
        cards = ""
        if prev:
            cards += (f'<a class="nextcard" href="{href(prev["url"])}"><span class="label">Previous</span>'
                      f'<strong>{esc(prev["title"])}</strong></a>')
        if nxt:
            cards += (f'<a class="nextcard" href="{href(nxt["url"])}"><span class="label">Next</span>'
                      f'<strong>{esc(nxt["title"])}</strong></a>')
        else:
            cards += (f'<a class="nextcard" href="{href("/" + s["slug"] + "/")}"><span class="label">'
                      f'End of the current text</span><strong>Back to {esc(s["title"])}</strong></a>')
        nav = f'<div class="chapnav">{cards}</div>'
    else:
        eyebrow += f" · {esc(FORM_LABEL[a['form']])}"
        back = f'<a class="back" href="{href("/")}">All fiction</a>'
        nav = ""
        if len(standalone) > 1:
            other = standalone[(standalone.index(a) + 1) % len(standalone)]
            nav = (f'<a class="nextcard" href="{href(other["url"])}"><span class="label">More fiction</span>'
                   f'<strong>{esc(other["title"])}</strong></a>')
    if a["date"]:
        eyebrow += f' <span>· <time datetime="{a["date"].isoformat()}">{esc(fmt_date(a["date"]))}</time></span>'
    lede = f'<p class="lede">{esc(a["summary"])}</p>' if a["summary"] else ""
    inner = poem_html(a["body"]) if a["form"] == "poem" else markdown(a["body"])
    cls = "prose reading poem" if a["form"] == "poem" else "prose reading"
    notice = f'<p class="note">{esc(SITE.get("fiction_notice", ""))}</p>' if SITE.get("fiction_notice") else ""
    body = (
        '<main id="main"><article class="article">' + back + f'<p class="eyebrow">{eyebrow}</p>'
        f'<h1>{esc(a["title"])}</h1>{lede}<div class="{cls}">{inner}</div>{notice}{nav}</article></main>'
    )
    node = {"@type": "CreativeWork", "name": a["title"], "description": a["description"] or SITE["description"],
            "inLanguage": SITE.get("lang", "en"), "author": person_ld(), "genre": FORM_LABEL[a["form"]],
            "mainEntityOfPage": abs_url(a["url"])}
    trail = []
    if s:
        node["position"] = s["pieces"].index(a) + 1
        node["isPartOf"] = {"@type": "CreativeWorkSeries", "name": s["title"], "url": abs_url(f"/{s['slug']}/")}
        trail.append((s["title"], f"/{s['slug']}/"))
    trail.append((a["title"], a["url"]))
    if a["date"]:
        node["datePublished"] = a["date"].isoformat()
        node["dateModified"] = (a["updated"] or a["date"]).isoformat()
    ld = {"@context": "https://schema.org", "@graph": [node, _crumbs(*trail)]}
    return layout(a["title"], a["description"] or SITE["description"], body, a["url"], current="/",
                  kind="article", jsonld=ld, published=a["date"], theme="fiction")


def page_about():
    if MODE == "fiction":
        return page_fiction_about()
    m, text = parse(CONTENT / "about.md")
    facts = [(c["label"], esc(c["value"])) for c in SITE.get("credentials", [])]
    if SITE.get("email"):
        e = esc(SITE["email"])
        facts.append(("Email", f'<a href="mailto:{e}">{e}</a>'))
    if SITE.get("linkedin"):
        u = esc(SITE["linkedin"])
        facts.append(("LinkedIn", f'<a href="{u}" rel="noopener noreferrer">{u}</a>'))
    dl = "".join(f"<div><dt>{esc(k)}</dt><dd>{v}</dd></div>" for k, v in facts)
    body = (
        '<main id="main"><section class="wrap page-head">'
        '<p class="eyebrow">About</p>'
        f'<h1 class="display">{esc(m["title"])}</h1>'
        f'<div class="about"><div class="prose">{markdown(text)}</div>'
        f'<dl class="facts">{dl}</dl></div>'
        '<p class="fine">The legal articles on this site are general information, not legal advice. '
        "Writing to me does not create an advocate-client relationship, so please do not send "
        "confidential information in a first email.</p></section></main>"
    )
    return layout("About", "About " + SITE["name"] + ", advocate in Kozhikode, Kerala.", body, LP + "/about/", current=LP + "/about/",
                  jsonld={"@context": "https://schema.org", "@type": "ProfilePage", "mainEntity": person_ld()})


def page_fiction_about():
    m, text = parse(CONTENT / "fiction-about.md")
    body = (
        '<main id="main"><section class="wrap page-head">'
        '<p class="eyebrow">About the author</p>'
        f'<h1 class="display">{esc(m["title"])}</h1>'
        f'<div class="about"><div class="prose">{markdown(text)}</div></div>'
        f'<p class="fine">{esc(SITE.get("fiction_notice", ""))}</p></section></main>'
    )
    return layout("About", m.get("description") or "About " + SITE["name"] + ", author of the stories on this site.",
                  body, "/about/", current="/about/",
                  jsonld={"@context": "https://schema.org", "@type": "ProfilePage", "mainEntity": person_ld()})


def page_404():
    body = (
        '<main id="main"><section class="wrap page-head">'
        '<p class="eyebrow">404</p><h1 class="display">That page does not exist.</h1>'
        f'<p class="intro"><a href="{href("/")}">Back to the home page</a></p></section></main>'
    )
    return layout("Page not found", "Page not found.", body, "/404.html", noindex=True)


# ---------------------------------------------------------------- output

def font_css():
    rules = []
    for family, filename, style, weight in FONT_FILES:
        if (STATIC / "fonts" / filename).exists():
            rules.append(
                f'@font-face{{font-family:"{family}";src:url("{href("/fonts/" + filename)}") format("woff2");'
                f"font-weight:{weight};font-style:{style};font-display:swap}}"
            )
    return "\n".join(rules)


def write(rel, text):
    target = DIST / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def sitemap(articles, series=(), pieces=()):
    if MODE == "fiction":
        urls = [("/", None), ("/about/", None)]
        urls += [(f"/{s['slug']}/", s["date"]) for s in series]
        urls += [(c["url"], c["updated"] or c["date"]) for c in pieces]
    elif MODE == "law":
        urls = [("/", None), ("/about/", None)]
        urls += [(f"/{a['slug']}/", a["updated"] or a["date"]) for a in articles]
    else:
        urls = [("/", None)]
    rows = []
    for path, d in urls:
        last = f"<lastmod>{d.isoformat()}</lastmod>" if d else ""
        rows.append(f"<url><loc>{xml_escape(abs_url(path))}</loc>{last}</url>")
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(rows) + "\n</urlset>\n")


def feed(articles, pieces=()):
    today = date.today().isoformat() + "T00:00:00Z"
    entries = []
    if MODE == "fiction":
        articles = []
    else:
        pieces = ()
    for c in pieces:
        stamp = (c["date"].isoformat() + "T00:00:00Z") if c["date"] else today
        link = xml_escape(abs_url(c["url"]))
        entries.append(
            f"<entry><title>{xml_escape(c['title'])}</title><link href=\"{link}\"/>"
            f"<id>{link}</id><updated>{stamp}</updated><summary>{xml_escape(c['summary'])}</summary></entry>"
        )
    for a in articles:
        stamp = (a["date"].isoformat() + "T00:00:00Z") if a["date"] else today
        link = xml_escape(abs_url(f"{LP}/{a['slug']}/"))
        entries.append(
            f"<entry><title>{xml_escape(a['title'])}</title><link href=\"{link}\"/>"
            f"<id>{link}</id><updated>{stamp}</updated>"
            f"<summary>{xml_escape(a['summary'] or a['blurb'])}</summary></entry>"
        )
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<feed xmlns="http://www.w3.org/2005/Atom">\n'
            f"<title>{xml_escape(SITE['name'])}</title><link href=\"{xml_escape(abs_url('/'))}\"/>"
            f"<id>{xml_escape(abs_url('/'))}</id><updated>{today}</updated>"
            f"<author><name>{xml_escape(SITE['name'])}</name></author>\n"
            + "\n".join(entries) + "\n</feed>\n")


def main():
    global FICTION_ON
    articles = [] if MODE == "fiction" else load_articles()
    series, standalone, pieces = load_fiction()
    FICTION_ON = bool(pieces) and (MODE == "fiction" or bool(FICTION_URL))
    if MODE != "fiction" and pieces and not FICTION_URL:
        print("Note: fiction pieces exist but fiction_url is not set in site.json, so the Fiction links are hidden.")
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()

    for item in STATIC.iterdir():
        if item.name == "style.css":
            continue
        if item.is_dir():
            shutil.copytree(item, DIST / item.name)
        else:
            shutil.copy2(item, DIST / item.name)

    fonts = font_css()
    css = (STATIC / "style.css").read_text(encoding="utf-8")
    write("style.css", (fonts + "\n" if fonts else "") + css)

    if MODE == "fiction":
        write("index.html", page_fiction(series, standalone))
        write("about/index.html", page_about())
        write("404.html", page_404())
        for s in series:
            write(f"{s['slug']}/index.html", page_series(s))
        for c in pieces:
            write(c["url"].strip("/") + "/index.html", page_piece(c, standalone))
    elif MODE == "law":
        write("index.html", page_law(articles))
        write("about/index.html", page_about())
        write("404.html", page_404())
        for a in articles:
            write(f"{a['slug']}/index.html", page_article(a, articles))
    else:
        write("index.html", page_home(articles, pieces))
        write("404.html", page_404())
        if LAW_URL:   # addresses that used to live on this domain now live on the law site
            write("_redirects", "\n".join([
                f"/law/about {LAW_URL}/about/ 301", f"/law/about/ {LAW_URL}/about/ 301",
                f"/about {LAW_URL}/about/ 301", f"/about/ {LAW_URL}/about/ 301",
                f"/feed.xml {LAW_URL}/feed.xml 301",
                f"/law {LAW_URL}/ 301", f"/law/ {LAW_URL}/ 301",
                f"/law/* {LAW_URL}/:splat 301"]) + "\n")

    robots = "User-agent: *\nAllow: /\n"
    if URL:
        robots += f"Sitemap: {abs_url('/sitemap.xml')}\n"
        write("sitemap.xml", sitemap(articles, series, pieces))
        if MODE != "hub":
            write("feed.xml", feed(articles, pieces))
    write("robots.txt", robots)

    if MODE == "fiction":
        print(f"Built the fiction site: {len(series)} series and {len(pieces)} piece(s) into {DIST}")
    elif MODE == "law":
        print(f"Built the law site: {len(articles)} article(s) into {DIST}")
    else:
        print(f"Built the home page (hub) into {DIST}")
    if not URL:
        print("Note: site_url is empty, so sitemap.xml, feed.xml and canonical links were skipped.")
    if not fonts:
        print("Note: no font files in static/fonts/, so the site uses system serif fonts.")


if __name__ == "__main__":
    main()
