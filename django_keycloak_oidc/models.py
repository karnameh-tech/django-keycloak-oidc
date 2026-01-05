from django.contrib.auth.models import Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _


class KeyCloakPermissionMapping(models.Model):
    keycloak_group_name = models.CharField(
        max_length=255,
        verbose_name=_("Keycloak Group Name"),
        null=True,
        blank=True,
    )
    keycloak_role_name = models.CharField(
        max_length=255,
        verbose_name=_("Keycloak Role Name"),
        null=True,
        blank=True,
    )
    groups = models.ManyToManyField(
        Group,
        related_name="keycloak_mappings",
        verbose_name=_("Django Groups"),
        null=True,
        blank=True,
    )
    permissions = models.ManyToManyField(
        Permission,
        related_name="keycloak_mappings",
        verbose_name=_("Django Permissions"),
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Is Active"),
        help_text=_("Designates whether this mapping is active."),
    )
