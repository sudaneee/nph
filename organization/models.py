from django.db import models
from django_ckeditor_5.fields import CKEditor5Field

from sitecore.icons import ICON_CHOICES
from sitecore.models import TimeStampedModel, OrderedMixin, IMAGE_VALIDATORS


class FounderProfile(TimeStampedModel):
    """Singleton-style — realistically one row (the current Founder & CEO)."""
    name = models.CharField(max_length=150)
    position = models.CharField(max_length=150, default='Founder & CEO')
    photo = models.ImageField(upload_to='team/', blank=True, null=True, validators=IMAGE_VALIDATORS)
    message = CKEditor5Field(config_name='richtext')
    linkedin_url = models.URLField(blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Founder's Message"
        verbose_name_plural = "Founder's Message"

    def __str__(self):
        return self.name


class TeamMember(OrderedMixin):
    name = models.CharField(max_length=150)
    role = models.CharField(max_length=150)
    photo = models.ImageField(upload_to='team/', blank=True, null=True, validators=IMAGE_VALIDATORS)
    bio = models.TextField(blank=True)
    linkedin_url = models.URLField(blank=True)
    active = models.BooleanField(default=True)

    class Meta(OrderedMixin.Meta):
        verbose_name = 'Team Member'

    def __str__(self):
        return f'{self.name} — {self.role}'


class CoreValue(OrderedMixin):
    name = models.CharField(max_length=80)
    slug = models.SlugField(max_length=80, unique=True)
    short_statement = models.CharField(max_length=200, blank=True)
    description = models.TextField()
    icon = models.CharField(max_length=30, choices=ICON_CHOICES, default='spark')
    active = models.BooleanField(default=True)

    class Meta(OrderedMixin.Meta):
        verbose_name = 'Core Value'

    def __str__(self):
        return self.name


class TargetAudience(OrderedMixin):
    name = models.CharField(max_length=80)
    icon = models.CharField(max_length=30, choices=ICON_CHOICES, default='users')
    active = models.BooleanField(default=True)

    class Meta(OrderedMixin.Meta):
        verbose_name = 'Target Audience'
        verbose_name_plural = 'Target Audiences'

    def __str__(self):
        return self.name


class WhyChooseFeature(OrderedMixin):
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=30, choices=ICON_CHOICES, default='check')
    active = models.BooleanField(default=True)

    class Meta(OrderedMixin.Meta):
        verbose_name = 'Why Choose Us — Feature'
        verbose_name_plural = 'Why Choose Us — Features'

    def __str__(self):
        return self.title


class ImpactStatistic(OrderedMixin):
    """Left empty until the client supplies real, verifiable numbers — never fabricated."""
    label = models.CharField(max_length=100)
    number = models.CharField(max_length=20, help_text='e.g. "500+", "1,200"')
    description = models.CharField(max_length=200, blank=True)
    icon = models.CharField(max_length=30, choices=ICON_CHOICES, default='chart')
    active = models.BooleanField(default=True)

    class Meta(OrderedMixin.Meta):
        verbose_name = 'Impact Statistic'

    def __str__(self):
        return f'{self.number} {self.label}'


class Testimonial(OrderedMixin):
    name = models.CharField(max_length=150)
    role_organization = models.CharField(max_length=200, blank=True)
    photo = models.ImageField(upload_to='testimonials/', blank=True, null=True, validators=IMAGE_VALIDATORS)
    quote = models.TextField()
    active = models.BooleanField(default=True)

    class Meta(OrderedMixin.Meta):
        verbose_name = 'Testimonial'

    def __str__(self):
        return self.name


class FAQ(OrderedMixin):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    active = models.BooleanField(default=True)

    class Meta(OrderedMixin.Meta):
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'

    def __str__(self):
        return self.question
