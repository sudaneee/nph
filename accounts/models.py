from django.conf import settings
from django.db import models


class Profile(models.Model):
    """Student extras kept off the auth User so existing admin accounts are untouched."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True, help_text='Required by Zainpay at checkout.')

    def __str__(self):
        return f'Profile of {self.user}'

    @classmethod
    def for_user(cls, user):
        profile, _ = cls.objects.get_or_create(user=user)
        return profile
