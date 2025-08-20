from typing import Any, Dict

from ariadne import SchemaDirectiveVisitor

from graphql import GraphQLField, GraphQLResolveInfo
from src.api.auth_context import (
    AuthenticationError,
    PasswordChangeRequiredError,
    get_current_user,
)
from src.db.models.user import UserRole
from src.services.permission_service import PermissionService


def _default_resolver(obj, info, **args):
    return getattr(obj, info.field_name)


class AuthDirective(SchemaDirectiveVisitor):
    """Legacy auth directive - kept for compatibility"""

    def visit_field_definition(self, field: GraphQLField, object_type):
        original_resolver = field.resolve or _default_resolver

        def auth_resolver(obj, info, **args):
            return original_resolver(obj, info, **args)

        field.resolve = auth_resolver
        return field


class RequiresAuthDirective(SchemaDirectiveVisitor):
    """Directive that requires user to be authenticated"""

    def visit_field_definition(self, field, object_type):
        original_resolver = field.resolve or _default_resolver

        async def auth_required_resolver(obj, info: GraphQLResolveInfo, **kwargs):
            user = get_current_user()
            if not user:
                raise AuthenticationError("Authentication required")

            # Check if password change is required
            if user.password_must_change:
                # Only allow changePassword mutation
                operation_name = info.field_name
                if operation_name != "changePassword":
                    raise PasswordChangeRequiredError(
                        "Password must be changed before accessing other operations"
                    )

            return await original_resolver(obj, info, **kwargs)

        field.resolve = auth_required_resolver
        return field


class RequiresRoleDirective(SchemaDirectiveVisitor):
    """Directive that requires user to have a specific role"""

    def visit_field_definition(self, field, object_type):
        original_resolver = field.resolve or _default_resolver
        required_role = self.args.get("role")

        async def role_required_resolver(obj, info: GraphQLResolveInfo, **kwargs):
            user = get_current_user()
            if not user:
                raise AuthenticationError("Authentication required")

            # Check if password change is required first
            if user.password_must_change and info.field_name != "changePassword":
                raise PasswordChangeRequiredError(
                    "Password must be changed before accessing other operations"
                )

            # Get organization ID from arguments or context
            organization_id = kwargs.get("organizationId") or kwargs.get("id")

            # required_role now matches Python enum values directly
            python_role = required_role

            if not organization_id:
                # If no organization context, check if user has the role anywhere
                permission_service = PermissionService()
                has_role = await permission_service.user_has_role_anywhere(
                    user.id, UserRole(python_role)
                )
                if not has_role:
                    raise AuthenticationError(
                        f"Insufficient permissions. Role {required_role} required."
                    )
            else:
                # Check role in specific organization
                permission_service = PermissionService()
                has_role = await permission_service.check_user_role_in_organization(
                    user.id, int(organization_id), UserRole(python_role)
                )
                if not has_role:
                    raise AuthenticationError(
                        f"Insufficient permissions. Role {required_role} required in this organization."
                    )

            return await original_resolver(obj, info, **kwargs)

        field.resolve = role_required_resolver
        return field
