"""
Zainpay client — mirrors the production-tested integration in the GIIA project
(wallet/services/zainpay_service.py), including its hard-won quirks:

- Auth is the PUBLIC key as a Bearer token; the SECRET key is only used to verify
  webhook signatures.
- Checkout `amount` is in NAIRA as a plain string ("15000"); a JSON number or a
  decimal suffix is rejected.
- Amounts Zainpay reports back (transaction history, webhooks) are in KOBO.
- There's no reliable verify-by-reference for checkout payments, so a payment is
  confirmed by finding its txnRef in the Zainbox account's transaction history.
- Uses `requests`: Zainpay's live API sits behind Cloudflare, which rejects
  Python's default urllib client outright (error 1010).
"""
import hashlib
import hmac
import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

TIMEOUT = 30


class ZainpayError(Exception):
    pass


def is_configured():
    return bool(settings.ZAINPAY_PUBLIC_KEY and settings.ZAINPAY_ZAINBOX_CODE)


def _url(path):
    return f"{settings.ZAINPAY_BASE_URL.rstrip('/')}/{path}"


def _headers():
    return {
        'Authorization': f'Bearer {settings.ZAINPAY_PUBLIC_KEY}',
        'Content-Type': 'application/json',
    }


def _get(path):
    """GET returning the parsed body when code == "00", else None (never raises)."""
    try:
        response = requests.get(_url(path), headers=_headers(), timeout=TIMEOUT)
        result = response.json()
    except (requests.RequestException, ValueError) as exc:
        logger.warning('Zainpay GET %s failed: %s', path, exc)
        return None
    if result.get('code') != '00':
        logger.info('Zainpay GET %s returned %s', path, result)
        return None
    return result


def initialize_checkout(*, email, mobile_number, amount, txn_ref, callback_url):
    """Start a hosted checkout (bank transfer only) into our Zainbox; returns the redirect URL."""
    payload = {
        'amount': str(int(amount)),  # whole naira — Zainpay rejects any decimal amount
        'txnRef': txn_ref,
        'mobileNumber': mobile_number,
        'zainboxCode': settings.ZAINPAY_ZAINBOX_CODE,
        'emailAddress': email,
        'callBackUrl': callback_url,
        'paymentChannels': ['bank_transfer'],
    }
    logger.info('Zainpay checkout initialize request (ref %s): %s', txn_ref, payload)
    try:
        response = requests.post(_url('zainbox/card/initialize/payment'), headers=_headers(),
                                 json=payload, timeout=TIMEOUT)
    except requests.RequestException as exc:
        logger.warning('Zainpay checkout initialize (ref %s) could not reach Zainpay: %s', txn_ref, exc)
        raise ZainpayError(f'Could not reach Zainpay: {exc}') from exc
    try:
        result = response.json()
    except ValueError as exc:
        logger.warning('Zainpay checkout initialize (ref %s) returned non-JSON: status=%s body=%r',
                       txn_ref, response.status_code, response.text[:500])
        raise ZainpayError(f'Zainpay returned an unexpected response (status {response.status_code}).') from exc

    logger.info('Zainpay checkout initialize response (ref %s): status=%s body=%s',
                txn_ref, response.status_code, result)
    if result.get('code') != '00' or not result.get('data'):
        raise ZainpayError(result.get('description') or 'Could not start Zainpay checkout.')
    return result['data']


def compute_webhook_signature(raw_body):
    """HMAC-SHA256 of the raw body with the secret key (the "Zainpay-Signature" header)."""
    return hmac.new(settings.ZAINPAY_SECRET_KEY.encode('utf-8'), raw_body, hashlib.sha256).hexdigest()


def verify_webhook_signature(raw_body, received_signature):
    if not received_signature or not settings.ZAINPAY_SECRET_KEY:
        return False
    return hmac.compare_digest(compute_webhook_signature(raw_body), received_signature)


def zainbox_account_number():
    """
    The Zainbox's settlement account, whose history we search to confirm payments.
    Taken from ZAINPAY_ACCOUNT_NUMBER if set, otherwise looked up from Zainpay once
    per process (the Zainbox's "Internal Settlement Account").
    """
    if settings.ZAINPAY_ACCOUNT_NUMBER:
        return settings.ZAINPAY_ACCOUNT_NUMBER
    cached = getattr(zainbox_account_number, '_cached', None)
    if cached:
        return cached
    result = _get(f'zainbox/virtual-accounts/{settings.ZAINPAY_ZAINBOX_CODE}')
    accounts = (result or {}).get('data') or []
    number = next((a.get('bankAccount') for a in accounts if a.get('bankAccount')), None)
    if number:
        zainbox_account_number._cached = number
    else:
        logger.error('Could not look up the account number for Zainbox %s — set ZAINPAY_ACCOUNT_NUMBER.',
                     settings.ZAINPAY_ZAINBOX_CODE)
    return number


def find_deposit_kobo(txn_ref):
    """
    Kobo deposited for `txn_ref` according to the Zainbox's own transaction history,
    or None if Zainpay has no such deposit (yet). Same lookup GIIA uses on callback.
    """
    account = zainbox_account_number()
    if not account:
        return None
    result = _get(f'virtual-account/wallet/transactions/{account}')
    transactions = (result or {}).get('data') or []
    match = next((t for t in transactions
                  if t.get('transactionRef') == txn_ref and t.get('transactionType') == 'deposit'), None)
    if not match:
        return None
    try:
        return int(float(match.get('amount', 0)))
    except (TypeError, ValueError):
        return None
