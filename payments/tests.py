import json
from unittest import mock

import requests
from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from accounts.models import Profile
from learning.models import Enrollment
from learning.tests import make_course
from . import zainpay
from .fees import processing_fee, total_with_zainpay_charge
from .models import Payment

User = get_user_model()

ZAINPAY_ON = dict(ZAINPAY_PUBLIC_KEY='pk_test', ZAINPAY_SECRET_KEY='sk_test', ZAINPAY_ZAINBOX_CODE='box123',
                  ZAINPAY_BASE_URL='https://sandbox.zainpay.ng', ZAINPAY_ACCOUNT_NUMBER='4812000000')


def http_response(body, status=200):
    resp = mock.Mock(status_code=status, text=json.dumps(body))
    resp.json.return_value = body
    return resp


def history(*txns):
    return http_response({'code': '00', 'data': list(txns)})


def deposit(ref, kobo):
    return {'transactionRef': ref, 'transactionType': 'deposit', 'amount': kobo}


@override_settings(**ZAINPAY_ON)
class CheckoutTests(TestCase):
    def setUp(self):
        self.course, _, _ = make_course(price=15000)
        self.user = User.objects.create_user('u', email='u@example.com', password='pw')
        Profile.objects.create(user=self.user, phone='08031234567')
        self.client.force_login(self.user)
        self.checkout_url = reverse('payments:checkout', kwargs={'slug': self.course.slug})

    def test_checkout_sends_naira_bank_transfer_to_our_zainbox(self):
        with mock.patch('requests.post', return_value=http_response(
                {'code': '00', 'data': 'https://checkout.zainpay.ng/x'})) as post:
            resp = self.client.post(self.checkout_url)
        self.assertRedirects(resp, 'https://checkout.zainpay.ng/x', fetch_redirect_response=False)
        payment = Payment.objects.get()
        url = post.call_args.args[0]
        body = post.call_args.kwargs['json']
        self.assertEqual(url, 'https://sandbox.zainpay.ng/zainbox/card/initialize/payment')
        self.assertEqual(post.call_args.kwargs['headers']['Authorization'], 'Bearer pk_test')
        self.assertEqual(body['amount'], '15280')  # naira incl. 1.5% + ₦50, plain string — not kobo
        self.assertEqual((payment.course_price, payment.amount), (15000, 15280))
        self.assertEqual(body['paymentChannels'], ['bank_transfer'])
        self.assertEqual(body['zainboxCode'], 'box123')
        self.assertEqual(body['txnRef'], payment.reference)
        self.assertEqual(body['mobileNumber'], '08031234567')
        self.assertTrue(body['callBackUrl'].endswith(f'/payments/callback/{payment.reference}/'))
        self.assertFalse(Enrollment.objects.exists())

    def test_checkout_requires_post(self):
        self.assertEqual(self.client.get(self.checkout_url).status_code, 405)

    def test_free_course_enrolls_without_payment(self):
        self.course.price = 0
        self.course.save()
        resp = self.client.post(self.checkout_url)
        self.assertRedirects(resp, reverse('learning:course_learn', kwargs={'slug': self.course.slug}),
                             fetch_redirect_response=False)
        self.assertEqual(Enrollment.objects.get().source, 'free')
        self.assertFalse(Payment.objects.exists())

    def test_missing_phone_sends_to_profile(self):
        Profile.objects.filter(user=self.user).update(phone='')
        resp = self.client.post(self.checkout_url)
        self.assertTrue(resp['Location'].startswith(reverse('accounts:profile')))

    @override_settings(ZAINPAY_PUBLIC_KEY='')
    def test_unconfigured_gateway_does_not_charge(self):
        resp = self.client.post(self.checkout_url)
        self.assertRedirects(resp, self.course.get_absolute_url())
        self.assertFalse(Payment.objects.exists())

    def test_gateway_rejection_marks_payment_failed(self):
        with mock.patch('requests.post', return_value=http_response({'code': '04', 'description': 'Invalid_amount'})):
            resp = self.client.post(self.checkout_url)
        self.assertRedirects(resp, self.course.get_absolute_url())
        payment = Payment.objects.get()
        self.assertEqual(payment.status, 'failed')
        self.assertEqual(payment.gateway_response, {'initialize_error': 'Invalid_amount'})

    def test_network_error_marks_payment_failed(self):
        with mock.patch('requests.post', side_effect=requests.ConnectionError('down')):
            self.client.post(self.checkout_url)
        self.assertEqual(Payment.objects.get().status, 'failed')


@override_settings(**ZAINPAY_ON)
class CallbackTests(TestCase):
    def setUp(self):
        self.course, _, _ = make_course(price=15000)
        self.user = User.objects.create_user('u', email='u@example.com', password='pw', first_name='Amina')
        self.payment = Payment.objects.create(user=self.user, course=self.course, course_price=15000, amount=15280)
        self.callback = reverse('payments:callback', kwargs={'reference': self.payment.reference})

    def test_enrolls_when_deposit_is_in_zainbox_history(self):
        with mock.patch('requests.get', return_value=history(deposit('other', 1), deposit(self.payment.reference, 1528000))) as get,                 self.captureOnCommitCallbacks(execute=True):
            resp = self.client.get(self.callback + f'?txnRef={self.payment.reference}&status=success')
        get.assert_called_once()
        self.assertEqual(get.call_args.args[0],
                         'https://sandbox.zainpay.ng/virtual-account/wallet/transactions/4812000000')
        self.assertRedirects(resp, reverse('learning:course_learn', kwargs={'slug': self.course.slug}),
                             fetch_redirect_response=False)
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, 'success')
        self.assertEqual(Enrollment.objects.get().source, 'paid')
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.payment.reference, mail.outbox[0].body)
        self.assertIn('₦15,280', mail.outbox[0].body)

    def test_status_param_alone_grants_nothing(self):
        with mock.patch('requests.get', return_value=history()):
            resp = self.client.get(self.callback + '?status=success')
        self.assertContains(resp, 'Check again')
        self.assertFalse(Enrollment.objects.exists())
        self.assertEqual(len(mail.outbox), 0)

    def test_cancelled_checkout_message(self):
        with mock.patch('requests.get', return_value=history()):
            resp = self.client.get(self.callback + '?status=cancelled')
        self.assertContains(resp, 'was not completed')
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, 'pending')

    def test_withdrawal_with_same_ref_is_not_a_deposit(self):
        withdrawal = {'transactionRef': self.payment.reference, 'transactionType': 'withdrawal', 'amount': 1500000}
        with mock.patch('requests.get', return_value=history(withdrawal)):
            self.client.get(self.callback)
        self.assertFalse(Enrollment.objects.exists())

    def test_deposit_reported_net_of_zainpay_fee_still_counts(self):
        net = 1528000 - (round(15280 * 0.015) + 50) * 100  # what we keep after Zainpay's cut
        with mock.patch('requests.get', return_value=history(deposit(self.payment.reference, net))):
            self.client.get(self.callback)
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, 'success')

    def test_underpayment_fails(self):
        with mock.patch('requests.get', return_value=history(deposit(self.payment.reference, 150000))):
            self.client.get(self.callback)
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, 'failed')
        self.assertFalse(Enrollment.objects.exists())

    def test_zainpay_unreachable_leaves_pending(self):
        with mock.patch('requests.get', side_effect=requests.Timeout()):
            resp = self.client.get(self.callback)
        self.assertEqual(resp.status_code, 200)
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, 'pending')

    def test_callback_accepts_server_to_server_post(self):
        with mock.patch('requests.get', return_value=history(deposit(self.payment.reference, 1528000))):
            resp = self.client.post(self.callback)
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Enrollment.objects.exists())

    @override_settings(ZAINPAY_ACCOUNT_NUMBER='')
    def test_account_number_looked_up_from_zainbox_when_not_set(self):
        zainpay.zainbox_account_number.__dict__.pop('_cached', None)
        accounts = http_response({'code': '00', 'data': [{'bankAccount': '9096059840', 'name': 'Internal Settlement Account'}]})
        with mock.patch('requests.get', side_effect=[accounts, history(deposit(self.payment.reference, 1528000))]) as get:
            self.client.get(self.callback)
        zainpay.zainbox_account_number.__dict__.pop('_cached', None)
        self.assertEqual(get.call_args_list[0].args[0], 'https://sandbox.zainpay.ng/zainbox/virtual-accounts/box123')
        self.assertTrue(get.call_args_list[1].args[0].endswith('/virtual-account/wallet/transactions/9096059840'))
        self.assertTrue(Enrollment.objects.exists())


@override_settings(**ZAINPAY_ON)
class WebhookTests(TestCase):
    def setUp(self):
        self.course, _, _ = make_course(price=15000)
        self.user = User.objects.create_user('u', email='u@example.com', password='pw')
        self.payment = Payment.objects.create(user=self.user, course=self.course, course_price=15000, amount=15280)
        self.url = reverse('payments:webhook')

    def post(self, body, sign=True, signature=None):
        raw = json.dumps(body).encode()
        headers = {}
        if sign:
            with override_settings(ZAINPAY_SECRET_KEY='sk_test'):
                headers['HTTP_ZAINPAY_SIGNATURE'] = signature or zainpay.compute_webhook_signature(raw)
        return self.client.post(self.url, raw, content_type='application/json', **headers)

    def event(self, ref=None, kobo='1500000', zainbox='box123', event='deposit.success'):
        return {'event': event, 'data': {'txnRef': ref or self.payment.reference, 'depositedAmount': kobo,
                                         'zainboxCode': zainbox}}

    def test_signed_deposit_enrolls_once(self):
        with self.captureOnCommitCallbacks(execute=True):
            self.assertEqual(self.post(self.event()).json(), {'status': 'success'})
            self.assertEqual(self.post(self.event()).json(), {'status': 'already_processed'})
        self.assertEqual(Enrollment.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)

    def test_unsigned_or_forged_webhook_rejected(self):
        self.assertEqual(self.post(self.event(), sign=False).status_code, 401)
        self.assertEqual(self.post(self.event(), signature='deadbeef').status_code, 401)
        self.assertFalse(Enrollment.objects.exists())

    def test_other_zainbox_or_event_ignored(self):
        self.assertEqual(self.post(self.event(zainbox='someone-else')).json(), {'status': 'ignored'})
        self.assertEqual(self.post(self.event(event='transfer.success')).json(), {'status': 'ignored'})
        self.assertFalse(Enrollment.objects.exists())

    def test_underpaid_webhook_fails_payment(self):
        self.post(self.event(kobo='100'))
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, 'failed')
        self.assertFalse(Enrollment.objects.exists())

    def test_unknown_reference_ignored(self):
        self.assertEqual(self.post(self.event(ref='NOPE')).json(), {'status': 'ignored'})


class FeeTests(TestCase):
    def test_gross_up_leaves_full_course_price_after_zainpay_cut(self):
        for price in (500, 1000, 5000, 15000, 49999, 250000):
            total = total_with_zainpay_charge(price)
            zainpay_cut = total * 0.015 + 50
            self.assertGreaterEqual(total - zainpay_cut, price, price)
            self.assertLess(total - zainpay_cut, price + 1, price)  # rounded up by under ₦1
            self.assertEqual(processing_fee(price), total - price)

    def test_known_values_and_free(self):
        self.assertEqual(total_with_zainpay_charge(15000), 15280)
        self.assertEqual(processing_fee(15000), 280)
        self.assertEqual(total_with_zainpay_charge(0), 0)
        self.assertEqual(processing_fee(0), 0)
