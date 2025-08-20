import pytest

from src.db.models.user import UserRole
from tests.factories import OrganizationFactory, OrganizationMemberFactory, UserFactory


@pytest.mark.asyncio
async def test_query_organizations_paginated(test_client, db_session):
    """Test querying organizations with pagination"""
    # Create test organizations
    orgs = []
    for i in range(3):
        org = OrganizationFactory(
            name=f"Test Organization {i}",
            address=f"123 Test St {i}, City, State",
            phone_number=f"+1-555-012{i}",
        )
        orgs.append(org)

    await db_session.commit()

    query = """
    query {
        organizations(first: 2) {
            edges {
                cursor
                node {
                    id
                    name
                    address
                    phoneNumber
                    logo
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

    response = await test_client.post("/graphql/", json={"query": query})
    assert response.status_code == 200

    data = response.json()
    assert "data" in data
    assert "organizations" in data["data"]

    orgs_data = data["data"]["organizations"]
    assert len(orgs_data["edges"]) == 2
    assert orgs_data["totalCount"] == 3
    assert orgs_data["pageInfo"]["hasNextPage"] == True
    assert orgs_data["pageInfo"]["hasPreviousPage"] == False


@pytest.mark.asyncio
async def test_query_single_organization(test_client, db_session):
    """Test querying a single organization by ID"""
    # Create organization with owner and members
    org = OrganizationFactory(
        name="Single Test Clinic",
        address="456 Medical Ave, Healthcare City",
        phone_number="+1-555-0789",
    )
    owner = UserFactory(
        first_name="Dr. Owner", last_name="Smith", email="owner@clinic.com"
    )
    radiologist = UserFactory(
        first_name="Dr. Radiologist",
        last_name="Johnson",
        email="radiologist@clinic.com",
    )

    # Create memberships
    OrganizationMemberFactory(user=owner, organization=org, role=UserRole.OWNER.value)
    OrganizationMemberFactory(
        user=radiologist, organization=org, role=UserRole.RADIOLOGIST.value
    )

    await db_session.commit()
    await db_session.refresh(org)

    query = """
    query($id: ID!) {
        organization(id: $id) {
            id
            name
            address
            phoneNumber
            logo
            createdBy {
                id
                firstName
                lastName
                email
            }
            members {
                id
                user {
                    id
                    firstName
                    lastName
                    email
                }
                role
                createdAt
            }
        }
    }
    """

    response = await test_client.post(
        "/graphql/", json={"query": query, "variables": {"id": str(org.id)}}
    )
    assert response.status_code == 200

    data = response.json()
    assert "data" in data
    assert "organization" in data["data"]

    org_data = data["data"]["organization"]
    assert org_data["id"] == str(org.id)
    assert org_data["name"] == "Single Test Clinic"
    assert org_data["address"] == "456 Medical Ave, Healthcare City"
    assert org_data["phoneNumber"] == "+1-555-0789"

    # Check members
    members = org_data["members"]
    assert len(members) == 2

    # Find owner and radiologist
    owner_member = next(m for m in members if m["role"] == "Owner")
    radiologist_member = next(m for m in members if m["role"] == "Radiologist")

    assert owner_member["user"]["firstName"] == "Dr. Owner"
    assert owner_member["user"]["lastName"] == "Smith"
    assert owner_member["user"]["email"] == "owner@clinic.com"

    assert radiologist_member["user"]["firstName"] == "Dr. Radiologist"
    assert radiologist_member["user"]["lastName"] == "Johnson"
    assert radiologist_member["user"]["email"] == "radiologist@clinic.com"


@pytest.mark.asyncio
async def test_query_organization_members(test_client, db_session):
    """Test querying organization members with roles"""
    # Create organization with multiple members
    org = OrganizationFactory(name="Multi-Member Clinic")

    # Create users
    owner1 = UserFactory(first_name="Owner1", email="owner1@clinic.com")
    owner2 = UserFactory(first_name="Owner2", email="owner2@clinic.com")
    radiologist1 = UserFactory(first_name="Radio1", email="radio1@clinic.com")
    radiologist2 = UserFactory(first_name="Radio2", email="radio2@clinic.com")

    # Create memberships
    OrganizationMemberFactory(user=owner1, organization=org, role=UserRole.OWNER.value)
    OrganizationMemberFactory(user=owner2, organization=org, role=UserRole.OWNER.value)
    OrganizationMemberFactory(
        user=radiologist1, organization=org, role=UserRole.RADIOLOGIST.value
    )
    OrganizationMemberFactory(
        user=radiologist2, organization=org, role=UserRole.RADIOLOGIST.value
    )

    await db_session.commit()
    await db_session.refresh(org)

    query = """
    query($id: ID!) {
        organization(id: $id) {
            id
            name
            members {
                user {
                    firstName
                    email
                }
                role
            }
        }
    }
    """

    response = await test_client.post(
        "/graphql/", json={"query": query, "variables": {"id": str(org.id)}}
    )
    assert response.status_code == 200

    data = response.json()
    org_data = data["data"]["organization"]

    members = org_data["members"]
    assert len(members) == 4

    # Count roles
    owners = [m for m in members if m["role"] == "Owner"]
    radiologists = [m for m in members if m["role"] == "Radiologist"]

    assert len(owners) == 2
    assert len(radiologists) == 2

    # Verify specific members
    owner_names = {m["user"]["firstName"] for m in owners}
    radio_names = {m["user"]["firstName"] for m in radiologists}

    assert owner_names == {"Owner1", "Owner2"}
    assert radio_names == {"Radio1", "Radio2"}
