from django.http import Http404, JsonResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


def handle_404(exc, context):
    response = exception_handler(exc, context)
    if response is not None and isinstance(exc, Http404):
        return Response(
            data={'data': {'errors': 'منبع مورد نظر پیدا نشد.'}},
            status=status.HTTP_404_NOT_FOUND
        )
    return response


def custom_page_not_found(request, exception):
    return JsonResponse(
        data={'data': {'errors': 'منبع مورد نظر پیدا نشد.'}},
    )
