# The Jackie Marno-McGoldrick Art Prize — website

A small, fast website for the annual art prize held in Glasgow.
Plain HTML, CSS and a little JavaScript — **no build step required to deploy**.

## Pages

| File | Nav label | What's on it |
| --- | --- | --- |
| `index.html` | Home | Photo of Callum and Jackie, what the prize is, partners |
| `about.html` | About us | Why it exists, how it works, partners, **get-involved form** |
| `jackies-story.html` | Jackie's Story | Biography, quotes, a few of her works |
| `art-prize.html` | The Art Prize | Who can enter, categories, prizes, timeline |
| `exhibitions.html` | Previous exhibitions | 2024 and 2025 write-ups + opening-night photos |
| `previous-work.html` | Previous work | "Jackie's artwork" gallery + "Previous competition entries" (by year → school), with a click-to-enlarge lightbox |
| `404.html` | — | Shown for unknown URLs |

Supporting files: `styles.css`, `main.js` (mobile menu, footer year, gentle
scroll-in), `favicon.svg`, `CNAME`, `robots.txt`, `sitemap.xml`, `.nojekyll`.

## Media coverage

The press cards on **About us** come from the `MEDIA` list near the top of
`build_site.py` — `(outlet, headline, year, url, image-or-None)`. Add a tuple,
put any clipping image in `assets/media/`, re-run `python3 build_site.py`.

## Fonts & colours

Headings use **Lora** (loaded from Google Fonts). Colours are CSS variables at the
top of `styles.css` (`--gold`, `--rust`, `--paper`, etc.) — change them in one place.

## Editing content — two ways

**A. Edit the HTML directly (fine for wording changes).**
Open the page, change the text, save. ⚠️ If you change the **header or footer**,
you must make the same change in *all six* pages, because each page has its own copy.

**B. Use the generator (safer for structural changes).**
`build_site.py` holds the shared header/footer once, plus each page's content, and
writes all six HTML files. To use it:

```bash
python3 build_site.py
```

Edit the `HOME`, `ABOUT`, `STORY`, … strings (or the `NAV` list / `FOOTER`) inside
`build_site.py`, re-run it, and every page is regenerated consistently.
`404.html` is **not** generated — edit it by hand.

## The "Previous work" page

Two galleries, both with a click-to-enlarge lightbox:

- **Jackie's artwork** — hand-listed in `build_site.py` (the `WORK` string). To add
  one of Jackie's pieces: drop the image in `assets/`, copy an `<a class="lb">…</a>`
  block, update `href` (full image), `src` (a smaller version is fine) and `alt`.

- **Previous competition entries** — generated from `assets/entries/manifest.json`
  by `tools/process_entries.py`. **No pupil names appear anywhere** — images are
  renamed to anonymous IDs (`2025-clydebank-high-school-s1-03.jpg`) and grouped only
  by year → school → stage. To rebuild after adding entries to the Google Drive
  submission folders:

  ```bash
  python3 tools/process_entries.py     # reads Drive, writes assets/entries/ + manifest.json
  python3 build_site.py                # regenerates the HTML
  ```

  `process_entries.py` needs the Google Drive "JMM Art Prize" folders synced locally
  (Google Drive for Desktop). Open it and check the `DRIVE` / `SRC_*` paths near the
  top. School codes in 2024 filenames (CHS, SPTA, DA, VOLA, OLSP) and the 2025
  per-school folders are mapped in the `SCHOOLS` / `FOLDER_TO_CODE` dicts.

## The get-involved form — one-time setup

The form on `about.html` posts to [Formspree](https://formspree.io) (free tier is fine).

1. Create a free account, verify your email.
2. Create a form; Formspree gives you an endpoint like `https://formspree.io/f/abcdwxyz`.
3. In `about.html` (and `build_site.py` if you use it), replace `REPLACE_WITH_FORM_ID`
   with your form ID (`abcdwxyz`).

4. In the Formspree dashboard, set the form's **notification email** to the address
   you want enquiries sent to. That address lives only in Formspree — it never
   appears on the website.

Until Formspree is set up the form shows but won't send. The page has no email
address on it by design; the fallback pointer is the Instagram link.

## Run it locally

```bash
cd jmm-art-prize
python3 -m http.server 8000
```

Open <http://localhost:8000>.

## Deploy

See [DEPLOY.md](DEPLOY.md) — GitHub Pages + connecting `jmmartprize.co.uk`.
