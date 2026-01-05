from django import forms

from .models import KeyCloakPermissionMapping


class KeyCloakPermissionMappingForm(forms.ModelForm):
    class Meta:
        model = KeyCloakPermissionMapping
        fields = (
            "keycloak_role_name",
            "keycloak_group_name",
            "groups",
            "permissions",
        )

    def clean(self):
        cleaned_data = super().clean()
        keycloak_group_name = cleaned_data.get("keycloak_group_name")
        keycloak_role_name = cleaned_data.get("keycloak_role_name")
        if not keycloak_group_name and not keycloak_role_name:
            raise forms.ValidationError(
                "Either Keycloak Group Name or Keycloak Role Name must be set."
            )

        groups = cleaned_data.get("groups")
        permissions = cleaned_data.get("permissions")
        if not groups and not permissions:
            raise forms.ValidationError(
                "At least one Django Group or Permission must be assigned."
            )

        return cleaned_data
