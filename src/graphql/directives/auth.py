from ariadne import SchemaDirectiveVisitor

from graphql import GraphQLField


def _default_resolver(obj, info, **args):
    return getattr(obj, info.field_name)


class AuthDirective(SchemaDirectiveVisitor):
    def visit_field_definition(self, field: GraphQLField, object_type):
        original_resolver = field.resolve or _default_resolver

        def auth_resolver(obj, info, **args):
            return original_resolver(obj, info, **args)

        field.resolve = auth_resolver
        return field
