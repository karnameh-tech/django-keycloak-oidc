from django.contrib import admin

from .forms import KeyCloakPermissionMappingForm
from .models import KeyCloakPermissionMapping


@admin.register(KeyCloakPermissionMapping)
class KeyCloakPermissionMappingAdmin(admin.ModelAdmin):
    list_display = ("id", "keycloak_role_name", "keycloak_group_name", "django_groups")
    search_fields = ("keycloak_role_name", "keycloak_group_name", "groups__name")
    list_filter = ("groups",)

    form = KeyCloakPermissionMappingForm

    def django_groups(self, obj):
        return ", ".join([group.name for group in obj.groups.all()])
