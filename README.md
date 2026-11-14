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
content/about.md          About page text (law site)
content/fiction-about.md  About page text (fiction site, at /about/)
content/articles/*.md     one file per article
content/fiction.md        Fiction site headline, intro and home page card line
content/series/*.md       one file per fiction series (a novel or serial)
content/pieces/*.md       one file per chapter, short story or poem
static/style.css          all styling
static/media/             images uploaded from the editor
static/fonts/             optional self-hosted fonts (see below)
static/_headers           security headers (Cloudflare Pages and Netlify)
site-law.json, site-fiction.json  settings for the law and fiction sites
wrangler-law.jsonc, wrangler-fiction.jsonc  Cloudflare settings for the law and fiction sites
build.py                  the build script (builds either site)
dist/, dist-law/, dist-fiction/  the finished sites, rebuilt every time you run build.py
```

## Build and preview

```
python3 build.py
python3 -m http.server 8000 -d dist
```

Then open http://localhost:8000. Python 3.8 or newer is the only requirement.

## Three sites from one repository

| Address | Build command | Output | What it holds |
|---|---|---|---|
| vishnuprasadv.com | `python3 build.py` | `dist/` | Home page with the Law and Fiction cards. Redirects old addresses to the law site. |
| law.vishnuprasadv.com | `python3 build.py --site law` | `dist-law/` | Articles and the Law About page |
| fiction.vishnuprasadv.com | `python3 build.py --site fiction` | `dist-fiction/` | Series, chapters, stories, poems and the Fiction About page |

One repository means one editor (Pages CMS) and one build script. Saving anything in the editor rebuilds all three sites.

- `site.json` holds shared settings and the home page. `site-law.json` and `site-fiction.json` override it for their site (name, description, address, menu). `law_url` and `fiction_url` in `site.json` are where the cards and menus link.
- The Fiction card and menu links appear only once at least one piece is published.
- The home page shows the latest three items of each section (`home_card_items` in `site.json`) as interactive cards. On a computer, hovering or tabbing to a card widens it and dims the other; on a phone they stack. This is plain CSS, so no site runs scripts.
- Addresses on the law site: `/` lists articles, `/<article>/` is an article, `/about/` is the About page. On the fiction site: `/` lists everything, `/<series>/`, `/<series>/<chapter>/`, `/<piece>/`, `/about/`.
- The old addresses vishnuprasadv.com/law/... and /about/ redirect permanently to the law site.

A **series** (`content/series/`) is a novel or serial. A **piece** (`content/pieces/`) is one text: a chapter has a Series and a chapter number, a story or poem has no Series. Set `draft: true` to keep anything off the site. **Poems:** in the editor, press Enter at the end of each line and leave one empty line (press Enter again) between stanzas; the site shows each stanza as a block of tight lines with a gap before the next. Each piece's `date` is the date shown, so older writing keeps its real date.

### Cloudflare setup (one-time)

The existing project (`vishnu-site`) keeps serving vishnuprasadv.com. Two more projects read the same repository. Do the law project first, then merge the pull request, so the redirects never point at a site that is not live.

1. Workers & Pages, Create, import the `vishnu-site` repository. Name it exactly `vishnu-law`. Build command `python3 build.py --site law`, deploy command `npx wrangler deploy --config wrangler-law.jsonc`.
2. When that build succeeds, open the project's Settings, Domains and Routes, and add the custom domain `law.vishnuprasadv.com`.
3. Repeat for fiction: name `vishnu-fiction`, build command `python3 build.py --site fiction`, deploy command `npx wrangler deploy --config wrangler-fiction.jsonc`, domain `fiction.vishnuprasadv.com`.
4. Leave the existing `vishnu-site` project unchanged: build `python3 build.py`, deploy with the existing `wrangler.jsonc`.
5. In each new project's build settings, if Cloudflare asks which paths trigger builds, leave it at the whole repository.

To use other subdomain names, change `site_url` in the two override files and `law_url`, `fiction_url` in `site.json`, and attach those names in step 2 and 3.

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
