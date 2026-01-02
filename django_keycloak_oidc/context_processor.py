from django.conf import settings


def _get_value(key, default=None):
    return getattr(settings, key, default)


def settings_context(request):
    return {
        "KEYCLOAK_DJANGO_ADMIN_LOGIN_VISIBLE": _get_value(
            "KEYCLOAK_DJANGO_ADMIN_LOGIN_VISIBLE", default=True
        ),
        "KEYCLOAK_DJANGO_ADMIN_LOGIN_DIRECTION": _get_value(
            "KEYCLOAK_DJANGO_ADMIN_LOGIN_DIRECTION", default="ltr"
        ),
        "KEYCLOAK_DJANGO_ADMIN_LOGIN_TEXT": _get_value(
            "KEYCLOAK_DJANGO_ADMIN_LOGIN_TEXT", default="Login with"
        ),
        "KEYCLOAK_DJANGO_ADMIN_LOGIN_LOGO": _get_value(
            "KEYCLOAK_DJANGO_ADMIN_LOGIN_LOGO",
            default="https://karnameh.com/assets/logos/karnameh-logo.svg",
        ),
    }
