from decouple import config

DEBUG = config('DJANGO_DEBUG', default=False, cast=bool)

MERCHANT = config('ZP_MERCHANT', default='00000000-0000-0000-0000-000000000000')
if DEBUG:
    sandbox = 'sandbox'
    api = 'sandbox'
else:
    sandbox = 'www'
    api = 'api'

ZP_API_REQUEST = f"https://{api}.zarinpal.com/pg/v4/payment/request.json"
ZP_API_VERIFY = f"https://{api}.zarinpal.com/pg/v4/payment/verify.json"
ZP_API_STARTPAY = f"https://{sandbox}.zarinpal.com/pg/StartPay/"
DESCRIPTION = "آسانسور گستران شرق"
CALLBACK_URL = config('ZP_CALLBACK')
