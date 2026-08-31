from django.db import models

from sitecore.models import TimeStampedModel


class ContactMessage(TimeStampedModel):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    organization = models.CharField(max_length=150, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()

    is_read = models.BooleanField(default=False)
    is_responded = models.BooleanField(default=False)
    internal_notes = models.TextField(blank=True, help_text='Private notes — not visible to the sender.')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Message'

    def __str__(self):
        return f'{self.subject} — {self.name}'


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=150, blank=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-subscribed_at']
        verbose_name = 'Newsletter Subscriber'

    def __str__(self):
        return self.email
