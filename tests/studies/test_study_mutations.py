import pytest

from tests.factories import OrganizationFactory, StudyFactory, UserFactory


@pytest.mark.asyncio
async def test_create_study_mutation(test_client, db_session):
    """Test creating a study via GraphQL mutation"""
    mutation = """
    mutation($input: CreateStudyInput!) {
        createStudy(input: $input) {
            id
            name
            categories
            createdAt
            templates {
                id
            }
            reports {
                id
            }
        }
    }
    """

    variables = {
        "input": {
            "name": "Test Study Creation",
            "categories": ["CT", "Emergency", "Neurological"],
        }
    }

    response = await test_client.post(
        "/graphql/", json={"query": mutation, "variables": variables}
    )
    assert response.status_code == 200

    data = response.json()
    assert "data" in data
    assert "createStudy" in data["data"]

    study_data = data["data"]["createStudy"]
    assert study_data["id"] is not None
    assert study_data["name"] == "Test Study Creation"
    assert study_data["categories"] == ["CT", "Emergency", "Neurological"]
    assert study_data["createdAt"] is not None
    assert isinstance(study_data["templates"], list)
    assert isinstance(study_data["reports"], list)


@pytest.mark.asyncio
async def test_update_study_mutation(test_client, db_session):
    """Test updating a study via GraphQL mutation"""
    # Create test study
    study = StudyFactory(name="Original Study Name", categories=["MRI", "Cardiac"])

    await db_session.commit()
    await db_session.refresh(study)

    mutation = """
    mutation($id: ID!, $input: UpdateStudyInput!) {
        updateStudy(id: $id, input: $input) {
            id
            name
            categories
            createdAt
        }
    }
    """

    variables = {
        "id": str(study.id),
        "input": {
            "name": "Updated Study Name",
            "categories": ["X-ray", "Emergency", "Orthopedic"],
        },
    }

    response = await test_client.post(
        "/graphql/", json={"query": mutation, "variables": variables}
    )
    assert response.status_code == 200

    data = response.json()
    assert "data" in data
    assert "updateStudy" in data["data"]

    study_data = data["data"]["updateStudy"]
    assert study_data["id"] == str(study.id)
    assert study_data["name"] == "Updated Study Name"
    assert study_data["categories"] == ["X-ray", "Emergency", "Orthopedic"]
    assert study_data["createdAt"] is not None


@pytest.mark.asyncio
async def test_delete_study_mutation(test_client, db_session):
    """Test deleting a study via GraphQL mutation"""
    # Create test study
    study = StudyFactory(name="Study to be deleted")

    await db_session.commit()
    await db_session.refresh(study)
    study_id = study.id

    mutation = """
    mutation($id: ID!) {
        deleteStudy(id: $id)
    }
    """

    variables = {"id": str(study_id)}

    response = await test_client.post(
        "/graphql/", json={"query": mutation, "variables": variables}
    )
    assert response.status_code == 200

    data = response.json()
    assert "data" in data
    assert "deleteStudy" in data["data"]
    assert data["data"]["deleteStudy"] == True

    # Verify the study is deleted by trying to query it
    query = """
    query($id: ID!) {
        study(id: $id) {
            id
        }
    }
    """

    verify_response = await test_client.post(
        "/graphql/", json={"query": query, "variables": {"id": str(study_id)}}
    )
    assert verify_response.status_code == 200

    verify_data = verify_response.json()
    # The study should not be found or should be null
    assert verify_data["data"]["study"] is None
