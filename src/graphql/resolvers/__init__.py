from ariadne import ObjectType

from src.graphql.resolvers.mutation import mutation
from src.graphql.resolvers.query import query
from src.graphql.resolvers.report import (
    report_event_type,
    report_history_type,
    report_type,
    study_template_type,
    study_type,
)
from src.graphql.resolvers.user import (
    organization_member_type,
    organization_type,
    user_type,
)
from src.graphql.types.enums import report_status_enum

# Pagination types
page_info_type = ObjectType("PageInfo")
user_connection_type = ObjectType("UserConnection")
user_edge_type = ObjectType("UserEdge")
organization_connection_type = ObjectType("OrganizationConnection")
organization_edge_type = ObjectType("OrganizationEdge")
organization_member_connection_type = ObjectType("OrganizationMemberConnection")
organization_member_edge_type = ObjectType("OrganizationMemberEdge")
study_connection_type = ObjectType("StudyConnection")
study_edge_type = ObjectType("StudyEdge")
report_connection_type = ObjectType("ReportConnection")
report_edge_type = ObjectType("ReportEdge")
auth_payload_type = ObjectType("AuthPayload")
user_role_enum = ObjectType("UserRole")


# PageInfo resolvers for snake_case to camelCase mapping
@page_info_type.field("hasNextPage")
def resolve_page_info_has_next_page(page_info, *_):
    return page_info.has_next_page


@page_info_type.field("hasPreviousPage")
def resolve_page_info_has_previous_page(page_info, *_):
    return page_info.has_previous_page


@page_info_type.field("startCursor")
def resolve_page_info_start_cursor(page_info, *_):
    return page_info.start_cursor


@page_info_type.field("endCursor")
def resolve_page_info_end_cursor(page_info, *_):
    return page_info.end_cursor


# Connection resolvers
@user_connection_type.field("edges")
def resolve_user_connection_edges(connection, *_):
    return connection.edges


@user_connection_type.field("pageInfo")
def resolve_user_connection_page_info(connection, *_):
    return connection.page_info


@user_connection_type.field("totalCount")
def resolve_user_connection_total_count(connection, *_):
    return connection.total_count


# Organization connection resolvers
@organization_connection_type.field("edges")
def resolve_organization_connection_edges(connection, *_):
    return connection.edges


@organization_connection_type.field("pageInfo")
def resolve_organization_connection_page_info(connection, *_):
    return connection.page_info


@organization_connection_type.field("totalCount")
def resolve_organization_connection_total_count(connection, *_):
    return connection.total_count


# Study connection resolvers
@study_connection_type.field("edges")
def resolve_study_connection_edges(connection, *_):
    return connection.edges


@study_connection_type.field("pageInfo")
def resolve_study_connection_page_info(connection, *_):
    return connection.page_info


@study_connection_type.field("totalCount")
def resolve_study_connection_total_count(connection, *_):
    return connection.total_count


# Report connection resolvers
@report_connection_type.field("edges")
def resolve_report_connection_edges(connection, *_):
    return connection.edges


@report_connection_type.field("pageInfo")
def resolve_report_connection_page_info(connection, *_):
    return connection.page_info


@report_connection_type.field("totalCount")
def resolve_report_connection_total_count(connection, *_):
    return connection.total_count


# Edge resolvers
@user_edge_type.field("cursor")
def resolve_user_edge_cursor(edge, *_):
    return edge.cursor


@user_edge_type.field("node")
def resolve_user_edge_node(edge, *_):
    return edge.node


@organization_edge_type.field("cursor")
def resolve_organization_edge_cursor(edge, *_):
    return edge.cursor


@organization_edge_type.field("node")
def resolve_organization_edge_node(edge, *_):
    return edge.node


@study_edge_type.field("cursor")
def resolve_study_edge_cursor(edge, *_):
    return edge.cursor


@study_edge_type.field("node")
def resolve_study_edge_node(edge, *_):
    return edge.node


@report_edge_type.field("cursor")
def resolve_report_edge_cursor(edge, *_):
    return edge.cursor


@report_edge_type.field("node")
def resolve_report_edge_node(edge, *_):
    return edge.node


# AuthPayload resolvers
@auth_payload_type.field("mustChangePassword")
def resolve_auth_payload_must_change_password(auth_payload, *_):
    return auth_payload["must_change_password"]


resolvers = [
    query,
    mutation,
    user_type,
    report_type,
    study_type,
    study_template_type,
    report_history_type,
    report_event_type,
    organization_type,
    organization_member_type,
    auth_payload_type,
    report_status_enum,
    page_info_type,
    user_connection_type,
    user_edge_type,
    organization_connection_type,
    organization_edge_type,
    organization_member_connection_type,
    organization_member_edge_type,
    study_connection_type,
    study_edge_type,
    report_connection_type,
    report_edge_type,
]
