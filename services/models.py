from django.db import models
from django.urls import reverse
from django_ckeditor_5.fields import CKEditor5Field

from sitecore.icons import ICON_CHOICES
from sitecore.models import TimeStampedModel, SEOFields, OrderedMixin, IMAGE_VALIDATORS


class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(active=True)


class Service(TimeStampedModel, SEOFields, OrderedMixin):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True)
    short_description = models.CharField(max_length=250)
    detailed_description = CKEditor5Field(config_name='richtext')
    icon = models.CharField(max_length=30, choices=ICON_CHOICES, default='business')
    image = models.ImageField(upload_to='services/', blank=True, null=True, validators=IMAGE_VALIDATORS)
    cta_text = models.CharField(max_length=50, default='Learn More')
    cta_url = models.CharField(max_length=255, blank=True,
                                help_text='Leave blank to link to this service’s detail page.')
    featured = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    objects = models.Manager()
    published = ActiveManager()

    class Meta(OrderedMixin.Meta):
        verbose_name = 'Service'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('services:detail', kwargs={'slug': self.slug})

    def get_cta_url(self):
        return self.cta_url or self.get_absolute_url()


class ServiceFeature(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='features')
    text = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Service Feature'

    def __str__(self):
        return self.text
