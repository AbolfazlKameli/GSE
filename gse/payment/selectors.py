from .models import Payment


def get_payment_by_id(payment_id: int) -> Payment | None:
    return Payment.objects.filter(id=payment_id).first()


def get_all_payments() -> list[Payment]:
    return Payment.objects.all()
