# Deploying to GitHub Pages with jmmartprize.co.uk

One-time setup. After this, every `git push` publishes automatically in ~1 minute.

## 1. Put the code on GitHub

From this folder:

```bash
git init
git add .
git commit -m "Initial site"
git branch -M main
```

Create a new **empty** repository on GitHub (no README, no .gitignore) — a good
name is `jmm-art-prize`. Then:

```bash
git remote add origin https://github.com/<your-username>/jmm-art-prize.git
git push -u origin main
```

## 2. Turn on GitHub Pages

1. Repo → **Settings** → **Pages**.
2. **Source**: "Deploy from a branch".
3. **Branch**: `main`, folder `/ (root)`. Save.
4. Wait a minute, then the page appears at `https://<your-username>.github.io/jmm-art-prize/`.
   Check it looks right before doing the domain.

## 3. Buy the domain

Register `jmmartprize.co.uk` at any registrar. For a `.co.uk`, good options are
[Namecheap](https://www.namecheap.com), [Gandi](https://www.gandi.net) or
[Cloudflare](https://www.cloudflare.com/products/registrar/) (Cloudflare needs the
domain's DNS moved to them first, so Namecheap/Gandi is simpler for one domain).
Cost is roughly £6–12/year.

## 4. Point the domain at GitHub

GitHub Pages needs a set of DNS records. In your registrar's DNS settings, add:

**Apex domain (`jmmartprize.co.uk`) — four A records:**

| Type | Name | Value |
| --- | --- | --- |
| A | `@` | `185.199.108.153` |
| A | `@` | `185.199.109.153` |
| A | `@` | `185.199.110.153` |
| A | `@` | `185.199.111.153` |

(Optionally also add the four AAAA records from GitHub's docs for IPv6.)

**`www` subdomain — one CNAME record:**

| Type | Name | Value |
| --- | --- | --- |
| CNAME | `www` | `<your-username>.github.io.` |

Delete any pre-existing "parking" A record or CNAME on `@` / `www` the registrar added.

## 5. Tell GitHub about the domain

1. Repo → **Settings** → **Pages** → **Custom domain**: enter `jmmartprize.co.uk`, Save.
   (The `CNAME` file in this repo already does this, but setting it in the UI
   triggers the certificate.)
2. DNS can take anywhere from 10 minutes to a few hours to propagate. GitHub shows
   a green tick when it verifies.
3. Once verified, tick **Enforce HTTPS**.

Done. `https://jmmartprize.co.uk` and `https://www.jmmartprize.co.uk` both serve the site.

## Updating the site later

```bash
# edit files...
git add .
git commit -m "Update 2026 dates"
git push
```

Live within a minute or two.

## Reference

- GitHub's own guide: <https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site>
