# Vishnu Prasad V: personal site

A static website. Each article is a markdown file. A small Python script turns those files into the finished pages, the article lists and the home page, so adding an article is adding one file.

No framework, no tracking, no scripts and no third-party requests, so the site sets no cookies and needs no cookie banner.

## Publishing from the browser (no code)

Articles are written in a visual editor, much like posting to Medium or LinkedIn. One-time setup:

1. Create a free GitHub account and a new repository (private is fine). Upload the contents of this folder to it, with the `main` branch.
2. In the repository, open Settings, then Pages, and set Source to "GitHub Actions". The included workflow in `.github/workflows/deploy.yml` then builds and publishes the site every time something is saved.
3. Go to https://app.pagescms.org, sign in with GitHub and install the Pages CMS GitHub App on this repository.
4. Open the repository there. You will see "Articles" and "About page".

Every day after that: open app.pagescms.org, choose Articles, press Add, write the title, summary and text, add images with the picture button, and save. Leave "Draft" ticked while it is unfinished. The site updates within a minute or two. Images are stored in `static/media`.

The editor writes the same markdown files described below, so you can still edit them by hand.

Note: GitHub Pages ignores `static/_headers`, so the strict security headers only apply on Cloudflare Pages or Netlify. Both can publish the same repository if you want them.

## Layout

```
site.json                 name, tagline, contact details, navigation, credentials
content/home.md           home page headline and intro
content/law.md            Law page headline and intro
content/about.md          About page text
content/articles/*.md     one file per article
content/fiction.md        Fiction page headline and intro
content/series/*.md       one file per fiction series (a novel or serial)
content/pieces/*.md       one file per chapter, short story or poem
static/style.css          all styling
static/media/             images uploaded from the editor
static/fonts/             optional self-hosted fonts (see below)
static/_headers           security headers (Cloudflare Pages and Netlify)
build.py                  the build script
dist/                     the finished site, rebuilt every time you run build.py
```

## Build and preview

```
python3 build.py
python3 -m http.server 8000 -d dist
```

Then open http://localhost:8000. Python 3.8 or newer is the only requirement.

## Fiction

The Fiction section stays hidden (no menu entry, no home page card) until the first piece is published. Then the home page shows two cards, Law and Fiction, and the menu gains a Fiction link.

A **series** (`content/series/`) is a novel or serial: title, summary, status and a synopsis. A **piece** (`content/pieces/`) is one text. A chapter is a piece with a Series and a chapter number. A short story or poem is a piece with no Series. In the editor these are "Fiction series" and "Fiction pieces".

```
---
title: The First Gate
form: chapter          # chapter, story or poem
series: The Test Saga  # leave out for a standalone piece
order: 1               # chapter number, used to sort and to link previous and next
date: 2026-12-01
summary: One or two sentences shown in the lists.
---
Text of the chapter. A line containing only --- is shown as a scene break.
```

Addresses: `/fiction/` lists everything, `/fiction/<series>/` is the series page with its contents, `/fiction/<series>/<chapter>/` is a chapter, and `/fiction/<piece>/` is a standalone piece. Poems keep their line breaks. Set `draft: true` on a piece or a whole series to keep it off the site. The notice under each piece comes from `fiction_notice` in `site.json`. When both sections are live, the home page headline comes from `title_both` and `intro_both` in `content/home.md`.

## Add an article

Create a file in `content/articles/`, for example `content/articles/my-new-article.md`. The file name becomes the address: `/law/my-new-article/`.

```
---
title: The article title
topic: Consent
date: 2026-12-01
summary: One or two sentences shown under the title on the article page.
blurb: One sentence shown in the article lists on the Home and Law pages.
---
## First heading

Body text. Supports ## headings, paragraphs, - bullet lists, 1. numbered lists,
> quotes, ---, [links](https://example.com), **bold** and *italic*.
```

Run `python3 build.py`. The article gets its own page, appears on the Law page and the Home page (newest first by `date`), and is added to the sitemap and feed.

Optional fields: `weight: 1` orders articles that have no date or the same date (lower first). `draft: true` keeps a file out of the build while you write it.

## Before going live

1. In `site.json`, fill `email` and `linkedin`. They appear on the About page only when set.
2. Set `site_url` to your final address, for example `https://yourname.in`. This turns on the sitemap, the feed and canonical links.
3. Put real `date:` values on the two articles.
4. Self-host the fonts (next section).
5. Run `python3 build.py` again.

## Fonts

The design uses Fraunces, Source Serif 4 and Inter. Loading them from Google's servers sends every visitor's IP address to Google, which is a data protection problem for a privacy site (a Munich court awarded damages over exactly this in 2022). So the fonts are self-hosted. Download the variable `.woff2` files, for example from fontsource.org, and save them in `static/fonts/` with these exact names:

```
Fraunces-Variable.woff2
SourceSerif4-Variable.woff2
Inter-Variable.woff2
```

Optional italics: `Fraunces-Italic-Variable.woff2`, `SourceSerif4-Italic-Variable.woff2`.

`build.py` detects the files and wires them in. Without them the site falls back to the visitor's system serif and sans fonts, which works but looks plainer.

## Publish

Upload the contents of `dist/` to any static host, or let the host run the build.

**Cloudflare Pages** (free): push this folder to a GitHub repository, create a Pages project from it, set build command `python3 build.py` and output directory `dist`. `static/_headers` is applied automatically.

**Netlify** (free): same settings. `_headers` is applied automatically.

**GitHub Pages** (free): publish the `dist/` folder. It ignores `_headers`. If the site lives at `username.github.io/repo-name`, set `"base_path": "/repo-name"` in `site.json`.

For your own domain, buy it from any registrar and add it in the host's custom domain settings. The host shows the DNS records to set.

## Notes

- `static/_headers` includes a strict Content-Security-Policy that allows only files from your own domain. If you later add something from elsewhere (an embed, an analytics script), that policy has to be loosened.
- The About page and every article footer carry the "not legal advice" notice. Check the wording against the Bar Council of India rules on advocate advertising before publishing.
