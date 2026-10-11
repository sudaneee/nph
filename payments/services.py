import logging

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.urls import reverse
from django.utils import timezone

from learning.models import Enrollment
from . import zainpay
from .models import Payment

logger = logging.getLogger(__name__)


def apply_deposit(payment, paid_kobo, details):
    """
    Record a confirmed deposit against `payment` and enroll the student.

    Idempotent and race-safe (the callback redirect and the webhook can arrive
    together): the row lock means enrollment + email happen exactly once.
    Returns the payment's resulting status.
    """
    with transaction.atomic():
        payment = Payment.objects.select_for_update().get(pk=payment.pk)
        if payment.status == 'success':
            return payment.status
        payment.gateway_response = details or {}
        if paid_kobo < payment.minimum_kobo:
            logger.error('Zainpay underpayment on %s: paid %s kobo, expected at least %s',
                         payment.reference, paid_kobo, payment.minimum_kobo)
            payment.status = 'failed'
            payment.save(update_fields=['status', 'gateway_response'])
            return payment.status
        payment.status = 'success'
        payment.paid_at = timezone.now()
        payment.save(update_fields=['status', 'gateway_response', 'paid_at'])
        Enrollment.objects.get_or_create(user=payment.user, course=payment.course, defaults={'source': 'paid'})
        transaction.on_commit(lambda: send_payment_confirmation_email(payment))
    return payment.status


def confirm_payment(payment):
    """
    Look the payment up in the Zainbox's transaction history and, if Zainpay has
    the deposit, enroll the student. Never trusts what the browser claims.
    Leaves the payment pending when Zainpay has no matching deposit yet.
    """
    if payment.status == 'success':
        return payment.status
    paid_kobo = zainpay.find_deposit_kobo(payment.reference)
    if paid_kobo is None:
        return payment.status
    return apply_deposit(payment, paid_kobo, {'source': 'transaction_history', 'amount_kobo': paid_kobo})


def send_payment_confirmation_email(payment):
    """Best-effort receipt to the student — a mail failure must never undo an enrollment."""
    user = payment.user
    if not user.email:
        return False
    course_url = f'{settings.SITE_PROTOCOL}://{settings.SITE_DOMAIN}' + reverse(
        'learning:course_learn', kwargs={'slug': payment.course.slug})
    try:
        send_mail(
            subject=f'Payment confirmed — {payment.course.title}',
            message=(
                f'Dear {user.get_full_name() or user.email},\n\n'
                f'We have received your payment of ₦{payment.amount:,} for "{payment.course.title}" '
                f'(course ₦{payment.course_price or payment.amount:,} + payment processing fee).\n'
                f'Payment reference: {payment.reference}\n\n'
                f'You can start learning right away:\n{course_url}\n\n'
                'Northpreneur Hub Ltd'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return True
    except Exception:
        logger.exception('Failed to send payment confirmation email for %s', payment.reference)
        return False
