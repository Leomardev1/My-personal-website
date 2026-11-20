from django.conf import settings


def site(request):
    """Põe o nome, o endereço público e o URL canónico da página em todos os templates."""
    return {
        'SITE_NAME': settings.SITE_NAME,
        'SITE_URL': settings.SITE_URL,
        'URL_CANONICA': settings.SITE_URL + request.path,
    }
