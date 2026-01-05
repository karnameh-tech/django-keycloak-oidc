from django.contrib import admin

from .forms import KeyCloakPermissionMappingForm
from .models import KeyCloakPermissionMapping


@admin.register(KeyCloakPermissionMapping)
class KeyCloakPermissionMappingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "keycloak_role_name",
        "keycloak_group_name",
        "django_groups",
        "django_permissions",
        "is_active",
    )
    search_fields = (
        "keycloak_role_name",
        "keycloak_group_name",
        "groups__name",
        "permissions__codename",
    )
    list_filter = ("groups", "keycloak_role_name", "keycloak_group_name", "is_active")

    form = KeyCloakPermissionMappingForm

    def django_groups(self, obj):
        return ", ".join([group.name for group in obj.groups.all()])

    def django_permissions(self, obj):
        return ", ".join([perm.codename for perm in obj.permissions.all()])
