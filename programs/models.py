from datetime import date

from django.db import models
from django.urls import reverse
from django_ckeditor_5.fields import CKEditor5Field

from sitecore.models import TimeStampedModel, SEOFields, OrderedMixin, IMAGE_VALIDATORS

PROGRAM_TYPES = [
    ('program', 'Training Program'),
    ('workshop', 'Workshop'),
    ('event', 'Event'),
    ('opportunity', 'Opportunity'),
    ('call_for_application', 'Call for Application'),
    ('community_initiative', 'Community Initiative'),
]

# Program listing (/programs/) vs Opportunities listing (/opportunities/) — one flexible
# model, two type-filtered querysets.
PROGRAM_LISTING_TYPES = ['program', 'workshop', 'event', 'community_initiative']
OPPORTUNITY_LISTING_TYPES = ['opportunity', 'call_for_application']

STATUS_CHOICES = [
    ('upcoming', 'Upcoming'),
    ('ongoing', 'Ongoing'),
    ('completed', 'Completed'),
    ('closed', 'Closed'),
]


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(published=True)


class Program(TimeStampedModel, SEOFields):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    program_type = models.CharField(max_length=25, choices=PROGRAM_TYPES, default='program', db_index=True)
    short_description = models.CharField(max_length=250)
    full_description = CKEditor5Field(config_name='richtext')
    image = models.ImageField(upload_to='programs/', blank=True, null=True, validators=IMAGE_VALIDATORS)

    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    application_deadline = models.DateField(blank=True, null=True)
    location = models.CharField(max_length=200, blank=True)

    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='upcoming')
    cta_text = models.CharField(max_length=50, default='Apply Now')
    external_application_url = models.URLField(blank=True,
                                                 help_text='Leave blank to link to this item’s own detail page.')

    featured = models.BooleanField(default=False)
    published = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0, db_index=True)

    objects = models.Manager()
    live = PublishedManager()

    class Meta:
        ordering = ['display_order', '-start_date', '-id']
        indexes = [models.Index(fields=['program_type', 'published'])]
        verbose_name = 'Program / Opportunity'
        verbose_name_plural = 'Programs & Opportunities'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        url_name = 'programs:opportunity_detail' if self.program_type in OPPORTUNITY_LISTING_TYPES else 'programs:program_detail'
        return reverse(url_name, kwargs={'slug': self.slug})

    def get_cta_url(self):
        return self.external_application_url or self.get_absolute_url()

    @property
    def is_opportunity(self):
        return self.program_type in OPPORTUNITY_LISTING_TYPES

    @property
    def is_open(self):
        if self.status == 'closed':
            return False
        if self.application_deadline:
            return self.application_deadline >= date.today()
        return self.status in ('upcoming', 'ongoing')


class ProgramImage(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='gallery')
    image = models.ImageField(upload_to='programs/gallery/', validators=IMAGE_VALIDATORS)
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Program Gallery Image'

    def __str__(self):
        return self.caption or f'Image for {self.program.title}'
