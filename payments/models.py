import secrets

from django.conf import settings
from django.db import models

from learning.models import Course


def _reference():
    return 'NPH' + secrets.token_hex(8).upper()


class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Successful'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='payments')
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name='payments')
    reference = models.CharField(max_length=40, unique=True, default=_reference, editable=False)
    amount = models.PositiveIntegerField(help_text='Naira, as charged at checkout.')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', db_index=True)
    gateway_response = models.JSONField(default=dict, blank=True,
                                        help_text='Last verification response from Zainpay.')
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.reference} — {self.user} — ₦{self.amount:,}'

    @property
    def amount_kobo(self):
        return self.amount * 100
