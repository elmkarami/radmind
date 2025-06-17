from ariadne import ObjectType

from .mutation import mutation
from .query import query
from .report import report_type, study_type
from .user import organization_type, user_type

# Pagination types
page_info_type = ObjectType("PageInfo")
user_connection_type = ObjectType("UserConnection")
user_edge_type = ObjectType("UserEdge")
organization_connection_type = ObjectType("OrganizationConnection")
organization_edge_type = ObjectType("OrganizationEdge")
study_connection_type = ObjectType("StudyConnection")
study_edge_type = ObjectType("StudyEdge")
report_connection_type = ObjectType("ReportConnection")
report_edge_type = ObjectType("ReportEdge")

# PageInfo resolvers
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

resolvers = [
    query,
    mutation,
    user_type,
    report_type,
    study_type,
    organization_type,
    page_info_type,
    user_connection_type,
    user_edge_type,
    organization_connection_type,
    organization_edge_type,
    study_connection_type,
    study_edge_type,
    report_connection_type,
    report_edge_type,
]
