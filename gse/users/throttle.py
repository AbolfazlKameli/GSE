from rest_framework.throttling import AnonRateThrottle


class FiveRequestPerHourThrottle(AnonRateThrottle):
    rate = '5/hour'


class OneRequestPerHourThrottle(AnonRateThrottle):
    rate = '1/hour'
