"""
Populates the database with Northpreneur Hub Ltd's real content, taken directly
from the supplied company profile (Northpreneur_Hub_Company_Profile.docx) and
real photos (NPH IMAGES/). No fabricated statistics, testimonials, team members
or blog posts are created — see the code comments below for what is seed
content that the client should review, versus verbatim profile content.

Usage: python manage.py seed_data
Safe to re-run — uses update_or_create / get_or_create throughout.
"""
from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction

from organization.models import (
    FounderProfile, CoreValue, TargetAudience, WhyChooseFeature,
)
from pages.models import AboutPage, LegalPage
from programs.models import Program
from services.models import Service, ServiceFeature
from sitecore.models import (
    SiteSettings, NavigationItem, FooterLink, SocialLink,
    HeroSlide, HomepageSection, CTASection, GalleryCategory, GalleryImage,
)

# Local path to the source images supplied alongside the company profile.
# Only needed the first time this command runs on the developer's machine —
# once images are in the database/media folder, admins manage them normally.
SOURCE_IMAGES = Path(r'C:\Users\ismai\Downloads\nph\NPH IMAGES\NPH IMAGES')


def _img(*relative_parts):
    """Return a Django File wrapper for a source image, or None if missing."""
    path = SOURCE_IMAGES.joinpath(*relative_parts)
    if not path.exists():
        return None
    return File(open(path, 'rb'), name=path.name)


def _crop_logo():
    """
    The real Northpreneur Hub logo turned up inside a supplied photo
    (a logo-sheet graphic, not a standalone file) — it contains three lockups:
    a light (white bg) wordmark, a circular icon-only badge, and a dark (green
    banner) wordmark. Auto-crop all three so the admin has a real, editable
    logo/favicon from day one instead of the CSS wordmark fallback.
    Returns (light_file, dark_file, favicon_file) — any may be None if missing.
    """
    from io import BytesIO
    from PIL import Image, ImageChops, ImageOps

    path = SOURCE_IMAGES / 'IMG-20251024-WA0009.jpg'
    if not path.exists():
        return None, None, None

    im = Image.open(path).convert('RGB')
    w, h = im.size

    def _to_file(cropped, name):
        buf = BytesIO()
        cropped.save(buf, format='PNG')
        buf.seek(0)
        return File(buf, name=name)

    def _bbox(region, threshold):
        return ImageChops.invert(ImageOps.grayscale(region).point(lambda p: 0 if p < threshold else 255)).getbbox()

    light_file = None
    top = im.crop((0, 0, w, int(h * 0.36)))
    bbox = _bbox(top, 235)
    if bbox:
        pad = 18
        l, t, r, b = bbox
        l, t = max(0, l - pad), max(0, t - pad)
        r, b = min(top.width, r + pad), min(top.height, b + pad)
        light_file = _to_file(top.crop((l, t, r, b)), 'northpreneur-hub-logo.png')

    favicon_file = None
    mid = im.crop((0, int(h * 0.36), w, int(h * 0.63)))
    bbox_mid = _bbox(mid, 235)
    if bbox_mid:
        pad = 10
        l, t, r, b = bbox_mid
        l, t = max(0, l - pad), max(0, t - pad)
        r, b = min(mid.width, r + pad), min(mid.height, b + pad)
        favicon_file = _to_file(mid.crop((l, t, r, b)), 'northpreneur-hub-favicon.png')

    dark_file = None
    bottom = im.crop((0, int(h * 0.63), w, h))
    bbox2 = _bbox(bottom, 245)
    if bbox2:
        dark_file = _to_file(bottom.crop(bbox2), 'northpreneur-hub-logo-dark.png')

    return light_file, dark_file, favicon_file


class Command(BaseCommand):
    help = "Seed the database with Northpreneur Hub Ltd's real content."

    @transaction.atomic
    def handle(self, *args, **options):
        self.seed_site_settings()
        self.seed_navigation()
        self.seed_footer()
        self.seed_social_links()
        self.seed_hero()
        self.seed_homepage_sections()
        self.seed_cta()
        self.seed_services()
        self.seed_core_values()
        self.seed_target_audience()
        self.seed_why_choose()
        self.seed_founder()
        self.seed_about_page()
        self.seed_legal_pages()
        self.seed_gallery_categories()
        self.seed_gallery()
        self.seed_programs()
        self.stdout.write(self.style.SUCCESS('Seed data loaded successfully.'))

    # -- Site identity -----------------------------------------------------
    def seed_site_settings(self):
        settings_obj = SiteSettings.load()
        settings_obj.site_name = 'Northpreneur Hub Ltd'
        settings_obj.tagline = 'Empowering Northern Nigerians through Digital Opportunities'
        settings_obj.phone_primary = '+234 806 773 0860'
        settings_obj.phone_secondary = '+234 806 133 2959'
        settings_obj.email = 'hello@northpreneurhub.com.ng'
        settings_obj.address = 'KM 4 Old Kano Road, Zaria, Kaduna State, Nigeria'
        settings_obj.mission_statement = (
            'To equip and inspire the next generation of Northern Nigerian entrepreneurs '
            'with the skills, knowledge and confidence to build sustainable digital enterprises.'
        )
        settings_obj.vision_statement = (
            'To become the leading digital empowerment hub in Northern Nigeria, creating a '
            'generation of self-reliant entrepreneurs and globally competitive digital professionals.'
        )
        settings_obj.footer_about = (
            'A forward-thinking digital empowerment and business development company committed '
            'to transforming lives across Northern Nigeria through innovation, entrepreneurship, '
            'and digital opportunities.'
        )
        settings_obj.copyright_text = ''  # template falls back to "© {year} {site_name}"
        settings_obj.default_seo_title = 'Northpreneur Hub Ltd — Empowering Northern Nigerians through Digital Opportunities'
        settings_obj.default_meta_description = (
            'Northpreneur Hub Ltd equips Northern Nigerian youths, women, students and '
            'entrepreneurs with digital skills, business knowledge and income-generating opportunities.'
        )

        if not settings_obj.logo or not settings_obj.logo_dark or not settings_obj.favicon:
            light_logo, dark_logo, favicon = _crop_logo()
            if light_logo and not settings_obj.logo:
                settings_obj.logo.save(light_logo.name, light_logo, save=False)
            if dark_logo and not settings_obj.logo_dark:
                settings_obj.logo_dark.save(dark_logo.name, dark_logo, save=False)
            if favicon and not settings_obj.favicon:
                settings_obj.favicon.save(favicon.name, favicon, save=False)

        settings_obj.save()
        self.stdout.write('Site settings ✓ (real logo cropped from source photo)')

    def seed_navigation(self):
        items = [
            ('Home', '/', False),
            ('About', '/about/', False),
            ('Services', '/services/', False),
            ('Programs', '/programs/', False),
            ('Opportunities', '/opportunities/', False),
            ('Gallery', '/gallery/', False),
            ('Insights', '/insights/', False),
            ('Contact', '/contact/', True),
        ]
        for order, (label, url, is_cta) in enumerate(items):
            NavigationItem.objects.update_or_create(
                label=label, defaults={'url': url, 'is_cta': is_cta, 'display_order': order, 'active': True},
            )
        self.stdout.write('Navigation ✓')

    def seed_footer(self):
        links = [
            ('company', 'About Us', '/about/', 0),
            ('company', 'Our Founder', '/about/#founder', 1),
            ('company', 'Contact', '/contact/', 2),
            ('services', 'Digital Skills Training', '/services/', 0),
            ('services', 'Entrepreneurship Development', '/services/', 1),
            ('services', 'Corporate Training', '/services/', 2),
            ('services', 'Consulting Services', '/services/', 3),
            ('programs', 'All Programs', '/programs/', 0),
            ('programs', 'Opportunities', '/opportunities/', 1),
            ('programs', 'Gallery', '/gallery/', 2),
            ('programs', 'Insights', '/insights/', 3),
            ('legal', 'Privacy Policy', '/privacy-policy/', 0),
            ('legal', 'Terms & Conditions', '/terms-conditions/', 1),
        ]
        for group, label, url, order in links:
            FooterLink.objects.update_or_create(
                group=group, label=label, defaults={'url': url, 'display_order': order, 'active': True},
            )
        self.stdout.write('Footer links ✓')

    def seed_social_links(self):
        # Only what the profile actually supplied — no Facebook/LinkedIn/X invented.
        socials = [
            ('instagram', 'https://instagram.com/Northpreneurhub_ltd', 0),
            ('tiktok', 'https://tiktok.com/@Northpreneurhub_ltd', 1),
        ]
        for platform, url, order in socials:
            SocialLink.objects.update_or_create(
                platform=platform, defaults={'url': url, 'display_order': order, 'active': True},
            )
        self.stdout.write('Social links ✓')

    # -- Hero ----------------------------------------------------------------
    def seed_hero(self):
        image = _img('TRAINING SESSION (2).jpg')
        hero, _ = HeroSlide.objects.get_or_create(headline='Empowering Northern Nigeria’s Next Generation of Digital Entrepreneurs')
        hero.badge_text = 'Digital Empowerment · Northern Nigeria'
        hero.subheadline = (
            'We equip youths, women, students and aspiring entrepreneurs with practical digital '
            'skills, business knowledge and income-generating opportunities that create sustainable income.'
        )
        hero.primary_cta_text = 'Explore Our Programs'
        hero.primary_cta_url = '/programs/'
        hero.secondary_cta_text = 'Talk To Us'
        hero.secondary_cta_url = '/contact/'
        hero.stat1_value, hero.stat1_label = '04', 'Core Service Areas'
        hero.stat2_value, hero.stat2_label = 'Kaduna', 'State & Beyond'
        hero.stat3_value, hero.stat3_label = 'Digital', '& Enterprise Skills'
        hero.collage_label_title = 'Skills to Income'
        hero.collage_label_subtitle = 'Practical, result-oriented training'
        hero.active = True
        if image and not hero.background_image:
            hero.background_image.save(image.name, image, save=False)
        hero.save()
        self.stdout.write('Hero ✓')

    # -- Homepage section builder ---------------------------------------------
    def seed_homepage_sections(self):
        # background_style is informational for the admin list view — each section
        # partial owns its actual look (per the "not a generic card grid" brief) —
        # but we still store the visual truth here for reference/reordering.
        dark_sections = {'founder'}  # mission_vision is a light/dark split panel; cta/footer are dark by design
        for order, (section_type, _label) in enumerate(HomepageSection.SECTION_TYPES):
            enabled = section_type != 'impact'  # no verified statistics supplied yet
            HomepageSection.objects.update_or_create(
                section_type=section_type,
                defaults={
                    'display_order': order,
                    'enabled': enabled,
                    'background_style': 'dark' if section_type in dark_sections else 'light',
                },
            )
        self.stdout.write('Homepage sections ✓')

    def seed_cta(self):
        CTASection.objects.update_or_create(
            title='Ready to Build Your Digital Future?',
            defaults={
                'subtitle': 'Join a training cohort, apply for an open opportunity, or partner with '
                             'Northpreneur Hub to empower your community.',
                'primary_button_text': 'Apply Now',
                'primary_button_url': '/programs/',
                'secondary_button_text': 'Partner With Us',
                'secondary_button_url': '/contact/',
                'active': True,
            },
        )
        self.stdout.write('CTA section ✓')

    # -- Services (verbatim from the profile) ----------------------------------
    def seed_services(self):
        services = [
            {
                'name': 'Digital Skills Training',
                'slug': 'digital-skills-training',
                'icon': 'training',
                'photo': ('TRAINING SESSION.jpg',),
                'short_description': 'Practical, hands-on training in the digital skills driving today’s economy.',
                'detailed_description': (
                    '<p>Our Digital Skills Training equips youths, women, students and aspiring '
                    'entrepreneurs with practical, in-demand digital competencies — designed to be '
                    'applied immediately for income generation and career growth.</p>'
                ),
                'features': [
                    'Social Media Advertisement', 'Affiliate Marketing', 'Graphic Design',
                    'Content Creation', 'Digital Marketing', 'Personal Branding',
                    'Business Development', 'Social Media Management',
                ],
            },
            {
                'name': 'Entrepreneurship Development',
                'slug': 'entrepreneurship-development',
                'icon': 'business',
                'photo': ('MAGIC CHARCOAL', 'PACKAGED PROCESSED CHARCOAL.jpg'),
                'short_description': 'Guidance and tools to launch, register and grow a sustainable business.',
                'detailed_description': (
                    '<p>We walk aspiring and early-stage entrepreneurs through the practical steps of '
                    'building a real business — from registration and planning to positioning it for growth.</p>'
                ),
                'features': [
                    'Business Registration Guidance', 'Business Planning', 'Proposal Writing',
                    'Startup Advisory', 'Branding & Positioning', 'Growth Strategy Development',
                ],
            },
            {
                'name': 'Corporate Training & Capacity Building',
                'slug': 'corporate-training-capacity-building',
                'icon': 'corporate',
                'photo': ('MINISTRY OF YOUTHS.jpg',),
                'short_description': 'Structured capacity-building programs for institutions and organizations.',
                'detailed_description': (
                    '<p>We design and deliver capacity-building programs for government institutions, '
                    'NGOs, private organizations and educational institutions — with a strong focus on '
                    'youth development outcomes.</p>'
                ),
                'features': [
                    'Government Institutions', 'NGOs', 'Private Organizations',
                    'Educational Institutions', 'Youth Development Programs',
                ],
            },
            {
                'name': 'Consulting Services',
                'slug': 'consulting-services',
                'icon': 'consulting',
                'photo': ('STUDENT GRADUATION PACKAGE AND CERTIFICATES (2).jpg',),
                'short_description': 'Strategic advisory for projects, businesses and digital transformation.',
                'detailed_description': (
                    '<p>Our consulting practice supports organizations and institutions with project '
                    'development, business strategy, digital transformation and youth empowerment '
                    'program design.</p>'
                ),
                'features': [
                    'Project Development', 'Business Strategy', 'Digital Transformation',
                    'Youth Empowerment Programs', 'SME Development Solutions',
                ],
            },
        ]
        for order, data in enumerate(services):
            features = data.pop('features')
            photo_parts = data.pop('photo', None)
            service, _ = Service.objects.update_or_create(
                slug=data['slug'],
                defaults={**data, 'display_order': order, 'active': True, 'featured': True},
            )
            service.features.all().delete()
            for f_order, text in enumerate(features):
                ServiceFeature.objects.create(service=service, text=text, order=f_order)
            if photo_parts and not service.image:
                image = _img(*photo_parts)
                if image:
                    service.image.save(image.name, image, save=True)
        self.stdout.write('Services ✓')

    # -- Core values (verbatim) -------------------------------------------------
    def seed_core_values(self):
        values = [
            ('Empowerment', 'spark', 'We believe in equipping people with the tools, knowledge, and confidence to succeed.'),
            ('Innovation', 'lightbulb', 'We embrace creativity and modern solutions for sustainable growth.'),
            ('Integrity', 'shield', 'We operate with honesty, transparency, and accountability.'),
            ('Reputation', 'award', 'We protect and promote our good name through quality service, transparency and professionalism.'),
            ('Community Impact', 'heart', 'We are committed to creating measurable positive change in society.'),
        ]
        for order, (name, icon, description) in enumerate(values):
            CoreValue.objects.update_or_create(
                slug=name.lower().replace(' ', '-'),
                defaults={'name': name, 'icon': icon, 'description': description, 'display_order': order, 'active': True},
            )
        self.stdout.write('Core values ✓')

    def seed_target_audience(self):
        audiences = [
            ('Youths', 'users'), ('Women', 'heart'), ('Students', 'graduation-cap'),
            ('Graduates', 'award'), ('Entrepreneurs', 'business'), ('SMEs', 'briefcase'),
            ('Startups', 'spark'), ('NGOs', 'handshake'), ('Government Agencies', 'building'),
            ('Educational Institutions', 'graduation-cap'),
        ]
        for order, (name, icon) in enumerate(audiences):
            TargetAudience.objects.update_or_create(
                name=name, defaults={'icon': icon, 'display_order': order, 'active': True},
            )
        self.stdout.write('Target audience ✓')

    def seed_why_choose(self):
        features = [
            ('Practical & Result-Oriented Training', 'target', 'We offer hands-on, outcome-focused training designed for real income generation.'),
            ('Community-Driven Impact', 'heart', 'We aim to create community-driven impact across Northern Nigeria.'),
            ('Sustainable Income Generation', 'growth', 'We focus primarily on helping people build sustainable income.'),
            ('Northern Nigeria Development', 'globe', 'We are passionate about Northern Nigeria’s development.'),
            ('Strong and Dependable Leadership & Mentorship', 'handshake', 'We provide strong and dependable leadership and mentorship.'),
        ]
        for order, (title, icon, description) in enumerate(features):
            WhyChooseFeature.objects.update_or_create(
                title=title, defaults={'icon': icon, 'description': description, 'display_order': order, 'active': True},
            )
        self.stdout.write('Why choose us ✓')

    # -- Founder (verbatim message) ---------------------------------------------
    def seed_founder(self):
        founder, _ = FounderProfile.objects.get_or_create(name='Haleematu Suleiman Basawa')
        founder.position = 'Founder & CEO'
        founder.message = (
            '<p>At NORTHPRENEUR HUB LTD, we believe that talent exists everywhere, but opportunity '
            'does not. Our vision was born from the desire to create a platform where Northern '
            'Nigerians can access the knowledge, skills, and support needed to thrive in today’s '
            'digital economy. We are committed to building a future where Northern Nigerians are '
            'creators of opportunities — not just seekers of them.</p>'
            '<p>We are not just building a business, we are building a movement of transformation, '
            'leadership, and economic empowerment. To us, empowerment is not just our service, it is '
            'our purpose. Our mission remains clear: to empower lives, build businesses, and shape '
            'futures.</p>'
        )
        founder.active = True
        image = _img('fOUNDER CEO', 'IMG-20250618-WA0008.jpg')
        if image and not founder.photo:
            founder.photo.save(image.name, image, save=False)
        founder.save()
        self.stdout.write('Founder ✓')

    # -- About page ---------------------------------------------------------------
    def seed_about_page(self):
        about = AboutPage.load()
        about.heading = 'About Northpreneur Hub'
        about.intro = (
            '<p>NORTHPRENEUR HUB LTD is a forward-thinking digital empowerment and business '
            'development company committed to transforming lives across Northern Nigeria through '
            'innovation, entrepreneurship, and digital opportunities.</p>'
            '<p>We focus on equipping individuals — especially youths, women, students, and aspiring '
            'entrepreneurs — with practical digital skills, business knowledge, and income-generating '
            'opportunities that create sustainable income.</p>'
            '<p>Our mission is to bridge the gap between talent and opportunity by building a '
            'generation of digitally skilled Northern entrepreneurs who can recognize business '
            'opportunities and positively exploit them accordingly.</p>'
        )
        about.cta_text = 'Explore Our Services'
        about.cta_url = '/services/'
        image = _img('IMG_20260702_133209.jpg')
        if image and not about.image:
            about.image.save(image.name, image, save=False)
        about.save()
        self.stdout.write('About page ✓')

    def seed_legal_pages(self):
        # Left empty — no legal text was supplied. The client will author these in admin.
        for title, slug in [('Privacy Policy', 'privacy-policy'), ('Terms & Conditions', 'terms-conditions')]:
            LegalPage.objects.get_or_create(slug=slug, defaults={'title': title, 'content': ''})
        self.stdout.write('Legal pages ✓ (empty — awaiting client-authored text)')

    # -- Gallery categories (database-driven, admin-editable) --------------------
    def seed_gallery_categories(self):
        categories = [
            'Training', 'Graduation & Certification', 'Entrepreneurship',
            'Community & Impact', 'Partnerships & Engagement',
        ]
        for order, name in enumerate(categories):
            GalleryCategory.objects.update_or_create(
                slug=name.lower().replace(' & ', '-').replace(' ', '-'),
                defaults={'name': name, 'display_order': order},
            )
        self.stdout.write('Gallery categories ✓')

    # -- Gallery (real photos, cautious captions grounded in filenames) -----------
    def seed_gallery(self):
        items = [
            ('training', 'TRAINING SESSION.jpg', 'Digital skills training session', ''),
            ('training', 'TRAINING SESSION (2).jpg', 'Training Session', 'Participants at a Northpreneur Hub training session'),
            ('training', 'TRAINING SESSION (4).jpg', 'Northpreneur Hub training in progress', ''),
            ('graduation-certification', 'STUDENT GRADUATION PACKAGE AND CERTIFICATES.jpg', 'Certificate of Competency', 'Graduation package and Certificate of Competency issued to trainees'),
            ('graduation-certification', 'STUDENT GRADUATION PACKAGE AND CERTIFICATES (2).jpg', 'Graduation Package', 'Graduation package prepared for trainees'),
            ('graduation-certification', 'GRADUATION FLYER.jpg', '2026 Batch A Graduation Ceremony', 'Invitation flyer for the 2026 Batch A graduation ceremony'),
            ('entrepreneurship', ('MAGIC CHARCOAL', 'PACKAGED PROCESSED CHARCOAL.jpg'), 'Packaged Charcoal Briquettes', 'Packaged charcoal briquettes from the eco-enterprise training'),
            ('entrepreneurship', ('MAGIC CHARCOAL', 'CHARCOAL MANUAL PRESS.jpg'), 'Charcoal Briquette Press', 'Manual press used in charcoal briquette production'),
            ('entrepreneurship', ('MAGIC CHARCOAL', 'MAGIC CHARCOAL.jpg'), 'Magic Charcoal', 'Finished charcoal briquettes from the eco-enterprise training'),
            ('entrepreneurship', 'DISPLAY OF ECO CRAFT  AND MAGIC CHARCOAL PRODUCTS AT MINISTRY OF YOUTH.jpg', 'Products On Display', 'Trainee products on display at the Ministry of Youth Development'),
            ('entrepreneurship', '1705151523902.JPG', 'Hands-On Craft Making', 'Trainees working on a hands-on craft-making activity'),
            ('entrepreneurship', '1705151523908.JPG', 'Craft Making Session', 'Trainees working on a hands-on craft-making activity'),
            ('community-impact', 'MINISTRY OF YOUTHS.jpg', 'Ministry of Youth Development', 'Engagement with the Ministry of Youth Development'),
            ('community-impact', 'FOUNDER AND CO FOUNDER WITH ASSOC. PROF AHMED ADAMU.jpg', 'With Assoc. Prof. Ahmed Adamu', 'Northpreneur Hub leadership with Assoc. Prof. Ahmed Adamu'),
            ('community-impact', 'IMG_20260306_140112.jpg', 'Graduation Announcement', ''),
            ('partnerships-engagement', ('PARTNERSHIPS', 'NPHL TEAM WITH COMMISSIONER OF YOUTH DEVELOPMENT KADUNA.jpg'), 'With the Commissioner, Kaduna State', 'Northpreneur Hub team with the Commissioner for Youth Development, Kaduna State'),
            ('partnerships-engagement', ('PARTNERSHIPS', 'WITH ABUCONS.jpg'), 'With ABUCONS', 'Engagement with ABUCONS'),
            ('partnerships-engagement', ('PARTNERSHIPS', 'AT MBIT KADUNA.jpg'), 'At MBIT, Kaduna', 'Northpreneur Hub at MBIT, Kaduna'),
        ]
        featured_titles = {
            'Training Session', 'Certificate of Competency', 'Packaged Charcoal Briquettes',
            'Products On Display', 'Ministry of Youth Development', 'With the Commissioner, Kaduna State',
            'Hands-On Craft Making', '2026 Batch A Graduation Ceremony',
        }
        for order, (cat_slug, filename, title, description) in enumerate(items):
            parts = filename if isinstance(filename, tuple) else (filename,)
            image = _img(*parts)
            if not image:
                continue
            category = GalleryCategory.objects.filter(slug=cat_slug).first()
            gallery_item, created = GalleryImage.objects.get_or_create(
                title=title,
                defaults={
                    'category': category, 'description': description, 'display_order': order,
                    'published': True, 'featured': title in featured_titles, 'alt_text': title,
                },
            )
            if created:
                gallery_item.image.save(image.name, image, save=True)
        self.stdout.write('Gallery ✓')

    # -- Programs (real photographic evidence, cautious factual descriptions) ----
    def seed_programs(self):
        programs = [
            {
                'title': 'Digital Skills & Enterprise Graduation Ceremony — 2026 Batch A',
                'slug': 'graduation-ceremony-2026-batch-a',
                'program_type': 'event',
                'short_description': 'Celebrating trainees who completed their digital skills and enterprise training.',
                'full_description': (
                    '<p>Northpreneur Hub Ltd hosted its 2026 Batch A Graduation Ceremony, celebrating '
                    'trainees who completed their digital skills and enterprise training and received '
                    'their Certificates of Competency.</p>'
                ),
                'image': ('GRADUATION FLYER.jpg',),
                'status': 'completed',
                'start_date': '2026-03-08',
                'location': 'Zaria, Kaduna State',
                'cta_text': 'View Our Programs',
            },
            {
                'title': 'Eco-Enterprise: Magic Charcoal Briquette Training',
                'slug': 'magic-charcoal-briquette-training',
                'program_type': 'program',
                'short_description': 'Hands-on training in producing charcoal briquettes as a sustainable micro-enterprise.',
                'full_description': (
                    '<p>Part of our entrepreneurship development track, this hands-on training equips '
                    'participants with the practical skills to produce and package charcoal briquettes '
                    'from recovered waste material — turning a simple process into a sustainable, '
                    'income-generating micro-enterprise.</p>'
                ),
                'image': ('MAGIC CHARCOAL', 'MAGIC CHARCOAL.jpg'),
                'gallery': [
                    ('MAGIC CHARCOAL', 'CHARCOAL MANUAL PRESS.jpg'),
                    ('MAGIC CHARCOAL', 'PACKAGED PROCESSED CHARCOAL.jpg'),
                ],
                'status': 'ongoing',
                'cta_text': 'Ask About This Program',
            },
            {
                'title': 'Digital Skills Training Cohort',
                'slug': 'digital-skills-training-cohort',
                'program_type': 'program',
                'short_description': 'Practical training in social media, content creation, and digital marketing.',
                'full_description': (
                    '<p>An ongoing cohort-based training program covering the core competencies of our '
                    'Digital Skills Training service — social media advertisement, content creation, '
                    'digital marketing, personal branding and more.</p>'
                ),
                'image': ('TRAINING SESSION.jpg',),
                'gallery': [('TRAINING SESSION (2).jpg',), ('TRAINING SESSION (4).jpg',)],
                'status': 'ongoing',
                'cta_text': 'Apply Now',
            },
        ]
        for order, data in enumerate(programs):
            image_parts = data.pop('image', None)
            gallery_parts = data.pop('gallery', [])
            start_date = data.pop('start_date', None)
            program, _ = Program.objects.update_or_create(
                slug=data['slug'],
                defaults={
                    **data, 'display_order': order, 'featured': True, 'published': True,
                    'start_date': start_date,
                },
            )
            if image_parts:
                image = _img(*image_parts)
                if image and not program.image:
                    program.image.save(image.name, image, save=True)
            if gallery_parts and not program.gallery.exists():
                from programs.models import ProgramImage
                for g_order, parts in enumerate(gallery_parts):
                    image = _img(*parts)
                    if image:
                        pi = ProgramImage(program=program, order=g_order)
                        pi.image.save(image.name, image, save=True)
        self.stdout.write(self.style.WARNING(
            'Programs ✓ — seeded from real photos with cautious descriptions; please review before launch.'
        ))
