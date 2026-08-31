from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django_ckeditor_5.fields import CKEditor5Field

from sitecore.models import TimeStampedModel, SEOFields, IMAGE_VALIDATORS

# These top-level path segments are already routed elsewhere — a LegalPage slug
# must not collide with them, since legal pages are served from the URL root.
RESERVED_SLUGS = {
    'about', 'services', 'programs', 'opportunities', 'insights', 'contact',
    'admin', 'ckeditor5', 'search', 'sitemap.xml', 'robots.txt', 'media', 'static',
}


class AboutPage(TimeStampedModel, SEOFields):
    """Singleton — the full "our story" content for the About page."""
    heading = models.CharField(max_length=200, default='About Northpreneur Hub')
    intro = CKEditor5Field(config_name='richtext')
    image = models.ImageField(upload_to='pages/', blank=True, null=True, validators=IMAGE_VALIDATORS)
    secondary_image = models.ImageField(upload_to='pages/', blank=True, null=True, validators=IMAGE_VALIDATORS)
    cta_text = models.CharField(max_length=50, blank=True)
    cta_url = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = 'About Page'
        verbose_name_plural = 'About Page'

    def __str__(self):
        return self.heading

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1, defaults={'intro': ''})
        return obj


class LegalPage(TimeStampedModel, SEOFields):
    title = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True)
    content = CKEditor5Field(config_name='richtext', blank=True)

    class Meta:
        verbose_name = 'Legal Page'

    def __str__(self):
        return self.title

    def clean(self):
        if self.slug in RESERVED_SLUGS:
            raise ValidationError({'slug': f'"{self.slug}" is a reserved URL and can’t be used as a page slug.'})

    def get_absolute_url(self):
        return reverse('pages:legal', kwargs={'slug': self.slug})
