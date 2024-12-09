from .models import Website


def get_all_attributes() -> list[Website]:
    return Website.objects.all()
