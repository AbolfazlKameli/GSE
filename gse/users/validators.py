import re

from django.core.exceptions import ValidationError


def validate_iranian_phone_number(value):
    pattern = '^(\\+98|0)?9\\d{9}$'

    if not re.match(pattern, value):
        raise ValidationError('یک شماره معتبر ایرانی وارد کنید.')
