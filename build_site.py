#!/usr/bin/env python3
"""Assembles the static pages for the JMM Art Prize site from one shared shell.
Output is plain static HTML in /Users/user/Desktop/jmm-art-prize/. No runtime build.

The "Previous work" gallery of competition entries is generated from
assets/entries/manifest.json (produced by tools/process_entries.py). Pupil names
never appear anywhere: images are grouped only by year -> school -> stage.
"""

import html
import json
import pathlib

SITE = pathlib.Path("/Users/user/Desktop/jmm-art-prize")

NAV = [
    ("index.html", "Home"),
    ("about.html", "About us"),
    ("jackies-story.html", "Jackie's Story"),
    ("art-prize.html", "The Art Prize"),
    ("exhibitions.html", "Previous exhibitions"),
    ("previous-work.html", "Previous work"),
]

BASE_URL = "https://jmmartprize.co.uk"

SCHOOL_ORDER = [
    "clydebank-high-school",
    "st-peter-the-apostle",
    "dumbarton-academy",
    "vale-of-leven-academy",
    "our-lady-and-st-patricks",
    "gavinburn-primary",
]
STAGE_ORDER = ["Primary", "S1", "S2", "S3", "S4", "S5", "S6", "S5–6", ""]


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
      <a href="about.html">Get involved</a>
      <a href="https://www.instagram.com/jmm_art_prize_glasgow/" target="_blank" rel="noopener">Instagram</a>
      <a href="mailto:callum_jstewart@hotmail.com">Email</a>
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


def page(path, title, description, main_html, lightbox=False):
    body = f'<main id="main">\n{main_html}\n</main>\n'
    if lightbox:
        body += LIGHTBOX
    return head(title, description, path) + header(path) + body + FOOTER + \
        '<script src="main.js"></script>\n</body>\n</html>\n'


# ---------------------------------------------------------------- entries gallery

def render_entries():
    mpath = SITE / "assets" / "entries" / "manifest.json"
    if not mpath.exists():
        return ('<p class="muted">The competition entries gallery will appear here once the '
                'images have been processed.</p>')
    manifest = json.loads(mpath.read_text(encoding="utf-8"))

    jump = " &middot; ".join(
        f'<a href="#entries-{y}">{y} entries</a>' for y in sorted(manifest, reverse=True)
    )
    out = [f'<p class="entry-jump">Jump to: <a href="#jackies-artwork">Jackie&rsquo;s artwork</a> &middot; {jump}</p>']

    for year in sorted(manifest, reverse=True):
        schools = manifest[year]
        total = sum(s["count"] for s in schools.values())
        out.append(f'<section class="entry-year">')
        out.append(f'  <h2 id="entries-{year}">{year} entries</h2>')
        out.append(f'  <p class="muted">{total} works, shown by school. No names &mdash; '
                   f'just the school and year group.</p>')
        for slug in SCHOOL_ORDER:
            if slug not in schools:
                continue
            s = schools[slug]
            label = html.escape(s["label"])
            noun = "work" if s["count"] == 1 else "works"
            out.append('  <div class="school-block">')
            out.append(f'    <h3>{label} <span class="count">{s["count"]} {noun}</span></h3>')
            groups = s["groups"]
            staged = len(groups) > 1 or (len(groups) == 1 and "" not in groups)
            for stage in STAGE_ORDER:
                if stage not in groups:
                    continue
                imgs = groups[stage]
                if staged and stage:
                    out.append(f'    <h4 class="stage">{stage}</h4>')
                out.append('    <div class="entry-grid">')
                alt_base = f"Pupil artwork — {s['label']}, {year}"
                for im in imgs:
                    alt = alt_base + (f", {stage}" if stage else "")
                    out.append(
                        f'      <a class="lb" href="{im["full"]}" aria-label="Enlarge artwork">'
                        f'<img src="{im["thumb"]}" loading="lazy" decoding="async" alt="{alt}"></a>'
                    )
                out.append('    </div>')
            out.append('  </div>')
        out.append('</section>')
    return "\n".join(out)


# ---------------------------------------------------------------- page content

HOME = """
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
      <ul class="partner-list">
        <li>The Glasgow School of Art</li>
        <li>West Dunbartonshire Council</li>
        <li>Partick Thistle Football Club</li>
        <li>Cass Art</li>
        <li>The Alchemy Experiment</li>
      </ul>
      <p><a class="btn btn-primary" href="about.html">Partner with us</a></p>
    </div>
  </section>
"""

ABOUT = """
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
      <ul class="partner-list">
        <li>The Glasgow School of Art</li>
        <li>West Dunbartonshire Council</li>
        <li>Partick Thistle Football Club</li>
        <li>Cass Art</li>
        <li>The Alchemy Experiment</li>
      </ul>
    </div>
  </section>

  <section class="section section-contact" id="get-involved">
    <div class="wrap contact-grid">
      <div class="contact-intro">
        <p class="eyebrow">Get involved</p>
        <h2>Partner, sponsor or support the prize</h2>
        <p>Every prize, every wall and every opening night comes from someone choosing to help. If you&rsquo;d like to be part of the next Jackie Marno-McGoldrick Art Prize as a partner, sponsor or supporter, we&rsquo;d love to hear from you.</p>
        <p class="contact-direct">Prefer email? <a href="mailto:callum_jstewart@hotmail.com?subject=JMM%20Art%20Prize%20%E2%80%94%20getting%20involved">callum_jstewart@hotmail.com</a></p>
        <p class="contact-note"><strong>Are you a pupil or parent wanting to enter?</strong> Entries are handled by school art departments &mdash; please speak to your school&rsquo;s art teacher, or send a message and we&rsquo;ll point you the right way.</p>
      </div>
      <!--
        FORM SETUP: create a free account at https://formspree.io, add a form,
        and replace REPLACE_WITH_FORM_ID below with your form's ID. See README.md.
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
        <p class="form-fallback">Trouble with the form? Email <a href="mailto:callum_jstewart@hotmail.com">callum_jstewart@hotmail.com</a>.</p>
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
        <p><a href="previous-work.html#entries-2025">See the 2025 entries &rarr;</a></p>
      </article>

      <article class="year">
        <h2>2024 &mdash; inaugural year</h2>
        <p class="year-meta">31 October &ndash; 14 November 2024 &middot; The Alchemy Experiment, Glasgow</p>
        <p>The first exhibition showed finalists&rsquo; work from the Clydebank area and was extended by a week after popular demand. The inaugural winner was Frankie Thom, for the work <em>Reflections</em>.</p>
        <blockquote>
          <p>&ldquo;You should take huge pride in what you&rsquo;ve created, which I&rsquo;m sure will be a successful and rewarding event for aspiring young artists for many years to come.&rdquo;</p>
          <cite>Graeme Thom, father of 2024 winner Frankie Thom</cite>
        </blockquote>
        <p><a href="previous-work.html#entries-2024">See the 2024 entries &rarr;</a></p>
      </article>
    </div>
  </section>
"""

WORK = f"""
  <section class="page-head">
    <div class="wrap">
      <p class="eyebrow">Previous work</p>
      <h1>Previous work</h1>
      <p class="lede">Jackie&rsquo;s own drawings and paintings, and the pupils&rsquo; work entered into past competitions &mdash; shown by year and school, without names.</p>
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
      {render_entries()}
    </div>
  </section>
"""

PAGES = [
    ("index.html", "The Jackie Marno-McGoldrick Art Prize | Glasgow",
     "A free annual art prize and exhibition for school pupils across West Dunbartonshire, held in Glasgow, in memory of artist and teacher Jackie Marno-McGoldrick.", HOME, False),
    ("about.html", "About us | The Jackie Marno-McGoldrick Art Prize",
     "Why the Jackie Marno-McGoldrick Art Prize exists, how it works, its partners, and how to get involved as a sponsor or supporter.", ABOUT, False),
    ("jackies-story.html", "Jackie's Story | The Jackie Marno-McGoldrick Art Prize",
     "Jackie Marno-McGoldrick was an artist and art teacher at Clydebank High School for nearly twenty years. Her story, and her work.", STORY, True),
    ("art-prize.html", "The Art Prize | The Jackie Marno-McGoldrick Art Prize",
     "How to enter the Jackie Marno-McGoldrick Art Prize: who can enter, categories, prizes and the timeline for the year.", PRIZE, False),
    ("exhibitions.html", "Previous exhibitions | The Jackie Marno-McGoldrick Art Prize",
     "The 2024 and 2025 Jackie Marno-McGoldrick Art Prize exhibitions at The Alchemy Experiment on Byres Road, Glasgow.", EXHIBITIONS, False),
    ("previous-work.html", "Previous work | The Jackie Marno-McGoldrick Art Prize",
     "Jackie Marno-McGoldrick's drawings and paintings, and pupils' work from the 2024 and 2025 competitions, shown by year and school.", WORK, True),
]

for path, title, desc, body, lb in PAGES:
    (SITE / path).write_text(page(path, title, desc, body, lightbox=lb), encoding="utf-8")
    print("wrote", path)
