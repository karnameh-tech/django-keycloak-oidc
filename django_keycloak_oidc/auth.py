from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from mozilla_django_oidc.auth import OIDCAuthenticationBackend

from .models import KeyCloakPermissionMapping

UserModel = get_user_model()


class KeyCloakAuthenticationBackend(OIDCAuthenticationBackend):
    def user_claims(self, claims: dict) -> dict:
        """
        Extract user information from Keycloak claims to create or update a Django user.
        Args:
            claims (dict): The claims received from Keycloak.
        Returns:
            dict: A dictionary containing user information.
        """
        return {
            "email": claims.get("email", ""),
            "first_name": claims.get("given_name", ""),
            "last_name": claims.get("family_name", ""),
            "username": self.get_username(claims),
        }

    def create_user(self, claims: dict) -> UserModel:
        """
        Create a new Django user based on Keycloak claims.
        Args:
            claims (dict): The claims received from Keycloak.
        Returns:
            UserModel: The created Django user instance.
        """
        user_data = self.user_claims(claims)
        user = self.UserModel.objects.create_user(
            **user_data,
        )
        return user

    def update_user(self, user: UserModel, claims: dict) -> UserModel:
        """
        Update an existing Django user based on Keycloak claims.
        Args:
            user (UserModel): The existing Django user instance.
            claims (dict): The claims received from Keycloak.
        Returns:
            UserModel: The updated Django user instance.
        """
        user_data = self.user_claims(claims)
        for key, value in user_data.items():
            setattr(user, key, value)
        user.save()
        return user

    def get_or_create_user(
        self, access_token: str, id_token: str, payload: dict
    ) -> UserModel:
        """
        Get or create a Django user based on Keycloak tokens and payload.
        Args:
            access_token (str): The access token from Keycloak.
            id_token (str): The ID token from Keycloak.
            payload (dict): The payload received from Keycloak.
        Returns:
            UserModel: The Django user instance.
        """
        user = super().get_or_create_user(access_token, id_token, payload)
        if user:
            self.user_permissions_mapping(
                user=user,
                payload=payload,
            )
        return user

    def user_permissions_mapping(self, user: UserModel, payload: dict) -> None:
        """
        Map Keycloak roles and groups to Django user permissions and groups.
        Args:
            user (UserModel): The Django user instance.
            payload (dict): The payload received from Keycloak.
        Returns:
            None
        """
        user.user_permissions.clear()
        user.groups.clear()

        is_superuser = self.is_superuser(user, payload)
        permissions = self.keycloak_roles_to_permissions_mapping(
            user, payload
        ) + self.keycloak_groups_to_permissions_mapping(user, payload)
        groups = self.keycloak_roles_to_groups_mapping(
            user, payload
        ) + self.keycloak_groups_to_groups_mapping(user, payload)

        self.set_staff(
            user=user,
            value=(is_superuser or permissions != [] or groups != []),
        )

        user.save()

    def is_superuser(self, user: UserModel, payload: dict) -> bool:
        """
        Determine if the user should be a superuser based on Keycloak roles.
        Args:
            user (UserModel): The Django user instance.
            payload (dict): The payload received from Keycloak.
        Returns:
            bool: True if the user is a superuser, False otherwise.
        """
        is_superuser = False
        if self.superuser_role(payload):
            is_superuser = True
        user.is_superuser = is_superuser
        return is_superuser

    def superuser_role(self, payload: dict) -> bool:
        """
        Check if the user has superuser roles in Keycloak.
        Args:
            payload (dict): The payload received from Keycloak.
        Returns:
            bool: True if the user has superuser roles, False otherwise.
        """
        return f"{self.OIDC_RP_CLIENT_ID}#superuser" in payload.get(
            "roles"
        ) or "django#superuser" in payload.get("roles")

    @staticmethod
    def keycloak_roles_to_permissions_mapping(
        user: UserModel, payload: dict
    ) -> list[Permission]:
        """
        Map Keycloak roles to Django user permissions.
        Args:
            user (UserModel): The Django user instance.
            payload (dict): The payload received from Keycloak.
        Returns:
            List[Permission]: A list of Django permissions assigned to the user.
        """
        claim_roles = payload.get("roles", [])
        permissions = []
        for claim_role in claim_roles:
            keycloak_mappings = KeyCloakPermissionMapping.objects.filter(
                keycloak_role_name=claim_role,
            )
            for mapping in keycloak_mappings:
                for perm in mapping.permissions.all():
                    permissions.append(perm)
                    user.user_permissions.add(perm)
        return permissions

    @staticmethod
    def keycloak_roles_to_groups_mapping(user: UserModel, payload: dict) -> list[Group]:
        """
        Map Keycloak roles to Django user groups.
        Args:
            user (UserModel): The Django user instance.
            payload (dict): The payload received from Keycloak.
        Returns:
            List[Group]: A list of Django groups assigned to the user.
        """
        claim_roles = payload.get("roles", [])
        groups = []
        for claim_role in claim_roles:
            keycloak_mappings = KeyCloakPermissionMapping.objects.filter(
                keycloak_role_name=claim_role,
            )
            for mapping in keycloak_mappings:
                for group in mapping.groups.all():
                    groups.append(group)
                    user.groups.add(group)
        return groups

    @staticmethod
    def keycloak_groups_to_groups_mapping(
        user: UserModel, payload: dict
    ) -> list[Group]:
        """
        Map Keycloak groups to Django user groups.
        Args:
            user (UserModel): The Django user instance.
            payload (dict): The payload received from Keycloak.
        Returns:
            List[Group]: A list of Django groups assigned to the user.
        """
        claim_groups = payload.get("groups", [])
        groups = []
        for claim_group in claim_groups:
            keycloak_mappings = KeyCloakPermissionMapping.objects.filter(
                keycloak_group_name=claim_group,
            )
            for mapping in keycloak_mappings:
                for group in mapping.groups.all():
                    groups.append(group)
                    user.groups.add(group)
        return groups

    @staticmethod
    def keycloak_groups_to_permissions_mapping(
        user: UserModel, payload: dict
    ) -> list[Permission]:
        """
        Map Keycloak groups to Django user permissions.
        Args:
            user (UserModel): The Django user instance.
            payload (dict): The payload received from Keycloak.
        Returns:
            List[Permission]: A list of Django permissions assigned to the user.
        """
        claim_groups = payload.get("groups", [])
        permissions = []
        for claim_group in claim_groups:
            keycloak_mappings = KeyCloakPermissionMapping.objects.filter(
                keycloak_group_name=claim_group,
            )
            for mapping in keycloak_mappings:
                for perm in mapping.permissions.all():
                    permissions.append(perm)
                    user.user_permissions.add(perm)
        return permissions

    @staticmethod
    def set_staff(user: UserModel, value: bool = True) -> None:
        """
        Set the is_staff attribute for the user.
        Args:
            user (UserModel): The Django user instance.
            value (bool): The value to set for is_staff.
        Returns:
            None
        """
        user.is_staff = value
