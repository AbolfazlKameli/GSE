ORDER_STATUS_SUCCESS = 'success'
ORDER_STATUS_PENDING = 'pending'
ORDER_STATUS_CANCELLED = 'cancelled'

ORDER_STATUS_CHOICES = (
    (ORDER_STATUS_SUCCESS, 'پرداخت شده'),
    (ORDER_STATUS_PENDING, 'درحال پردازش'),
    (ORDER_STATUS_CANCELLED, 'لغو شده'),
)
