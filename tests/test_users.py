import pytest

from src.db.models.user import Organization, User
from tests.factories import OrganizationFactory, UserFactory


@pytest.mark.asyncio
async def test_query_users_paginated(test_client, db_session):
    org = OrganizationFactory(name="Test Org")
    await db_session.commit()
    await db_session.refresh(org)

    # Create multiple users for pagination testing
    users = []
    for i in range(3):
        user = UserFactory(
            first_name=f"John{i}",
            last_name=f"Doe{i}",
            email=f"john{i}@example.com",
            organization=org,
        )
        users.append(user)

    await db_session.commit()
    for user in users:
        await db_session.refresh(user)

    query = """
    query($first: Int) {
        users(first: $first) {
            edges {
                cursor
                node {
                    id
                    firstName
                    lastName
                    email
                    organization {
                        name
                    }
                }
            }
            pageInfo {
                hasNextPage
                hasPreviousPage
                startCursor
                endCursor
            }
            totalCount
        }
    }
    """

    response = await test_client.post(
        "/graphql/", json={"query": query, "variables": {"first": 2}}
    )
    print(f"Response status: {response.status_code}")
    print(f"Response headers: {response.headers}")
    print(f"Response text: {response.text}")
    assert response.status_code == 200

    data = response.json()
    assert "data" in data
    assert "users" in data["data"]

    users_data = data["data"]["users"]
    assert len(users_data["edges"]) == 2
    assert users_data["totalCount"] == 3
    assert users_data["pageInfo"]["hasNextPage"] == True
    assert users_data["pageInfo"]["hasPreviousPage"] == False
    assert users_data["pageInfo"]["startCursor"] is not None
    assert users_data["pageInfo"]["endCursor"] is not None

    # Test first user
    first_user = users_data["edges"][0]["node"]
    assert first_user["firstName"] == "John0"
    assert first_user["lastName"] == "Doe0"
    assert first_user["email"] == "john0@example.com"
    assert first_user["organization"]["name"] == "Test Org"


@pytest.mark.asyncio
async def test_query_users_pagination_after(test_client, db_session):
    org = OrganizationFactory(name="Test Org")
    await db_session.commit()
    await db_session.refresh(org)

    # Create multiple users
    for i in range(5):
        UserFactory(
            first_name=f"User{i}",
            last_name=f"Test{i}",
            email=f"user{i}@example.com",
            organization=org,
        )

    await db_session.commit()

    # First, get the first page
    first_query = """
    query {
        users(first: 2) {
            edges {
                cursor
                node { id firstName }
            }
            pageInfo {
                hasNextPage
                endCursor
            }
        }
    }
    """

    first_response = await test_client.post("/graphql/", json={"query": first_query})
    assert first_response.status_code == 200

    first_data = first_response.json()["data"]["users"]
    end_cursor = first_data["pageInfo"]["endCursor"]

    # Then get the next page using the cursor
    next_query = """
    query($after: String) {
        users(first: 2, after: $after) {
            edges {
                node { id firstName }
            }
            pageInfo {
                hasNextPage
                hasPreviousPage
            }
        }
    }
    """

    next_response = await test_client.post(
        "/graphql/", json={"query": next_query, "variables": {"after": end_cursor}}
    )
    assert next_response.status_code == 200

    next_data = next_response.json()["data"]["users"]
    assert len(next_data["edges"]) == 2
    assert next_data["pageInfo"]["hasPreviousPage"] == True


@pytest.mark.asyncio
async def test_query_organizations_paginated(test_client, db_session):
    # Create multiple organizations
    orgs = []
    for i in range(3):
        org = OrganizationFactory(name=f"Organization {i}")
        orgs.append(org)

    await db_session.commit()

    query = """
    query {
        organizations(first: 2) {
            edges {
                node {
                    id
                    name
                }
            }
            pageInfo {
                hasNextPage
                hasPreviousPage
            }
            totalCount
        }
    }
    """

    response = await test_client.post("/graphql/", json={"query": query})
    assert response.status_code == 200

    data = response.json()
    orgs_data = data["data"]["organizations"]

    assert len(orgs_data["edges"]) == 2
    assert orgs_data["totalCount"] == 3
    assert orgs_data["pageInfo"]["hasNextPage"] == True
    assert orgs_data["pageInfo"]["hasPreviousPage"] == False
