# Northpreneur Hub Ltd — Website

Premium, fully database-driven corporate website for Northpreneur Hub Ltd, built with
Django, SQLite, HTML5, CSS3 and vanilla JavaScript (no frontend framework, no build step).

## Stack

- Django 5.2.4 · Pillow · django-ckeditor-5 (rich text) · whitenoise (static files) · python-decouple (env vars)
- SQLite (designed to migrate cleanly to Postgres later — just swap `DATABASES` in `config/settings.py`)

## Local Setup

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
copy .env.example .env          # then edit SECRET_KEY etc.
python manage.py migrate
python manage.py seed_data      # loads the real company content (see below)
python manage.py createsuperuser
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` for the site and `/admin/` for the CMS.

## `seed_data` management command

`sitecore/management/commands/seed_data.py` populates the database from the supplied
company profile and real photos. It's safe to re-run (idempotent). The source images path
is hardcoded to this machine's `Downloads\nph\NPH IMAGES` folder — only needed the first
time; after that, all content lives in the database and is managed through `/admin/`.

**What it seeds (real content only):** site settings (incl. the real logo — auto-cropped
from a source photo, see below), navigation, footer, social links (Instagram + TikTok — the
only two supplied), hero, homepage section toggles, the 4 services with their real
sub-features and photos, 5 core values, 10 target audience segments, 5 "why choose us"
points, the Founder's real message, the About page, 5 gallery categories, an 18-photo
gallery, and 3 programs built from actual event/training photos.

**Left empty on purpose (no fabrication):** Impact statistics, testimonials, FAQs and blog
posts — none were supplied, so those sections ship hidden/empty until you add real content
in `/admin/`. Privacy Policy and Terms & Conditions are also empty — write the real legal
text in `/admin/ → Pages → Legal Pages` before launch.

## Production deployment notes

- Set `DEBUG=False` and a real `SECRET_KEY`/`ALLOWED_HOSTS` in `.env`.
- **Run `python manage.py collectstatic`** — required, because whitenoise uses
  `CompressedManifestStaticFilesStorage` in this config, which raises a hard error for any
  static file referenced without a matching entry in its build manifest. The site will not
  work with `DEBUG=False` until this has been run at least once (re-run it after every
  static file change).
- Configure a real email backend (`EMAIL_*` env vars) so contact-form notifications and
  `mail_admins` actually deliver — the dev default just prints to the console.
- Point a real webserver (nginx/Apache) or a platform like Render/Railway at
  `config.wsgi.application`; whitenoise serves static files directly from Django in the
  meantime.

## Project layout

```
config/          settings, root urls, wsgi/asgi
sitecore/        site settings, nav/footer, homepage section builder, gallery, icons, seed_data
organization/    founder, team, core values, target audience, why-choose, impact, testimonials, FAQ
services/        Service + ServiceFeature
programs/        Program (drives both /programs/ and /opportunities/ via program_type)
blog/            BlogPost, BlogCategory, BlogTag, Author
contact/         ContactMessage, NewsletterSubscriber, forms
pages/           AboutPage, LegalPage
templates/       base.html, partials/, home/sections/ (one partial per homepage section), gallery/, per-app templates
static/css/      tokens.css (design system: green+gold palette) → base → components → animations → home/pages/gallery
static/js/main.js  nav, reveal-on-scroll, counters, service/value tabs, FAQ accordion, gallery filter + lightbox, forms
```

## Design system

Green + gold, ~70% light / ~30% deliberate dark (Founder section, half of Mission/Vision,
final CTA, footer). Colors in `static/css/tokens.css` as `--color-primary*`, `--color-gold*`,
`--color-dark`, `--color-off-white` etc. — sampled from the **real Northpreneur Hub logo**,
which turned up embedded in one of the supplied photos (`IMG-20251024-WA0009.jpg`, a
logo-sheet graphic). `seed_data` auto-crops it into `SiteSettings.logo` /`logo_dark` on
first run — no more CSS-wordmark fallback needed. Replace it in `/admin/ → Website
Management → Site Settings` if you get a cleaner source file from your designer.

## Gallery

`/gallery/` — a masonry photo gallery with a JS lightbox (keyboard arrows + Esc, click
outside to close) and category filtering. Backed by `sitecore.GalleryImage` +
`sitecore.GalleryCategory` (both fully admin-manageable: upload, caption, categorize,
feature, reorder, publish/unpublish). Featured images also drive the homepage's "Stories in
Motion" preview strip.

## Known gaps to close before launch

1. A second person appears in several source photos (folders named "CO FOUNDER" /
   "MD-COFOUNDER"), but no name or title for them was in the company profile, so no `Team
   Member` record was created. Add them yourself in `/admin/ → Organization → Team Members`
   once you have the correct name/title/bio.
2. Privacy Policy and Terms & Conditions are empty — write the real text before launch.
3. Impact statistics and testimonials are unpopulated (no real numbers/quotes were
   supplied) — their homepage sections stay hidden until you add real ones in `/admin/`.
4. One gallery photo (a charcoal-briquette bag close-up) is sideways in its source file —
   worth a quick rotate/replace in `/admin/` if you notice it.
