#!/usr/bin/env python3
"""Assembles the static pages for the JMM Art Prize site from one shared shell.
Output is plain static HTML in /Users/user/Desktop/jmm-art-prize/. No runtime build.

The "Previous work" area is generated from assets/entries/manifest.json
(produced by tools/process_entries.py):

    previous-work.html                          landing + Jackie's artwork + year cards
    entries-<year>.html                         one page per year, cards per school
    entries-<year>-<school-slug>.html           one page per school/year, the grid

Pupil names never appear anywhere: images are grouped only by year -> school -> stage.
"""

import html
import json
import pathlib

SITE = pathlib.Path(__file__).resolve().parent

NAV = [
    ("index.html", "Home"),
    ("about.html", "About us"),
    ("jackies-story.html", "Jackie's Story"),
    ("art-prize.html", "The Art Prize"),
    ("exhibitions.html", "Previous exhibitions"),
    ("previous-work.html", "Previous work"),
]

BASE_URL = "https://jmmartprize.co.uk"

# Submissions come in with names to strip; here they are only ever grouped.
PARTNERS = [
    ("The Glasgow School of Art", "https://www.gsa.ac.uk/"),
    ("West Dunbartonshire Council", "https://www.west-dunbarton.gov.uk/"),
    ("Partick Thistle Football Club", "https://ptfc.co.uk/"),
    ("Cass Art", "https://www.cassart.co.uk/"),
    ("The Alchemy Experiment", "https://www.alchemyexperiment.com/"),
]

# Media coverage — (outlet, headline, year, url, image or None)
MEDIA = [
    ("Glasgow Times", "Jackie Marno-McGoldrick Prize held in Glasgow for second year",
     "2025", "https://www.glasgowtimes.co.uk/news/scottish-news/25581673.jackie-marno-mcgoldrick-prize-held-glasgow-second-year/",
     "assets/media/press-glasgowtimes-print.jpg"),
    ("Clydebank Post", "Son of late Clydebank art teacher reveals plans to carry on her legacy",
     "2024", "https://www.clydebankpost.co.uk/news/24001386.son-late-clydebank-art-teacher-reveals-plans-carry-legacy/",
     "assets/media/press-clydebankpost-2024.jpg"),
    ("Glasgow West End", "The Jackie Marno-McGoldrick Art Prize and Exhibition",
     "2025", "https://www.glasgowwestend.co.uk/the-jackie-marno-mcgoldrick-art-prize-and-exhibition-2025/",
     "assets/media/press-glasgowwestend.jpg"),
    ("The National", "Jackie Marno: a tribute to an extraordinary woman",
     "2023", "https://www.thenational.scot/sevendays/23427692.jackie-marno-tribute-extraordinary-woman/", None),
    ("Clydebank Post", "Clydebank High School pays tribute to a much-loved art teacher",
     "2023", "https://www.clydebankpost.co.uk/news/23417651.clydebank-high-school-tributes-much-loved-art-teacher/", None),
    ("Artmag", "Clydebank’s young talent at The Alchemy Experiment, Glasgow",
     "2024", "https://artmag.co.uk/clydebanks-young-talent-at-the-alchemy-experiment-glasgow/", None),
    ("Instagram", "The 2025 exhibition",
     "2025", "https://www.instagram.com/p/DQUj1zOjPfp/", None),
    ("Instagram", "Opening night",
     "2025", "https://www.instagram.com/p/DQuLc5CDHwZ/", None),
    ("LinkedIn", "Callum Stewart on founding the prize",
     "2024", "https://www.linkedin.com/posts/callum-stewart-msc_what-an-absolute-thrill-it-is-to-help-make-activity-7391808358762315776-8V3_", None),
]


def media_section():
    cards = []
    for outlet, headline, year, url, img in MEDIA:
        img_html = ""
        cls = "press-card"
        if img:
            cls += " has-img"
            img_html = (f'\n        <span class="press-card-img">'
                        f'<img src="{img}" loading="lazy" decoding="async" alt="{html.escape(outlet)} coverage of the prize"></span>')
        cards.append(
            f'      <a class="{cls}" href="{url}" target="_blank" rel="noopener">{img_html}\n'
            f'        <span class="press-card-body">\n'
            f'          <span class="press-outlet">{html.escape(outlet)}</span>\n'
            f'          <strong>{html.escape(headline)}</strong>\n'
            f'          <span class="muted">{year}</span>\n'
            f'        </span>\n'
            f'      </a>'
        )
    return (
        '  <section class="section section-alt" id="media-coverage">\n'
        '    <div class="wrap">\n'
        '      <p class="eyebrow">Media coverage</p>\n'
        '      <h2>The prize in the press</h2>\n'
        '      <p class="section-lede">Selected coverage of the prize and of Jackie, in print and online.</p>\n'
        '      <div class="press-grid">\n'
        + "\n".join(cards) +
        '\n      </div>\n'
        '    </div>\n'
        '  </section>\n'
    )


SCHOOL_ORDER = [
    "clydebank-high-school",
    "st-peter-the-apostle",
    "dumbarton-academy",
    "vale-of-leven-academy",
    "our-lady-and-st-patricks",
    "gavinburn-primary",
]
STAGE_ORDER = ["Primary", "S1", "S2", "S3", "S4", "S5", "S6", "S5–6", ""]

# The get-involved form delivers wherever Formspree is configured to send it.
# The address is set in the Formspree dashboard, never on the page.


def partner_list():
    lis = "\n".join(
        f'        <li><a href="{url}" target="_blank" rel="noopener">{html.escape(name)}</a></li>'
        for name, url in PARTNERS
    )
    return f'      <ul class="partner-list">\n{lis}\n      </ul>'


def head(title, description, path):
    canonical = BASE_URL + "/" + ("" if path == "index.html" else path)
    return f"""<!DOCTYPE html>
<html lang="en-GB">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{BASE_URL}/assets/og-image.jpg">
<meta property="og:locale" content="en_GB">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Lora:wght@500;600;700&display=swap">
<link rel="stylesheet" href="styles.css">
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
"""


def header(current):
    links = "\n".join(
        '      <a href="{href}"{cur}>{label}</a>'.format(
            href=href,
            label=label,
            cur=' aria-current="page"' if href == current else "",
        )
        for href, label in NAV
    )
    return f"""<header class="site-header">
  <div class="wrap header-inner">
    <a class="brand" href="index.html">The Jackie Marno-McGoldrick<span class="brand-line2">Art Prize</span></a>
    <a class="nav-cta" href="about.html#get-involved">Partner with us</a>
    <button class="nav-toggle" aria-expanded="false" aria-controls="primary-nav" aria-label="Open menu">
      <span></span><span></span><span></span>
    </button>
    <nav id="primary-nav" class="primary-nav" aria-label="Primary">
{links}
    </nav>
  </div>
</header>
"""


FOOTER = """<footer class="site-footer">
  <div class="wrap footer-inner">
    <p class="footer-dedication">In memory of Jackie Marno-McGoldrick<br>artist and teacher, Clydebank High School</p>
    <nav class="footer-links" aria-label="Footer">
      <a href="art-prize.html">The Art Prize</a>
      <a href="about.html#get-involved">Contact</a>
      <a href="https://www.instagram.com/jmm_art_prize_glasgow/" target="_blank" rel="noopener">Instagram</a>
    </nav>
    <p class="footer-fine">&copy; <span id="year">2026</span> The Jackie Marno-McGoldrick Art Prize &middot; Glasgow, Scotland.<br>Artwork reproduced by kind permission of the artists and their families.</p>
  </div>
</footer>
"""

LIGHTBOX = """<div id="lightbox" class="lightbox" aria-hidden="true">
  <button class="lb-close" aria-label="Close">&times;</button>
  <button class="lb-prev" aria-label="Previous">&#8249;</button>
  <img class="lb-img" alt="">
  <button class="lb-next" aria-label="Next">&#8250;</button>
</div>
"""


def page(path, title, description, main_html, current=None, lightbox=False):
    body = f'<main id="main">\n{main_html}\n</main>\n'
    if lightbox:
        body += LIGHTBOX
    return head(title, description, path) + header(current or path) + body + FOOTER + \
        '<script src="main.js"></script>\n</body>\n</html>\n'


# ---------------------------------------------------------------- entries pages

def load_manifest():
    mpath = SITE / "assets" / "entries" / "manifest.json"
    if not mpath.exists():
        return {}
    return json.loads(mpath.read_text(encoding="utf-8"))


def school_page_name(year, slug):
    return f"entries-{year}-{slug}.html"


def crumbs(*parts):
    """parts: (label, href|None) tuples; last is current (no link)."""
    out = []
    for label, href in parts:
        if href:
            out.append(f'<a href="{href}">{html.escape(label)}</a>')
        else:
            out.append(f'<span aria-current="page">{html.escape(label)}</span>')
    return '<p class="crumbs">' + ' <span aria-hidden="true">&rsaquo;</span> '.join(out) + '</p>'


def render_year_cards(manifest):
    cards = []
    for year in sorted(manifest, reverse=True):
        schools = manifest[year]
        total = sum(s["count"] for s in schools.values())
        # a representative thumbnail: first image of the first school in order
        thumb = ""
        for slug in SCHOOL_ORDER:
            if slug in schools:
                for stage in STAGE_ORDER:
                    if stage in schools[slug]["groups"]:
                        thumb = schools[slug]["groups"][stage][0]["thumb"]
                        break
            if thumb:
                break
        cards.append(
            f'    <a class="year-card" href="entries-{year}.html">\n'
            f'      <span class="year-card-img"><img src="{thumb}" loading="lazy" decoding="async" alt=""></span>\n'
            f'      <span class="year-card-body"><strong>{year}</strong>'
            f'<span class="muted">{total} works &middot; {len(schools)} schools</span></span>\n'
            f'    </a>'
        )
    return '  <div class="year-cards">\n' + "\n".join(cards) + '\n  </div>'


def render_school_cards(year, schools):
    cards = []
    for slug in SCHOOL_ORDER:
        if slug not in schools:
            continue
        s = schools[slug]
        thumb = ""
        for stage in STAGE_ORDER:
            if stage in s["groups"]:
                thumb = s["groups"][stage][0]["thumb"]
                break
        noun = "work" if s["count"] == 1 else "works"
        cards.append(
            f'    <a class="year-card" href="{school_page_name(year, slug)}">\n'
            f'      <span class="year-card-img"><img src="{thumb}" loading="lazy" decoding="async" alt=""></span>\n'
            f'      <span class="year-card-body"><strong>{html.escape(s["label"])}</strong>'
            f'<span class="muted">{s["count"]} {noun}</span></span>\n'
            f'    </a>'
        )
    return '  <div class="year-cards">\n' + "\n".join(cards) + '\n  </div>'


def render_school_grid(year, slug, s):
    label = html.escape(s["label"])
    groups = s["groups"]
    staged = len(groups) > 1 or (len(groups) == 1 and "" not in groups)
    blocks = []
    for stage in STAGE_ORDER:
        if stage not in groups:
            continue
        imgs = groups[stage]
        if staged and stage:
            blocks.append(f'      <h2 class="stage">{stage}</h2>')
        blocks.append('      <div class="entry-grid">')
        alt_base = f"Pupil artwork — {s['label']}, {year}"
        for im in imgs:
            alt = alt_base + (f", {stage}" if stage else "")
            blocks.append(
                f'        <a class="lb" href="{im["full"]}" aria-label="Enlarge artwork">'
                f'<img src="{im["thumb"]}" loading="lazy" decoding="async" alt="{alt}"></a>'
            )
        blocks.append('      </div>')
    noun = "work" if s["count"] == 1 else "works"
    return f"""
  <section class="page-head">
    <div class="wrap">
      {crumbs(("Previous work", "previous-work.html"), (str(year), f"entries-{year}.html"), (s["label"], None))}
      <p class="eyebrow">{year} competition entries</p>
      <h1>{label}</h1>
      <p class="lede">{s["count"]} {noun}, shown by year group. No names. Click any image to enlarge.</p>
    </div>
  </section>

  <section class="section">
    <div class="wrap">
{chr(10).join(blocks)}
      <p class="back-link"><a href="entries-{year}.html">&larr; All {year} schools</a></p>
    </div>
  </section>
"""


def build_entries_pages(manifest):
    """Yields (path, title, description, main_html, lightbox) for every generated page."""
    pages = []
    for year in sorted(manifest, reverse=True):
        schools = manifest[year]
        total = sum(s["count"] for s in schools.values())
        year_main = f"""
  <section class="page-head">
    <div class="wrap">
      {crumbs(("Previous work", "previous-work.html"), (str(year), None))}
      <p class="eyebrow">Previous work</p>
      <h1>{year} competition entries</h1>
      <p class="lede">{total} works from {len(schools)} schools. No names &mdash; choose a school to see the work, grouped by year group.</p>
    </div>
  </section>

  <section class="section">
    <div class="wrap">
{render_school_cards(year, schools)}
      <p class="back-link"><a href="previous-work.html">&larr; Previous work</a></p>
    </div>
  </section>
"""
        pages.append((
            f"entries-{year}.html",
            f"{year} competition entries | The Jackie Marno-McGoldrick Art Prize",
            f"Pupils' work entered into the {year} Jackie Marno-McGoldrick Art Prize, shown by school and year group, without names.",
            year_main, False,
        ))
        for slug in SCHOOL_ORDER:
            if slug not in schools:
                continue
            s = schools[slug]
            pages.append((
                school_page_name(year, slug),
                f"{s['label']} — {year} entries | The Jackie Marno-McGoldrick Art Prize",
                f"{s['label']} pupils' work from the {year} Jackie Marno-McGoldrick Art Prize, shown by year group, without names.",
                render_school_grid(year, slug, s), True,
            ))
    return pages


# ---------------------------------------------------------------- page content

HOME = f"""
  <section class="hero">
    <div class="wrap hero-grid">
      <div class="hero-copy">
        <p class="eyebrow">Glasgow &middot; Annual since 2024</p>
        <h1>An art prize for young people, in memory of a teacher who believed in them</h1>
        <p class="lede">The Jackie Marno-McGoldrick Art Prize is a free annual competition and exhibition for school pupils across West Dunbartonshire, held in Glasgow&rsquo;s West End. It continues the work of Jackie Marno-McGoldrick, artist and art teacher at Clydebank High School.</p>
        <div class="btn-row">
          <a class="btn btn-primary" href="art-prize.html">About the prize</a>
          <a class="btn btn-ghost" href="jackies-story.html">Jackie&rsquo;s story</a>
        </div>
      </div>
      <figure class="hero-figure">
        <img src="assets/home-callum-jackie.jpg" width="943" height="1164" alt="Callum Stewart and his mother, Jackie Marno-McGoldrick, laughing together in a kitchen." fetchpriority="high">
        <figcaption>Jackie with her son Callum, who founded the prize in her memory</figcaption>
      </figure>
    </div>
  </section>

  <section class="section">
    <div class="wrap">
      <p class="eyebrow">In brief</p>
      <h2>What the prize is</h2>
      <div class="card-grid">
        <div class="card">
          <h3>Open to every pupil</h3>
          <p>Free to enter, open to school pupils up to S6 across West Dunbartonshire, in any medium &mdash; painting, drawing, photography, ceramics, design and more.</p>
          <p><a href="art-prize.html">How it works &rarr;</a></p>
        </div>
        <div class="card">
          <h3>A real exhibition</h3>
          <p>Finalists&rsquo; work is hung in a public exhibition in Glasgow&rsquo;s West End, with prizes in every age category and an opening night for families and teachers.</p>
          <p><a href="exhibitions.html">Previous exhibitions &rarr;</a></p>
        </div>
        <div class="card">
          <h3>Jackie&rsquo;s legacy</h3>
          <p>Founded in 2024 by Jackie&rsquo;s son, Callum Stewart, to carry on her belief that every child deserves a creative voice.</p>
          <p><a href="jackies-story.html">Jackie&rsquo;s story &rarr;</a></p>
        </div>
      </div>
    </div>
  </section>

  <section class="section section-alt">
    <div class="wrap">
      <p class="eyebrow">Partners &amp; supporters</p>
      <h2>In association with</h2>
{partner_list()}
      <p><a class="btn btn-primary" href="about.html">Partner with us</a></p>
    </div>
  </section>
"""

ABOUT = f"""
  <section class="page-head">
    <div class="wrap">
      <p class="eyebrow">About us</p>
      <h1>About the prize</h1>
      <p class="lede">A small, volunteer-run initiative with one aim: to put young people&rsquo;s art on a real wall, in front of a real audience, and to tell them it matters.</p>
    </div>
  </section>

  <section class="section">
    <div class="wrap prose">
      <h2>Why it exists</h2>
      <p>The Jackie Marno-McGoldrick Art Prize was founded in 2024 by Callum Stewart in memory of his mother, Jackie &mdash; an artist and art teacher at Clydebank High School for nearly two decades. Jackie spent her career making sure that every pupil, whatever their circumstances, had the same chance to be taken seriously as an artist. The prize is an attempt to keep doing that.</p>
      <blockquote>
        <p>&ldquo;Mum was really good at giving kids a voice and making sure that everyone had the same opportunities, so I wanted to make sure that keeps going.&rdquo;</p>
        <cite>Callum Stewart, founder</cite>
      </blockquote>

      <h2>How it works</h2>
      <p>Each year pupils across West Dunbartonshire enter work through their school art departments. A panel of judges &mdash; art teachers and people who knew Jackie and her work &mdash; selects finalists and category winners. Finalists&rsquo; work is then shown in a public exhibition in Glasgow&rsquo;s West End, with an invitation-only opening night for pupils, families and teachers. Full details are on <a href="art-prize.html">The Art Prize</a> page.</p>

      <h2>Partners &amp; supporters</h2>
      <p>The prize runs on donated prizes, space, materials and time. Supporters have included:</p>
{partner_list()}
    </div>
  </section>

{media_section()}
  <section class="section section-contact" id="get-involved">
    <div class="wrap contact-grid">
      <div class="contact-intro">
        <p class="eyebrow">Get involved</p>
        <h2>Partner, sponsor or support the prize</h2>
        <p>Every prize, every wall and every opening night comes from someone choosing to help. If you&rsquo;d like to be part of the next Jackie Marno-McGoldrick Art Prize as a partner, sponsor or supporter, send a message below and we&rsquo;ll be in touch.</p>
        <p class="contact-note"><strong>Are you a pupil or parent wanting to enter?</strong> Entries are handled by school art departments &mdash; please speak to your school&rsquo;s art teacher, or send a message and we&rsquo;ll point you the right way.</p>
      </div>
      <!--
        FORM SETUP: create a free account at https://formspree.io, add a form, set
        its notification email in the Formspree dashboard, then replace
        REPLACE_WITH_FORM_ID below with the form's ID. See README.md. The delivery
        address lives only in Formspree, never on this page.
      -->
      <form class="contact-form" action="https://formspree.io/f/REPLACE_WITH_FORM_ID" method="POST">
        <p class="field">
          <label for="name">Your name</label>
          <input type="text" id="name" name="name" autocomplete="name" required>
        </p>
        <p class="field">
          <label for="email">Email</label>
          <input type="email" id="email" name="email" autocomplete="email" required>
        </p>
        <p class="field">
          <label for="org">Organisation <span class="opt">(optional)</span></label>
          <input type="text" id="org" name="organisation" autocomplete="organization">
        </p>
        <p class="field">
          <label for="message">Message</label>
          <textarea id="message" name="message" rows="5" required></textarea>
        </p>
        <input type="hidden" name="_subject" value="JMM Art Prize &mdash; website enquiry">
        <p class="field-hp" aria-hidden="true">
          <label>Leave this field empty<input type="text" name="_gotcha" tabindex="-1" autocomplete="off"></label>
        </p>
        <button type="submit" class="btn btn-primary">Send message</button>
        <p class="form-fallback">You can also reach us on <a href="https://www.instagram.com/jmm_art_prize_glasgow/" target="_blank" rel="noopener">Instagram</a>.</p>
      </form>
    </div>
  </section>
"""

STORY = """
  <section class="page-head">
    <div class="wrap">
      <p class="eyebrow">Jackie's Story</p>
      <h1>Jackie Marno-McGoldrick</h1>
      <p class="lede">Artist. Art teacher at Clydebank High School for nearly twenty years. The reason this prize exists.</p>
    </div>
  </section>

  <section class="section">
    <div class="wrap story-grid">
      <div class="prose">
        <p>Jackie studied art and graphic design at Cardonald College and went on to win first place in an International Fine Art Award for Women Artists in the 1990s. She later trained as a teacher at Jordanhill College and joined the art department at Clydebank High School, where she taught for close to two decades. In 2019 her pupils voted her their best teacher.</p>
        <p>She was known for making learning feel like an adventure, and for refusing to let a pupil&rsquo;s background decide how far they could go. Colleagues described someone who &ldquo;would light up every room she entered&rdquo;. One parent credited her belief in their son &mdash; who went on to a master&rsquo;s degree in art &mdash; entirely to her.</p>
        <p>Jackie kept her own practice going throughout: expressive, figurative drawing and painting, often of the human form, worked in charcoal and heavy, worked-back colour.</p>
        <p>She passed away in March 2023 after an illness. The following year her son, Callum Stewart, founded the Jackie Marno-McGoldrick Art Prize so that the thing she cared about most &mdash; young people being taken seriously as artists &mdash; would carry on.</p>
        <blockquote>
          <p>&ldquo;She was the best of us. An inspiration.&rdquo;</p>
          <cite>A former colleague, Clydebank High School</cite>
        </blockquote>
      </div>
      <figure class="story-figure">
        <img src="assets/jackie-artwork-1.jpg" width="1400" height="1894" loading="lazy" decoding="async" alt="A charcoal and wash drawing by Jackie Marno-McGoldrick of a child's face with lemons and figures around it, signed 'Marno 21'.">
        <figcaption>Untitled, Jackie Marno-McGoldrick, 2021</figcaption>
      </figure>
    </div>
  </section>

  <section class="section section-alt">
    <div class="wrap">
      <h2>Her work</h2>
      <p class="section-lede">A few of Jackie&rsquo;s drawings and paintings. More on the <a href="previous-work.html#jackies-artwork">Previous work</a> page.</p>
      <div class="entry-grid">
        <a class="lb" href="assets/jackie-artwork-1.jpg" aria-label="Enlarge artwork"><img src="assets/jackie-artwork-1-thumb.jpg" loading="lazy" decoding="async" alt="Charcoal and wash drawing of a child's face, by Jackie Marno-McGoldrick, 2021."></a>
        <a class="lb" href="assets/jackie-painting.jpg" aria-label="Enlarge artwork"><img src="assets/jackie-painting.jpg" loading="lazy" decoding="async" alt="Figurative painting in blue, ochre and rust by Jackie Marno-McGoldrick."></a>
        <a class="lb" href="assets/jackie-charcoal.jpg" aria-label="Enlarge artwork"><img src="assets/jackie-charcoal.jpg" loading="lazy" decoding="async" alt="Charcoal drawing of intertwined figures by Jackie Marno-McGoldrick."></a>
      </div>
    </div>
  </section>
"""

PRIZE = """
  <section class="page-head">
    <div class="wrap">
      <p class="eyebrow">The Art Prize</p>
      <h1>How the prize works</h1>
      <p class="lede">Free to enter, open to school pupils across West Dunbartonshire, in any medium. Finalists are shown in a public exhibition in Glasgow.</p>
    </div>
  </section>

  <section class="section">
    <div class="wrap">
      <div class="card-grid">
        <div class="card">
          <h3>Who can enter</h3>
          <p>Pupils up to S6 (under 18) at participating West Dunbartonshire schools &mdash; including Clydebank High School, St Peter the Apostle High School, Dumbarton Academy and Vale of Leven Academy.</p>
        </div>
        <div class="card">
          <h3>Categories</h3>
          <ul class="tick">
            <li>Primary 6 &ndash; S2</li>
            <li>S3 &ndash; S4</li>
            <li>S5 &ndash; S6</li>
            <li>Photography</li>
          </ul>
        </div>
        <div class="card">
          <h3>How to enter</h3>
          <p>Entries go through each school&rsquo;s art department. Pupils and parents should speak to their art teacher, or <a href="about.html#get-involved">contact us</a> for details of the next round.</p>
        </div>
      </div>

      <div class="prose">
        <h2>Prizes</h2>
        <p>Every category has first, second and third place prizes of art-shop vouchers. Partners donate additional prizes each year. Recent examples:</p>
        <ul class="tick">
          <li>A place on a week-long summer course at The Glasgow School of Art</li>
          <li>Cass Art vouchers and art materials</li>
          <li>Signed match balls and match tickets from Partick Thistle Football Club</li>
          <li>Art books from The Glasgow School of Art</li>
        </ul>

        <h2>The year at a glance</h2>
        <ol class="timeline">
          <li><strong>Spring &ndash; summer</strong><span>Competition opens; pupils make and submit work through school art departments.</span></li>
          <li><strong>Early autumn</strong><span>Judging panel selects finalists and category winners.</span></li>
          <li><strong>Late October</strong><span>Opening night for finalists, families and teachers; winners announced.</span></li>
          <li><strong>Late October &ndash; November</strong><span>Public exhibition in Glasgow&rsquo;s West End, roughly two weeks.</span></li>
        </ol>
        <p class="muted">Exact dates change year to year &mdash; <a href="about.html#get-involved">get in touch</a> or follow <a href="https://www.instagram.com/jmm_art_prize_glasgow/" target="_blank" rel="noopener">@jmm_art_prize_glasgow</a> for the current round.</p>
      </div>
    </div>
  </section>
"""

EXHIBITIONS = """
  <section class="page-head">
    <div class="wrap">
      <p class="eyebrow">Previous exhibitions</p>
      <h1>Two years in Glasgow&rsquo;s West End</h1>
      <p class="lede">Both exhibitions have been held at The Alchemy Experiment, 157 Byres Road, Glasgow &mdash; a gallery, events space and artist shop.</p>
    </div>
  </section>

  <section class="section">
    <div class="wrap">
      <article class="year">
        <h2>2025 &mdash; second year</h2>
        <p class="year-meta">31 October &ndash; 13 November 2025 &middot; The Alchemy Experiment, Glasgow</p>
        <p>Entries were up 96% on the first year. With the support of partners and sponsors, eleven prizes were awarded across the four categories &mdash; roughly one in every eleven entries. The exhibition ran for two weeks and drew pupils, families, teachers and West End visitors through the doors. Work came from Clydebank High School, St Peter the Apostle High School, Dumbarton Academy and Vale of Leven Academy.</p>
        <div class="photo-row">
          <figure><img src="assets/alchemy-exterior.jpg" width="1600" height="1067" loading="lazy" decoding="async" alt="Crowds inside The Alchemy Experiment on Byres Road at the 2025 opening, seen through the window beneath the neon sign."></figure>
          <figure><img src="assets/callum-speech.jpg" width="1600" height="1067" loading="lazy" decoding="async" alt="Callum Stewart speaking to guests at the 2025 opening night."><figcaption>Callum Stewart at the 2025 opening night</figcaption></figure>
          <figure><img src="assets/alchemy-crowd.jpg" width="1600" height="1067" loading="lazy" decoding="async" alt="Guests gathered among the hung pupil artworks at the 2025 opening night."></figure>
        </div>
        <p><a href="entries-2025.html">See the 2025 entries &rarr;</a></p>
      </article>

      <article class="year">
        <h2>2024 &mdash; inaugural year</h2>
        <p class="year-meta">31 October &ndash; 14 November 2024 &middot; The Alchemy Experiment, Glasgow</p>
        <p>The first exhibition showed finalists&rsquo; work from the Clydebank area and was extended by a week after popular demand. The inaugural winner was Frankie Thom, for the work <em>Reflections</em>.</p>
        <div class="photo-row">
          <figure><img src="assets/media/exh2024-wall.jpg" width="1600" height="1067" loading="lazy" decoding="async" alt="Pupils' paintings and drawings hung on the brick wall at the 2024 exhibition."></figure>
          <figure><img src="assets/media/exh2024-room.jpg" width="1600" height="1067" loading="lazy" decoding="async" alt="Guests filling the room at the 2024 opening night, artworks lining both walls."><figcaption>The 2024 opening night</figcaption></figure>
          <figure><img src="assets/media/exh2024-crowd.jpg" width="1600" height="1067" loading="lazy" decoding="async" alt="A visitor photographing a pupil's cityscape drawing at the 2024 exhibition."></figure>
        </div>
        <blockquote>
          <p>&ldquo;You should take huge pride in what you&rsquo;ve created, which I&rsquo;m sure will be a successful and rewarding event for aspiring young artists for many years to come.&rdquo;</p>
          <cite>Father of 2024 winner</cite>
        </blockquote>
        <p><a href="entries-2024.html">See the 2024 entries &rarr;</a></p>
      </article>
    </div>
  </section>
"""


def build_previous_work(manifest):
    if manifest:
        entries_block = f"""
      <p class="section-lede">Pupils&rsquo; work entered into past competitions, shown by year and school &mdash; without names. Choose a year:</p>
{render_year_cards(manifest)}
"""
    else:
        entries_block = ('\n      <p class="muted">The competition entries gallery will appear '
                         'here once the images have been processed.</p>\n')
    return f"""
  <section class="page-head">
    <div class="wrap">
      <p class="eyebrow">Previous work</p>
      <h1>Previous work</h1>
      <p class="lede">Jackie&rsquo;s own drawings and paintings, and the pupils&rsquo; work entered into past competitions.</p>
    </div>
  </section>

  <section class="section" id="jackies-artwork">
    <div class="wrap">
      <h2>Jackie&rsquo;s artwork</h2>
      <p class="section-lede">A selection of Jackie&rsquo;s drawings and paintings. Click any image to enlarge.</p>
      <div class="entry-grid">
        <a class="lb" href="assets/jackie-artwork-1.jpg" aria-label="Enlarge artwork"><img src="assets/jackie-artwork-1-thumb.jpg" loading="lazy" decoding="async" alt="Charcoal and wash drawing of a child's face surrounded by lemons and figures, by Jackie Marno-McGoldrick, 2021."></a>
        <a class="lb" href="assets/jackie-painting.jpg" aria-label="Enlarge artwork"><img src="assets/jackie-painting.jpg" loading="lazy" decoding="async" alt="Figurative painting in blue, ochre and rust by Jackie Marno-McGoldrick."></a>
        <a class="lb" href="assets/jackie-charcoal.jpg" aria-label="Enlarge artwork"><img src="assets/jackie-charcoal.jpg" loading="lazy" decoding="async" alt="Charcoal drawing of intertwined figures by Jackie Marno-McGoldrick."></a>
      </div>
      <!-- ADD MORE of Jackie's work: drop images in assets/ and copy an <a class="lb"> block above. -->
    </div>
  </section>

  <section class="section section-alt">
    <div class="wrap">
      <h2>Previous competition entries</h2>
{entries_block}
    </div>
  </section>
"""


# ---------------------------------------------------------------- write it all

def build_sitemap(extra_paths):
    urls = ["", "about.html", "jackies-story.html", "art-prize.html",
            "exhibitions.html", "previous-work.html"] + list(extra_paths)
    items = "\n".join(
        f"  <url><loc>{BASE_URL}/{u}</loc></url>" for u in urls
    )
    (SITE / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + items + "\n</urlset>\n",
        encoding="utf-8",
    )


def main():
    manifest = load_manifest()

    static_pages = [
        ("index.html", "The Jackie Marno-McGoldrick Art Prize | Glasgow",
         "A free annual art prize and exhibition for school pupils across West Dunbartonshire, held in Glasgow, in memory of artist and teacher Jackie Marno-McGoldrick.",
         HOME, None, False),
        ("about.html", "About us | The Jackie Marno-McGoldrick Art Prize",
         "Why the Jackie Marno-McGoldrick Art Prize exists, how it works, its partners, and how to get involved as a sponsor or supporter.",
         ABOUT, None, False),
        ("jackies-story.html", "Jackie's Story | The Jackie Marno-McGoldrick Art Prize",
         "Jackie Marno-McGoldrick was an artist and art teacher at Clydebank High School for nearly twenty years. Her story, and her work.",
         STORY, None, True),
        ("art-prize.html", "The Art Prize | The Jackie Marno-McGoldrick Art Prize",
         "How to enter the Jackie Marno-McGoldrick Art Prize: who can enter, categories, prizes and the timeline for the year.",
         PRIZE, None, False),
        ("exhibitions.html", "Previous exhibitions | The Jackie Marno-McGoldrick Art Prize",
         "The 2024 and 2025 Jackie Marno-McGoldrick Art Prize exhibitions at The Alchemy Experiment on Byres Road, Glasgow.",
         EXHIBITIONS, None, False),
        ("previous-work.html", "Previous work | The Jackie Marno-McGoldrick Art Prize",
         "Jackie Marno-McGoldrick's drawings and paintings, and pupils' work from past competitions, shown by year and school.",
         build_previous_work(manifest), None, True),
    ]

    entries_pages = [
        (p, t, d, m, "previous-work.html", lb)
        for (p, t, d, m, lb) in build_entries_pages(manifest)
    ]

    for path, title, desc, body, current, lb in static_pages + entries_pages:
        (SITE / path).write_text(
            page(path, title, desc, body, current=current, lightbox=lb), encoding="utf-8"
        )
        print("wrote", path)

    build_sitemap(p for (p, *_rest) in entries_pages)
    print("wrote sitemap.xml")


if __name__ == "__main__":
    main()
