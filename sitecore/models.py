from django.core.validators import FileExtensionValidator
from django.db import models

IMAGE_VALIDATORS = [FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])]


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SEOFields(models.Model):
    """Reusable per-object SEO fieldset, edited inline on each content model's admin."""
    seo_title = models.CharField(
        max_length=70, blank=True,
        help_text='Overrides the browser tab / search result title. Defaults to the page title if left blank.',
    )
    meta_description = models.CharField(
        max_length=160, blank=True,
        help_text='Shown in search results. Aim for 120–160 characters.',
    )
    og_image = models.ImageField(
        upload_to='seo/', blank=True, null=True, validators=IMAGE_VALIDATORS,
        help_text='Image shown when this page is shared on social media. Defaults to the site OG image.',
    )
    canonical_url = models.URLField(blank=True)
    robots_index = models.BooleanField(default=True, help_text='Allow search engines to index this page.')
    robots_follow = models.BooleanField(default=True, help_text='Allow search engines to follow links on this page.')

    class Meta:
        abstract = True

    def get_seo_title(self, fallback):
        return self.seo_title or fallback

    def get_meta_description(self, fallback=''):
        return self.meta_description or fallback


class OrderedMixin(models.Model):
    display_order = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        abstract = True
        ordering = ['display_order', 'id']


class SiteSettings(TimeStampedModel):
    """Singleton — global site identity, contact details and defaults. Managed via the admin."""
    site_name = models.CharField(max_length=150, default='Northpreneur Hub Ltd')
    tagline = models.CharField(max_length=200, default='Empowering Northern Nigerians through Digital Opportunities')
    logo = models.ImageField(upload_to='branding/', blank=True, null=True, validators=IMAGE_VALIDATORS,
                              help_text='Optional. If left blank the site uses a designed text wordmark.')
    logo_dark = models.ImageField(upload_to='branding/', blank=True, null=True, validators=IMAGE_VALIDATORS,
                                   help_text='Optional alternate logo for dark backgrounds.')
    favicon = models.ImageField(upload_to='branding/', blank=True, null=True, validators=IMAGE_VALIDATORS)

    phone_primary = models.CharField(max_length=30, blank=True)
    phone_secondary = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    map_embed_url = models.URLField(blank=True, help_text='Optional Google Maps embed URL for the contact page.')

    mission_statement = models.TextField(blank=True)
    vision_statement = models.TextField(blank=True)

    footer_about = models.TextField(blank=True, help_text='Short company summary shown in the footer.')
    copyright_text = models.CharField(max_length=200, blank=True,
                                       help_text='e.g. "© {year} Northpreneur Hub Ltd. All rights reserved."')

    default_seo_title = models.CharField(max_length=70, blank=True)
    default_meta_description = models.CharField(max_length=160, blank=True)
    default_og_image = models.ImageField(upload_to='seo/', blank=True, null=True, validators=IMAGE_VALIDATORS)
    google_analytics_id = models.CharField(max_length=30, blank=True)

    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class NavigationItem(OrderedMixin):
    label = models.CharField(max_length=50)
    url = models.CharField(max_length=255, help_text='Internal path (e.g. /about/) or a full URL.')
    open_in_new_tab = models.BooleanField(default=False)
    is_cta = models.BooleanField(default=False, help_text='Style this item as the primary nav button.')
    active = models.BooleanField(default=True)

    class Meta(OrderedMixin.Meta):
        verbose_name = 'Navigation Item'

    def __str__(self):
        return self.label


class FooterLink(OrderedMixin):
    GROUP_CHOICES = [
        ('company', 'Company'),
        ('services', 'Services'),
        ('programs', 'Programs'),
        ('legal', 'Legal'),
    ]
    group = models.CharField(max_length=20, choices=GROUP_CHOICES, default='company')
    label = models.CharField(max_length=50)
    url = models.CharField(max_length=255)
    open_in_new_tab = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    class Meta(OrderedMixin.Meta):
        verbose_name = 'Footer Link'
        ordering = ['group', 'display_order', 'id']

    def __str__(self):
        return f'{self.get_group_display()} — {self.label}'


class SocialLink(OrderedMixin):
    PLATFORM_CHOICES = [
        ('instagram', 'Instagram'),
        ('tiktok', 'TikTok'),
        ('facebook', 'Facebook'),
        ('linkedin', 'LinkedIn'),
        ('youtube', 'YouTube'),
        ('whatsapp', 'WhatsApp'),
    ]
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, unique=True)
    url = models.URLField()
    active = models.BooleanField(default=True)

    class Meta(OrderedMixin.Meta):
        verbose_name = 'Social Link'

    def __str__(self):
        return self.get_platform_display()

    @property
    def icon_key(self):
        return self.platform


class HeroSlide(TimeStampedModel):
    headline = models.CharField(max_length=200)
    subheadline = models.TextField(max_length=400)
    badge_text = models.CharField(max_length=100, blank=True,
                                   help_text='Small credibility indicator above the headline.')
    primary_cta_text = models.CharField(max_length=50, blank=True)
    primary_cta_url = models.CharField(max_length=255, blank=True)
    secondary_cta_text = models.CharField(max_length=50, blank=True)
    secondary_cta_url = models.CharField(max_length=255, blank=True)
    background_image = models.ImageField(upload_to='hero/', blank=True, null=True, validators=IMAGE_VALIDATORS)

    # Small 3-up stat strip beneath the CTA buttons (e.g. "04 / Core Service Areas").
    stat1_value = models.CharField(max_length=20, blank=True)
    stat1_label = models.CharField(max_length=40, blank=True)
    stat2_value = models.CharField(max_length=20, blank=True)
    stat2_label = models.CharField(max_length=40, blank=True)
    stat3_value = models.CharField(max_length=20, blank=True)
    stat3_label = models.CharField(max_length=40, blank=True)

    # Floating label on the hero photo collage (e.g. "Skills to Income").
    collage_label_title = models.CharField(max_length=60, blank=True)
    collage_label_subtitle = models.CharField(max_length=100, blank=True)

    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Hero Slide'

    def __str__(self):
        return self.headline


class HomepageSection(OrderedMixin):
    SECTION_TYPES = [
        ('trust_strip', 'Trust / Credibility Strip'),
        ('about', 'About / Purpose'),
        ('mission_vision', 'Mission & Vision'),
        ('services', 'Services'),
        ('why_choose_us', 'Why Choose Northpreneur Hub'),
        ('audience', 'Target Audience'),
        ('core_values', 'Core Values'),
        ('founder', "Founder's Message"),
        ('impact', 'Impact'),
        ('image_grid', 'Creative Image Grid'),
        ('programs_featured', 'Featured Programs'),
        ('blog_featured', 'Latest Insights'),
        ('gallery_preview', 'Gallery Preview — Stories in Motion'),
        ('cta', 'Call To Action'),
    ]
    BACKGROUND_CHOICES = [
        ('light', 'Light'),
        ('dark', 'Dark'),
        ('image', 'Image-led'),
    ]
    section_type = models.CharField(max_length=30, choices=SECTION_TYPES, unique=True)
    title = models.CharField(max_length=200, blank=True, help_text='Overrides the default section heading.')
    subtitle = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='sections/', blank=True, null=True, validators=IMAGE_VALIDATORS)
    background_style = models.CharField(max_length=10, choices=BACKGROUND_CHOICES, default='light')
    enabled = models.BooleanField(default=True)

    class Meta(OrderedMixin.Meta):
        verbose_name = 'Homepage Section'

    def __str__(self):
        return self.get_section_type_display()


class CTASection(TimeStampedModel):
    title = models.CharField(max_length=200)
    subtitle = models.TextField(blank=True)
    primary_button_text = models.CharField(max_length=50, blank=True)
    primary_button_url = models.CharField(max_length=255, blank=True)
    secondary_button_text = models.CharField(max_length=50, blank=True)
    secondary_button_url = models.CharField(max_length=255, blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'CTA Section'
        verbose_name_plural = 'CTA Sections'

    def __str__(self):
        return self.title


class GalleryCategory(OrderedMixin):
    """Database-driven gallery categories — admin can add/rename/reorder freely."""
    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(max_length=70, unique=True)

    class Meta(OrderedMixin.Meta):
        verbose_name = 'Gallery Category'
        verbose_name_plural = 'Gallery Categories'

    def __str__(self):
        return self.name


class GalleryImage(OrderedMixin):
    title = models.CharField(max_length=150, blank=True)
    image = models.ImageField(upload_to='gallery/', validators=IMAGE_VALIDATORS)
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        GalleryCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='images',
    )
    date = models.DateField(blank=True, null=True, help_text='When this photo was taken (optional).')
    caption = models.CharField(max_length=255, blank=True)
    alt_text = models.CharField(max_length=200, blank=True)
    featured = models.BooleanField(default=False, help_text='Show on the homepage "Stories in Motion" preview.')
    published = models.BooleanField(default=True)

    class Meta(OrderedMixin.Meta):
        verbose_name = 'Gallery Image'

    def __str__(self):
        return self.title or f'{self.category or "Uncategorized"} photo #{self.pk}'
