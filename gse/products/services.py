from django.utils.text import slugify


def slugify_title(title: str) -> str:
    return slugify(title, allow_unicode=True)
