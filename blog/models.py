import math

from django.db import models
from django.urls import reverse
from django.utils import timezone
from django_ckeditor_5.fields import CKEditor5Field

from sitecore.models import TimeStampedModel, SEOFields, IMAGE_VALIDATORS


class Author(TimeStampedModel):
    name = models.CharField(max_length=150)
    avatar = models.ImageField(upload_to='blog/authors/', blank=True, null=True, validators=IMAGE_VALIDATORS)
    role = models.CharField(max_length=150, blank=True)
    bio = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Author'

    def __str__(self):
        return self.name


class BlogCategory(models.Model):
    name = models.CharField(max_length=80)
    slug = models.SlugField(max_length=90, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Blog Category'
        verbose_name_plural = 'Blog Categories'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('blog:category', kwargs={'slug': self.slug})


class BlogTag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=60, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Blog Tag'

    def __str__(self):
        return self.name


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(published=True, published_date__lte=timezone.now())


class BlogPost(TimeStampedModel, SEOFields):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    excerpt = models.CharField(max_length=300)
    content = CKEditor5Field(config_name='richtext')
    featured_image = models.ImageField(upload_to='blog/', blank=True, null=True, validators=IMAGE_VALIDATORS)
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    tags = models.ManyToManyField(BlogTag, blank=True, related_name='posts')
    published_date = models.DateTimeField(default=timezone.now)
    featured = models.BooleanField(default=False)
    published = models.BooleanField(default=False)

    objects = models.Manager()
    live = PublishedManager()

    class Meta:
        ordering = ['-published_date']
        indexes = [models.Index(fields=['published', 'published_date'])]
        verbose_name = 'Blog Post'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:detail', kwargs={'slug': self.slug})

    @property
    def reading_time(self):
        import re
        word_count = len(re.sub('<[^<]+?>', '', self.content).split())
        return max(1, math.ceil(word_count / 200))
