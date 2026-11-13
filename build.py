#!/usr/bin/env python3
"""Builds the site from content/ and static/ into dist/.

Usage:  python3 build.py
Needs only Python 3.8+ and the standard library.
"""
import html
import json
import re
import shutil
from datetime import date, datetime
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
STATIC = ROOT / "static"
DIST = ROOT / "dist"

SITE = json.loads((ROOT / "site.json").read_text(encoding="utf-8"))
BASE = SITE.get("base_path", "").rstrip("/")   # e.g. "/repo-name" for a GitHub project site
URL = SITE.get("site_url", "").rstrip("/")     # e.g. "https://example.com"
SITE.setdefault("description", "")
SITE.setdefault("nav", [{"label": "Law", "path": "/law/"}, {"label": "About", "path": "/about/"}])

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
        slug = re.sub(r"[^a-z0-9]+", "-", path.stem.lower()).strip("-")
        if any(i["slug"] == slug for i in items):
            raise SystemExit(f"{path.name}: another article already has the address /law/{slug}/")
        try:
            weight = int(meta.get("weight", 100))
        except ValueError:
            weight = 100
        items.append({
            "slug": slug,
            "title": meta["title"],
            "topic": meta.get("topic", ""),
            "summary": summary,
            "blurb": meta.get("blurb", summary),
            "date": d,
            "weight": weight,
            "body": body,
        })
    items.sort(key=lambda a: (-(a["date"].toordinal() if a["date"] else 0), a["weight"], a["slug"]))
    return items


# ---------------------------------------------------------------- layout

def nav_links(current, cls):
    parts = []
    for n in SITE["nav"]:
        aria = ' aria-current="page"' if n["path"] == current else ""
        parts.append(f'<a href="{href(n["path"])}"{aria}>{esc(n["label"])}</a>')
    return f'<nav class="{cls}" aria-label="Main">' + "".join(parts) + "</nav>"


def layout(title, desc, body, path, current=None, kind="website", noindex=False, jsonld=None, published=None):
    name = SITE["name"]
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
        f'<a class="brand" href="{href("/")}">{esc(name)}</a>'
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
        + '\n</head>\n<body>\n<a class="skip" href="#main">Skip to content</a>\n'
        + header + "\n" + body + "\n" + footer + "\n</body>\n</html>\n"
    )


def person_ld():
    p = {"@type": "Person", "name": SITE["name"], "url": abs_url("/about/"),
         "jobTitle": "Advocate", "knowsAbout": ["Privacy law", "Data protection", "Consent"]}
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
        f'<a class="entry" href="{href("/law/" + a["slug"] + "/")}">'
        f'<div class="entry-meta">{meta}</div>'
        f'<div><h3>{esc(a["title"])}</h3><p>{esc(a["blurb"])}</p></div></a>'
    )


# ---------------------------------------------------------------- pages

def page_home(articles):
    m, _ = parse(CONTENT / "home.md")
    limit = int(SITE.get("home_articles", 5))
    body = (
        '<main id="main"><section class="wrap hero">'
        f'<p class="eyebrow">{esc(m.get("kicker", ""))}</p>'
        f'<h1 class="display xl">{esc(m["title"])}</h1>'
        f'<p class="intro">{esc(m.get("intro", ""))}</p></section>'
        '<section class="wrap"><div class="section-head"><h2 class="label">Articles</h2>'
        f'<a class="more" href="{href("/law/")}">All articles</a></div>'
        '<div class="entries">' + "".join(entry_html(a) for a in articles[:limit]) + "</div></section></main>"
    )
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
    return layout("Law", m.get("intro", SITE["description"]), body, "/law/", current="/law/")


def page_article(a, articles):
    i = articles.index(a)
    nxt = ""
    if len(articles) > 1:
        other = articles[(i + 1) % len(articles)]
        nxt = (
            f'<a class="nextcard" href="{href("/law/" + other["slug"] + "/")}">'
            f'<span class="label">More in law</span><strong>{esc(other["title"])}</strong></a>'
        )
    eyebrow = "Law"
    if a["topic"]:
        eyebrow += f" · {esc(a['topic'])}"
    if a["date"]:
        eyebrow += f' <span>· <time datetime="{a["date"].isoformat()}">{esc(fmt_date(a["date"]))}</time></span>'
    lede = f'<p class="lede">{esc(a["summary"])}</p>' if a["summary"] else ""
    body = (
        '<main id="main"><article class="article">'
        f'<a class="back" href="{href("/law/")}">Back to law</a>'
        f'<p class="eyebrow">{eyebrow}</p>'
        f'<h1>{esc(a["title"])}</h1>{lede}'
        f'<div class="prose">{markdown(a["body"])}</div>'
        '<p class="note">General information, not legal advice. Check the current text of each law '
        "and any regulator guidance for your situation.</p>"
        f"{nxt}</article></main>"
    )
    ld = {
        "@context": "https://schema.org", "@type": "Article",
        "headline": a["title"], "description": a["summary"] or SITE["description"],
        "inLanguage": SITE.get("lang", "en"), "author": person_ld(),
        "mainEntityOfPage": abs_url(f"/law/{a['slug']}/"),
    }
    if a["topic"]:
        ld["articleSection"] = a["topic"]
    if a["date"]:
        ld["datePublished"] = ld["dateModified"] = a["date"].isoformat()
    return layout(a["title"], a["summary"] or SITE["description"], body,
                  f"/law/{a['slug']}/", current="/law/", kind="article",
                  jsonld=ld, published=a["date"])


def page_about():
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
    return layout("About", "About " + SITE["name"] + ", advocate in Kozhikode, Kerala.", body, "/about/", current="/about/",
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


def sitemap(articles):
    urls = [("/", None), ("/law/", None), ("/about/", None)]
    urls += [(f"/law/{a['slug']}/", a["date"]) for a in articles]
    rows = []
    for path, d in urls:
        last = f"<lastmod>{d.isoformat()}</lastmod>" if d else ""
        rows.append(f"<url><loc>{xml_escape(abs_url(path))}</loc>{last}</url>")
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(rows) + "\n</urlset>\n")


def feed(articles):
    today = date.today().isoformat() + "T00:00:00Z"
    entries = []
    for a in articles:
        stamp = (a["date"].isoformat() + "T00:00:00Z") if a["date"] else today
        link = xml_escape(abs_url(f"/law/{a['slug']}/"))
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
    articles = load_articles()
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

    write("index.html", page_home(articles))
    write("law/index.html", page_law(articles))
    write("about/index.html", page_about())
    write("404.html", page_404())
    for a in articles:
        write(f"law/{a['slug']}/index.html", page_article(a, articles))

    robots = "User-agent: *\nAllow: /\n"
    if URL:
        robots += f"Sitemap: {abs_url('/sitemap.xml')}\n"
        write("sitemap.xml", sitemap(articles))
        write("feed.xml", feed(articles))
    write("robots.txt", robots)

    print(f"Built {len(articles)} article(s) into {DIST}")
    if not URL:
        print("Note: site_url is empty, so sitemap.xml, feed.xml and canonical links were skipped.")
    if not fonts:
        print("Note: no font files in static/fonts/, so the site uses system serif fonts.")


if __name__ == "__main__":
    main()
