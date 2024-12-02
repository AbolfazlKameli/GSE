from django.http import JsonResponse


def custom_page_not_found(request, exception):
    return JsonResponse(
        data={'data': {'errors': 'منبع مورد نظر پیدا نشد.'}},
    )
