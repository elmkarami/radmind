import base64
import json
from dataclasses import dataclass
from typing import Generic, List, Optional, TypeVar

from sqlalchemy import asc, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import db

T = TypeVar("T")


@dataclass
class PageInfo:
    has_next_page: bool
    has_previous_page: bool
    start_cursor: Optional[str]
    end_cursor: Optional[str]


@dataclass
class Edge(Generic[T]):
    cursor: str
    node: T


@dataclass
class Connection(Generic[T]):
    edges: List[Edge[T]]
    page_info: PageInfo
    total_count: int


def encode_cursor(value: int) -> str:
    """Encode cursor value to base64 string"""
    return base64.b64encode(json.dumps({"id": value}).encode()).decode()


def decode_cursor(cursor: str) -> int:
    """Decode base64 cursor to get ID value"""
    try:
        decoded = base64.b64decode(cursor.encode()).decode()
        return json.loads(decoded)["id"]
    except:
        raise ValueError("Invalid cursor")


async def paginate(
    model,
    first: Optional[int] = None,
    after: Optional[str] = None,
    last: Optional[int] = None,
    before: Optional[str] = None,
    order_by_field: str = "id",
    filters: Optional[List] = None,
) -> Connection[T]:
    """
    Generic cursor pagination function
    """
    # Validate arguments
    if first is not None and last is not None:
        raise ValueError("Cannot provide both first and last")

    if first is not None and first <= 0:
        raise ValueError("first must be positive")

    if last is not None and last <= 0:
        raise ValueError("last must be positive")

    # Build base query
    query = select(model)

    # Apply custom filters
    if filters:
        for filter_condition in filters:
            query = query.where(filter_condition)

    # Handle cursor filtering
    if after:
        after_id = decode_cursor(after)
        query = query.where(getattr(model, order_by_field) > after_id)

    if before:
        before_id = decode_cursor(before)
        query = query.where(getattr(model, order_by_field) < before_id)

    # Determine ordering and limit
    if last is not None:
        # For last N, we need reverse order
        query = query.order_by(desc(getattr(model, order_by_field)))
        limit = last + 1  # +1 to check if there are more
    else:
        # Default or first N
        query = query.order_by(asc(getattr(model, order_by_field)))
        limit = (first or 20) + 1  # Default to 20, +1 to check if there are more

    query = query.limit(limit)

    # Execute query
    result = await db.session.execute(query)
    items = list(result.scalars().all())

    # Handle last N case - reverse the results back to correct order
    if last is not None:
        items.reverse()

    # Check for more pages
    has_more = len(items) > (last or first or 20)
    if has_more:
        items = items[:-1]  # Remove the extra item

    # Get total count (separate query for performance)
    count_query = select(func.count(getattr(model, order_by_field)))

    # Apply the same filters to the count query (but not cursor filters)
    if filters:
        for filter_condition in filters:
            count_query = count_query.where(filter_condition)

    # Note: totalCount represents the total number of items matching the filters
    # regardless of cursor filtering - this follows GraphQL best practices

    total_result = await db.session.execute(count_query)
    total_count = total_result.scalar()

    # Create edges
    edges = [
        Edge(cursor=encode_cursor(getattr(item, order_by_field)), node=item)
        for item in items
    ]

    # Create page info
    start_cursor = edges[0].cursor if edges else None
    end_cursor = edges[-1].cursor if edges else None

    if last is not None:
        has_next_page = bool(before and has_more)
        has_previous_page = bool(after or (not before and has_more))
    else:
        has_next_page = has_more
        has_previous_page = bool(after)

    page_info = PageInfo(
        has_next_page=has_next_page,
        has_previous_page=has_previous_page,
        start_cursor=start_cursor,
        end_cursor=end_cursor,
    )

    return Connection(edges=edges, page_info=page_info, total_count=total_count)
