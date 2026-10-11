from decimal import ROUND_CEILING, Decimal

# Zainpay's checkout charge: 1.5% + ₦50 per transaction, passed on to the student.
ZAINPAY_FEE_PERCENTAGE = Decimal('0.015')
ZAINPAY_FEE_FLAT = Decimal('50')


def total_with_zainpay_charge(amount):
    """
    Amount to charge so Northpreneur still nets the full course price — same
    formula as GIIA's admissions fee. Zainpay deducts its 1.5% + ₦50 from the
    amount actually paid, so simply adding the charge on top would leave us
    short. Solve G - (G * 1.5% + 50) == amount → G = (amount + 50) / (1 - 1.5%),
    rounded UP to whole naira (Zainpay rejects decimal amounts, and rounding up
    keeps the net at or above the course price).
    """
    amount = Decimal(str(amount))
    if amount <= 0:
        return 0
    gross = (amount + ZAINPAY_FEE_FLAT) / (Decimal('1') - ZAINPAY_FEE_PERCENTAGE)
    return int(gross.quantize(Decimal('1'), rounding=ROUND_CEILING))


def processing_fee(amount):
    return total_with_zainpay_charge(amount) - int(amount) if amount else 0
