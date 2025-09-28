from django.db import transaction
from django.utils import timezone
from .models import Order

def _generate_order_ref():
    """
    Format: FOODLY-YYYYMMDD-XXXX  (XXXX = zero-padded sequence for that date)
    """
    today = timezone.localtime(timezone.now()).date()
    date_str = today.strftime('%Y%m%d')
    prefix = f"FOODLY-{date_str}"

    # count how many orders already exist today (fast enough for small scale)
    base_count = Order.objects.filter(ordered_at__date=today).count()
    # Start sequence at base_count + 1 and ensure uniqueness in a loop to be safe
    seq = base_count + 1
    while True:
        ref = f"{prefix}-{seq:04d}"
        if not Order.objects.filter(order_ref=ref).exists():
            return ref
        seq += 1
