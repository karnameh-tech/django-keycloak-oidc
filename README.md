# django-keyclock-oidc

This project depends on [mozilla-django-oidc](https://github.com/mozilla/mozilla-django-oidc/) and map keycloak roles and groups to django user permissions and groups.

## Features
- Automatic mapping of Keycloak roles and groups to Django user permissions and groups
- Django admin login integration with Keycloak
- OIDC authentication with Keycloak

## Installation

1. You can install the package via your python package manager, example:

```bash
pip install mozilla-django-oidc
pip install django-keycloak-oidc
# or
poetry add mozilla-django-oidc
poetry add django-keycloak-oidc
# or
uv add mozilla-django-oidc
uv add django-keycloak-oidc
```

2. Add `django_keycloak_oidc` and `mozilla_django_oidc` to your `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    "django_keycloak_oidc",  # top of admin app
    "django.contrib.admin",
    "django.contrib.auth",
    "mozilla_django_oidc",  # bottom of auth app
    ...
]
```

3. Add the authentication backend to your `AUTHENTICATION_BACKENDS` in `settings.py`:

```python
AUTHENTICATION_BACKENDS = [
    "django_keycloak_oidc.auth.KeyCloakAuthenticationBackend",  # here
    "django.contrib.auth.backends.ModelBackend",  # django default (need it too)
    ...,  # and other
]
```

4. Add `mozilla_django_oidc` urls to your `urls.py`:

```python
urlpatterns = [
    ...,
    path("oidc/", include("mozilla_django_oidc.urls")),
    ...,
]
```
**Important Note:** If you changed your admin root path, make sure that the `oidc/` and `admin/` paths are in same root.

for example:

```python
urlpatterns = [
    ...,
    path(
        "root/",  # your root (if you did it)
        include(
            [
                ...,
                path("admin/", admin.site.urls),
                path("oidc/", include("mozilla_django_oidc.urls")),
                ...,
            ]
        )
    ),
    ...,
]
```

5. Add the settings_context to your context_processors in `settings.py`:

```python
TEMPLATES = [
    {
        ...,
        "OPTIONS": {
            "context_processors": [
                ...,
                "django_keycloak_oidc.context_processor.settings_context",  # here
            ],
        },
    },
]
```

6. Run migrations (Done):

```bash
python manage.py migrate
```

## Configuration
You can see configuration of the original project [here](https://mozilla-django-oidc.readthedocs.io/en/latest/).

1. Keycloak setup:
    - You need to add `Group Membership` and `User Realm Role` from Client scopes -> profile -> Mappers -> Add mapper -> By configuration:
        - User Realm Role:
            - Mapper Type: `User Realm Role`
            - Name: `roles`
            - Token Claim Name: `roles`
          - Add to ID token, Add to access token, Add to userinfo, Add to token introspection: `on`
        - Group Membership:
            - Mapper Type: `Group Membership`
            - Name: `groups`
            - Token Claim Name: `groups`
            - Full group path: `off` . if its on, you must enter group name in django admin with full path.
            - Add to ID token, Add to access token, Add to userinfo, Add to token introspection: `on`
    - And create you `roles` and `groups` in your Keycloak console.

2. My Django sample configuration(`settings.py`) is as below:

```python
OIDC_RP_CLIENT_ID = "<client-id>"
OIDC_RP_CLIENT_SECRET = "<client-secret>"
OIDC_RP_SIGN_ALGO = "RS256"

OIDC_VERIFY_SSL = False

OIDC_OP_AUTHORIZATION_ENDPOINT = "http://<keycloak-host>/realms/<realm>/protocol/openid-connect/auth"
OIDC_OP_TOKEN_ENDPOINT = "http://<keycloak-host>/realms/<realm>/protocol/openid-connect/token"
OIDC_OP_USER_ENDPOINT = "http://<keycloak-host>/realms/<realm>/protocol/openid-connect/userinfo"
OIDC_OP_JWKS_ENDPOINT = "http://<keycloak-host>/realms/<realm>/protocol/openid-connect/certs"

LOGIN_URL = "/oidc/authenticate/"
LOGIN_REDIRECT_URL = "/leasing/admin/"
LOGIN_REDIRECT_URL_FAILURE = "/leasing/admin/"
LOGOUT_REDIRECT_URL = "/leasing/admin/login/"

# (django-keycloak-oidc) settings for customizing the login button in django admin login page(make sure you did step 5 in installation):
KEYCLOAK_DJANGO_ADMIN_LOGIN_VISIBLE = True
KEYCLOAK_DJANGO_ADMIN_LOGIN_DIRECTION = "rtl"
KEYCLOAK_DJANGO_ADMIN_LOGIN_TEXT = "Login with"
KEYCLOAK_DJANGO_ADMIN_LOGIN_LOGO = "https://karnameh.com/assets/logos/karnameh-logo.svg"
```

3. Go to your Django admin and start mapping:

![mapping](https://raw.githubusercontent.com/karnameh-tech/django-keycloak-oidc/refs/heads/main/assets/mapping.png)
