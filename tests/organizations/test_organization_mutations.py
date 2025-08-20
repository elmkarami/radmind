import pytest

from src.db.models.user import UserRole
from tests.factories import OrganizationFactory, OrganizationMemberFactory, UserFactory


@pytest.mark.asyncio
async def test_create_organization_with_owner(
    test_client, db_session, authenticated_user
):
    """Test creating organization automatically assigns creator as owner"""
    # The authenticated_user will be the creator

    mutation = """
    mutation($input: CreateOrganizationInput!) {
        createOrganization(input: $input) {
            id
            name
            address
            phoneNumber
            createdBy {
                id
                firstName
                lastName
            }
            members {
                user {
                    id
                    firstName
                }
                role
            }
        }
    }
    """

    variables = {
        "input": {
            "name": "Test Radiology Clinic",
            "address": "123 Medical St, City, State 12345",
            "phoneNumber": "+1-555-0123",
        }
    }

    response = await test_client.post(
        "/graphql/", json={"query": mutation, "variables": variables}
    )
    assert response.status_code == 200

    data = response.json()
    assert "data" in data
    assert "createOrganization" in data["data"]

    org_data = data["data"]["createOrganization"]
    assert org_data["name"] == "Test Radiology Clinic"
    assert org_data["createdBy"]["firstName"] == "AuthUser"

    # Check that creator is automatically added as OWNER
    members = org_data["members"]
    assert len(members) == 1
    assert members[0]["user"]["firstName"] == "AuthUser"
    assert members[0]["role"] == "Owner"


@pytest.mark.asyncio
async def test_update_organization_mutation(test_client, db_session):
    """Test updating organization details"""
    # Create organization
    org = OrganizationFactory(
        name="Original Clinic Name",
        address="Original Address",
        phone_number="+1-555-0000",
    )

    await db_session.commit()
    await db_session.refresh(org)

    mutation = """
    mutation($id: ID!, $input: UpdateOrganizationInput!) {
        updateOrganization(id: $id, input: $input) {
            id
            name
            address
            phoneNumber
            logo
        }
    }
    """

    variables = {
        "id": str(org.id),
        "input": {
            "name": "Updated Clinic Name",
            "address": "Updated Address, New City, State",
            "phoneNumber": "+1-555-9999",
            "logo": "https://example.com/new-logo.png",
        },
    }

    response = await test_client.post(
        "/graphql/", json={"query": mutation, "variables": variables}
    )
    assert response.status_code == 200

    data = response.json()
    assert "data" in data
    assert "updateOrganization" in data["data"]

    org_data = data["data"]["updateOrganization"]
    assert org_data["id"] == str(org.id)
    assert org_data["name"] == "Updated Clinic Name"
    assert org_data["address"] == "Updated Address, New City, State"
    assert org_data["phoneNumber"] == "+1-555-9999"
    assert org_data["logo"] == "https://example.com/new-logo.png"


@pytest.mark.asyncio
async def test_delete_organization_mutation(
    test_client, db_session, authenticated_user
):
    """Test deleting an organization (owner only)"""
    # Create organization with authenticated user as owner
    org = OrganizationFactory(name="Clinic to Delete")

    OrganizationMemberFactory(
        user=authenticated_user, organization=org, role=UserRole.OWNER.value
    )

    await db_session.commit()
    await db_session.refresh(org)
    org_id = org.id

    mutation = """
    mutation($id: ID!) {
        deleteOrganization(id: $id)
    }
    """

    variables = {"id": str(org_id)}

    response = await test_client.post(
        "/graphql/", json={"query": mutation, "variables": variables}
    )
    assert response.status_code == 200

    data = response.json()
    assert "data" in data
    assert "deleteOrganization" in data["data"]
    assert data["data"]["deleteOrganization"] == True

    # Verify organization is deleted
    query = """
    query($id: ID!) {
        organization(id: $id) {
            id
        }
    }
    """

    verify_response = await test_client.post(
        "/graphql/", json={"query": query, "variables": {"id": str(org_id)}}
    )
    assert verify_response.status_code == 200

    verify_data = verify_response.json()
    assert verify_data["data"]["organization"] is None


@pytest.mark.asyncio
async def test_invite_radiologist_mutation(test_client, db_session, authenticated_user):
    """Test owner can invite radiologist to organization"""
    # Create organization with authenticated user as owner
    org = OrganizationFactory(name="Test Clinic")

    # Create owner membership
    owner_membership = OrganizationMemberFactory(
        user=authenticated_user, organization=org, role=UserRole.OWNER.value
    )

    await db_session.commit()
    await db_session.refresh(org)
    await db_session.refresh(authenticated_user)
    await db_session.refresh(owner_membership)

    mutation = """
    mutation($organizationId: ID!, $input: InviteRadiologistInput!) {
        inviteRadiologist(organizationId: $organizationId, input: $input) {
            id
            firstName
            lastName
            email
            mustChangePassword
            organizationMemberships {
                role
                organization {
                    name
                }
            }
        }
    }
    """

    variables = {
        "organizationId": str(org.id),
        "input": {
            "firstName": "Jane",
            "lastName": "Radiologist",
            "email": "jane.radiologist@clinic.com",
            "phoneNumber": "+1-555-0456",
        },
    }

    response = await test_client.post(
        "/graphql/", json={"query": mutation, "variables": variables}
    )
    assert response.status_code == 200

    data = response.json()
    assert "data" in data
    assert "inviteRadiologist" in data["data"]

    radiologist_data = data["data"]["inviteRadiologist"]
    assert radiologist_data["firstName"] == "Jane"
    assert radiologist_data["lastName"] == "Radiologist"
    assert radiologist_data["email"] == "jane.radiologist@clinic.com"
    assert radiologist_data["mustChangePassword"] == True

    # Check organization membership
    memberships = radiologist_data["organizationMemberships"]
    assert len(memberships) == 1
    assert memberships[0]["role"] == "Radiologist"
    assert memberships[0]["organization"]["name"] == "Test Clinic"


@pytest.mark.asyncio
async def test_remove_radiologist_mutation(test_client, db_session, authenticated_user):
    """Test owner can remove radiologist from organization"""
    # Create organization with authenticated user as owner
    org = OrganizationFactory(name="Test Clinic")
    radiologist = UserFactory(first_name="Jane", email="jane@clinic.com")

    # Create memberships
    OrganizationMemberFactory(
        user=authenticated_user, organization=org, role=UserRole.OWNER.value
    )
    OrganizationMemberFactory(
        user=radiologist, organization=org, role=UserRole.RADIOLOGIST.value
    )

    await db_session.commit()
    await db_session.refresh(radiologist)

    mutation = """
    mutation($userId: ID!, $organizationId: ID!) {
        removeRadiologist(userId: $userId, organizationId: $organizationId)
    }
    """

    variables = {"userId": str(radiologist.id), "organizationId": str(org.id)}

    response = await test_client.post(
        "/graphql/", json={"query": mutation, "variables": variables}
    )
    assert response.status_code == 200

    data = response.json()
    assert "data" in data
    assert "removeRadiologist" in data["data"]
    assert data["data"]["removeRadiologist"] == True

    # Verify radiologist is no longer a member
    verify_query = """
    query($id: ID!) {
        organization(id: $id) {
            members {
                user {
                    firstName
                }
                role
            }
        }
    }
    """

    verify_response = await test_client.post(
        "/graphql/", json={"query": verify_query, "variables": {"id": str(org.id)}}
    )
    assert verify_response.status_code == 200

    verify_data = verify_response.json()
    members = verify_data["data"]["organization"]["members"]

    # Should only have the owner left
    assert len(members) == 1
    assert members[0]["user"]["firstName"] == "AuthUser"
    assert members[0]["role"] == "Owner"
