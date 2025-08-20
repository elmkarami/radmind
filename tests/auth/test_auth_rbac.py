import pytest

from src.db.models.user import UserRole
from tests.factories import (
    OrganizationFactory,
    OrganizationMemberFactory,
    StudyFactory,
    StudyTemplateFactory,
    UserFactory,
)


@pytest.mark.asyncio
async def test_login_mutation(test_client, db_session):
    """Test login mutation with valid credentials"""
    # Create test user
    user = UserFactory(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        password_must_change=False,
    )
    user.set_password("Password123!")

    await db_session.commit()
    await db_session.refresh(user)

    mutation = """
    mutation($email: String!, $password: String!) {
        login(email: $email, password: $password) {
            token
            user {
                id
                firstName
                lastName
                email
                mustChangePassword
            }
            mustChangePassword
        }
    }
    """

    variables = {"email": "john.doe@example.com", "password": "Password123!"}

    response = await test_client.post(
        "/graphql/", json={"query": mutation, "variables": variables}
    )
    assert response.status_code == 200

    data = response.json()
    assert "data" in data
    assert "login" in data["data"]

    login_data = data["data"]["login"]
    assert login_data["token"] is not None
    assert login_data["user"]["email"] == "john.doe@example.com"
    assert login_data["user"]["firstName"] == "John"
    assert login_data["mustChangePassword"] == False


@pytest.mark.asyncio
async def test_login_mutation_invalid_credentials(test_client, db_session):
    """Test login mutation with invalid credentials"""
    # Create test user
    user = UserFactory(email="john.doe@example.com")
    user.set_password("Password123!")

    await db_session.commit()

    mutation = """
    mutation($email: String!, $password: String!) {
        login(email: $email, password: $password) {
            token
            user {
                id
                email
            }
            mustChangePassword
        }
    }
    """

    variables = {"email": "john.doe@example.com", "password": "WrongPassword"}

    response = await test_client.post(
        "/graphql/", json={"query": mutation, "variables": variables}
    )
    assert response.status_code == 200

    data = response.json()
    assert "errors" in data


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
async def test_invite_radiologist(test_client, db_session, authenticated_user):
    """Test owner can invite radiologist to organization"""
    # Create organization with authenticated user as owner
    org = OrganizationFactory(name="Test Clinic")

    # Create owner membership for authenticated user
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
async def test_get_radiologist_temp_password(
    test_client, db_session, authenticated_user
):
    """Test owner can view radiologist's temporary password"""
    # Create organization with authenticated_user as owner
    org = OrganizationFactory(name="Test Clinic")
    radiologist = UserFactory(
        first_name="Jane",
        email="jane@clinic.com",
        temp_password="TempPass123!",
        password_must_change=True,
    )

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
    mutation($userId: ID!) {
        getRadiologistPassword(userId: $userId)
    }
    """

    variables = {"userId": str(radiologist.id)}

    response = await test_client.post(
        "/graphql/", json={"query": mutation, "variables": variables}
    )
    assert response.status_code == 200

    data = response.json()
    assert "data" in data
    assert "getRadiologistPassword" in data["data"]
    assert data["data"]["getRadiologistPassword"] == "TempPass123!"


@pytest.mark.asyncio
async def test_force_password_reset(test_client, db_session, authenticated_user):
    """Test owner can force password reset for radiologist"""
    # Create organization with authenticated_user as owner
    org = OrganizationFactory(name="Test Clinic")
    radiologist = UserFactory(
        first_name="Jane", email="jane@clinic.com", password_must_change=False
    )

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
    mutation($userId: ID!) {
        forcePasswordReset(userId: $userId)
    }
    """

    variables = {"userId": str(radiologist.id)}

    response = await test_client.post(
        "/graphql/", json={"query": mutation, "variables": variables}
    )
    assert response.status_code == 200

    data = response.json()
    assert "data" in data
    assert "forcePasswordReset" in data["data"]

    # Should return a new temporary password
    new_temp_password = data["data"]["forcePasswordReset"]
    assert new_temp_password is not None
    assert len(new_temp_password) == 12  # Default generated password length


@pytest.mark.asyncio
async def test_create_report_without_user_id(test_client, db_session):
    """Test creating report doesn't require userId - comes from auth context"""
    # Create test data
    org = OrganizationFactory(name="Test Organization")
    user = UserFactory(first_name="Test", email="test@example.com")

    # Create organization membership
    OrganizationMemberFactory(
        user=user, organization=org, role=UserRole.RADIOLOGIST.value
    )

    study = StudyFactory(name="Test Study")
    template = StudyTemplateFactory(study=study)

    await db_session.commit()
    await db_session.refresh(study)
    await db_session.refresh(template)

    mutation = """
    mutation($input: CreateReportInput!) {
        createReport(input: $input) {
            id
            promptText
            status
            user {
                firstName
                email
            }
            study {
                name
            }
        }
    }
    """

    # Note: No userId in input - should come from auth context
    variables = {
        "input": {
            "studyId": str(study.id),
            "templateId": str(template.id),
            "promptText": "Test report creation without explicit userId",
        }
    }

    response = await test_client.post(
        "/graphql/", json={"query": mutation, "variables": variables}
    )
    assert response.status_code == 200

    data = response.json()
    assert "data" in data
    assert "createReport" in data["data"]

    report_data = data["data"]["createReport"]
    assert report_data["promptText"] == "Test report creation without explicit userId"
    assert report_data["status"] == "DRAFT"
    assert report_data["study"]["name"] == "Test Study"
    # User should be populated from auth context (placeholder currently)


@pytest.mark.asyncio
async def test_organization_members_query(test_client, db_session, authenticated_user):
    """Test querying organization members shows roles correctly"""
    # Create organization with multiple members
    org = OrganizationFactory(name="Multi-Member Clinic")
    radiologist1 = UserFactory(first_name="Alice", email="alice@clinic.com")
    radiologist2 = UserFactory(first_name="Bob", email="bob@clinic.com")

    # Create memberships (use authenticated_user as owner)
    OrganizationMemberFactory(
        user=authenticated_user, organization=org, role=UserRole.OWNER.value
    )
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
            createdBy {
                firstName
            }
            members {
                user {
                    firstName
                    email
                }
                role
                createdAt
            }
        }
    }
    """

    variables = {"id": str(org.id)}

    response = await test_client.post(
        "/graphql/", json={"query": query, "variables": variables}
    )
    assert response.status_code == 200

    data = response.json()
    assert "data" in data
    assert "organization" in data["data"]

    org_data = data["data"]["organization"]
    assert org_data["name"] == "Multi-Member Clinic"

    members = org_data["members"]
    assert len(members) == 3

    # Check roles are assigned correctly
    owner_member = next(m for m in members if m["user"]["firstName"] == "AuthUser")
    assert owner_member["role"] == "Owner"

    alice_member = next(m for m in members if m["user"]["firstName"] == "Alice")
    assert alice_member["role"] == "Radiologist"

    bob_member = next(m for m in members if m["user"]["firstName"] == "Bob")
    assert bob_member["role"] == "Radiologist"
