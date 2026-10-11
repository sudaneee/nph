import json
import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from accounts.models import Profile
from learning.models import Course, Enrollment
from . import zainpay
from .models import Payment
from .services import apply_deposit, confirm_payment

logger = logging.getLogger(__name__)

CANCELLED_STATUSES = ('cancel', 'cancelled', 'failed', 'failure')


@login_required
@require_POST
def checkout(request, slug):
    course = get_object_or_404(Course.live, slug=slug)
    learn_url = reverse('learning:course_learn', kwargs={'slug': course.slug})

    if Enrollment.objects.filter(user=request.user, course=course).exists():
        return redirect(learn_url)

    if course.is_free:
        Enrollment.objects.create(user=request.user, course=course, source='free')
        messages.success(request, f'You are enrolled in “{course.title}”. Enjoy the course!')
        return redirect(learn_url)

    if not zainpay.is_configured():
        messages.error(request, 'Online payment is not available yet. Please contact us to enroll.')
        return redirect(course)

    profile = Profile.for_user(request.user)
    if not profile.phone:
        messages.info(request, 'Please add your phone number — it is required for payment.')
        return redirect(f"{reverse('accounts:profile')}?next={course.get_absolute_url()}")

    payment = Payment.objects.create(user=request.user, course=course, amount=course.price)
    callback_url = request.build_absolute_uri(reverse('payments:callback', kwargs={'reference': payment.reference}))
    try:
        checkout_url = zainpay.initialize_checkout(
            email=request.user.email, mobile_number=profile.phone, amount=payment.amount,
            txn_ref=payment.reference, callback_url=callback_url,
        )
    except zainpay.ZainpayError as exc:
        payment.status = 'failed'
        payment.gateway_response = {'initialize_error': str(exc)}
        payment.save(update_fields=['status', 'gateway_response'])
        messages.error(request, 'We could not start the payment. Please try again in a moment.')
        return redirect(course)
    return redirect(checkout_url)


@csrf_exempt
def callback(request, reference):
    """
    Where Zainpay sends the student back (it appends ?txnRef=…&status=…). Not
    login/CSRF-gated: as in GIIA, Zainpay may also hit it server-to-server. The
    status param is only used for messaging — access is granted solely when the
    deposit shows up in our Zainbox's transaction history.
    """
    logger.info('Zainpay callback hit: method=%s ref=%s GET=%s', request.method, reference, dict(request.GET))
    payment = get_object_or_404(Payment.objects.select_related('course'), reference=reference)
    status = confirm_payment(payment)
    if status == 'success':
        messages.success(request, f'Payment received — welcome to “{payment.course.title}”!')
        return redirect('learning:course_learn', slug=payment.course.slug)
    cancelled = (request.GET.get('status') or '').lower() in CANCELLED_STATUSES
    return render(request, 'payments/status.html', {
        'payment': payment, 'status': status, 'cancelled': cancelled,
        'crumbs': [('Courses', reverse('learning:course_list')), ('Payment', None)],
    })


@csrf_exempt
@require_POST
def webhook(request):
    """
    Zainpay deposit notification, signed with our secret key ("Zainpay-Signature").
    Register https://<domain>/payments/webhook/zainpay/ as the Zainbox callback URL.
    Returns 200 for anything we choose to ignore so Zainpay doesn't retry forever;
    only a bad signature gets 401.
    """
    raw_body = request.body
    signature = request.headers.get('Zainpay-Signature')
    logger.info('Zainpay webhook inbound - body: %s', raw_body.decode('utf-8', errors='replace')[:2000])

    if not zainpay.verify_webhook_signature(raw_body, signature):
        logger.warning('Zainpay webhook rejected: invalid signature.')
        return JsonResponse({'error': 'Invalid signature'}, status=401)

    try:
        payload = json.loads(raw_body)
    except ValueError:
        return JsonResponse({'status': 'ignored'})

    data = payload.get('data') if isinstance(payload.get('data'), dict) else payload
    if payload.get('event') != 'deposit.success' or data.get('zainboxCode') != settings.ZAINPAY_ZAINBOX_CODE:
        return JsonResponse({'status': 'ignored'})

    payment = Payment.objects.filter(reference=data.get('txnRef')).first()
    if not payment:
        logger.warning('Zainpay webhook: no Payment for txnRef %s', data.get('txnRef'))
        return JsonResponse({'status': 'ignored'})
    if payment.status == 'success':
        return JsonResponse({'status': 'already_processed'})

    try:
        paid_kobo = int(float(data['depositedAmount']))  # kobo, like GIIA's webhook
    except (KeyError, TypeError, ValueError):
        status = confirm_payment(payment)  # signed but no amount — fall back to history lookup
    else:
        status = apply_deposit(payment, paid_kobo, data)
    return JsonResponse({'status': status})
