import pytest

from src.db.models.report import ReportStatus
from tests.factories import (
    OrganizationFactory,
    ReportFactory,
    StudyFactory,
    StudyTemplateFactory,
    UserFactory,
)


@pytest.mark.asyncio
async def test_create_report_mutation(test_client, db_session):
    """Test creating a report via GraphQL mutation"""
    # Create test data
    org = OrganizationFactory(name="Create Report Test Org")
    user = UserFactory(
        first_name="Bob",
        last_name="Wilson",
        email="bob.wilson@example.com",
    )
    study = StudyFactory(name="Create Report Study")
    template = StudyTemplateFactory(study=study)

    await db_session.commit()
    await db_session.refresh(org)
    await db_session.refresh(user)
    await db_session.refresh(study)
    await db_session.refresh(template)

    mutation = """
    mutation($input: CreateReportInput!) {
        createReport(input: $input) {
            id
            promptText
            resultText
            status
            createdAt
            updatedAt
            study {
                id
                name
            }
            template {
                id
                sectionNames
            }
            user {
                id
                firstName
                lastName
                email
            }
        }
    }
    """

    variables = {
        "input": {
            "studyId": str(study.id),
            "templateId": str(template.id),
            "promptText": "This is a test report creation prompt",
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
    assert report_data["id"] is not None
    assert report_data["promptText"] == "This is a test report creation prompt"
    assert report_data["resultText"] is None  # Should be None for new reports
    assert report_data["status"] == "DRAFT"  # Default status
    assert report_data["createdAt"] is not None
    assert report_data["study"]["name"] == "Create Report Study"
    assert report_data["template"]["sectionNames"] == [
        "Introduction",
        "Methodology",
        "Results",
        "Discussion",
        "Conclusion",
    ]


@pytest.mark.asyncio
async def test_update_report_mutation(test_client, db_session):
    """Test updating a report via GraphQL mutation"""
    # Create test data
    org = OrganizationFactory(name="Update Report Test Org")
    user = UserFactory(
        first_name="Charlie",
        last_name="Brown",
        email="charlie.brown@example.com",
    )
    study = StudyFactory(name="Update Report Study")
    template = StudyTemplateFactory(study=study)

    await db_session.commit()
    await db_session.refresh(org)
    await db_session.refresh(user)
    await db_session.refresh(study)
    await db_session.refresh(template)

    report = ReportFactory(
        study=study,
        template=template,
        user=user,
        prompt_text="Original prompt text",
        result_text="Original result text",
        status=ReportStatus.draft.value,
    )

    await db_session.commit()
    await db_session.refresh(report)

    mutation = """
    mutation($id: ID!, $input: UpdateReportInput!) {
        updateReport(id: $id, input: $input) {
            id
            promptText
            resultText
            status
            updatedAt
            study {
                id
                name
            }
            user {
                id
                firstName
                lastName
            }
        }
    }
    """

    variables = {
        "id": str(report.id),
        "input": {
            "promptText": "Updated prompt text",
            "resultText": "Updated result text",
            "status": "SIGNED",
        },
    }

    response = await test_client.post(
        "/graphql/", json={"query": mutation, "variables": variables}
    )
    assert response.status_code == 200

    data = response.json()
    assert "data" in data
    assert "updateReport" in data["data"]

    report_data = data["data"]["updateReport"]
    assert report_data["id"] == str(report.id)
    assert report_data["promptText"] == "Updated prompt text"
    assert report_data["resultText"] == "Updated result text"
    assert report_data["status"] == "SIGNED"
    assert report_data["updatedAt"] is not None
    assert report_data["study"]["name"] == "Update Report Study"
    assert report_data["user"]["firstName"] == "Charlie"
    assert report_data["user"]["lastName"] == "Brown"


@pytest.mark.asyncio
async def test_partial_update_report_mutation(test_client, db_session):
    """Test partially updating a report via GraphQL mutation"""
    # Create test data
    org = OrganizationFactory(name="Partial Update Test Org")
    user = UserFactory(
        first_name="David",
        last_name="Davis",
        email="david.davis@example.com",
    )
    study = StudyFactory(name="Partial Update Study")
    template = StudyTemplateFactory(study=study)

    await db_session.commit()
    await db_session.refresh(org)
    await db_session.refresh(user)
    await db_session.refresh(study)
    await db_session.refresh(template)

    report = ReportFactory(
        study=study,
        template=template,
        user=user,
        prompt_text="Original prompt for partial update",
        result_text="Original result for partial update",
        status=ReportStatus.draft.value,
    )

    await db_session.commit()
    await db_session.refresh(report)

    mutation = """
    mutation($id: ID!, $input: UpdateReportInput!) {
        updateReport(id: $id, input: $input) {
            id
            promptText
            resultText
            status
        }
    }
    """

    # Only update the status
    variables = {
        "id": str(report.id),
        "input": {
            "status": "PRELIMINARY",
        },
    }

    response = await test_client.post(
        "/graphql/", json={"query": mutation, "variables": variables}
    )
    assert response.status_code == 200

    data = response.json()
    assert "data" in data
    assert "updateReport" in data["data"]

    report_data = data["data"]["updateReport"]
    assert report_data["id"] == str(report.id)
    assert (
        report_data["promptText"] == "Original prompt for partial update"
    )  # Unchanged
    assert (
        report_data["resultText"] == "Original result for partial update"
    )  # Unchanged
    assert report_data["status"] == "PRELIMINARY"  # Updated


@pytest.mark.asyncio
async def test_delete_report_mutation(test_client, db_session):
    """Test deleting a report via GraphQL mutation"""
    # Create test data
    org = OrganizationFactory(name="Delete Report Test Org")
    user = UserFactory(
        first_name="Eve",
        last_name="Evans",
        email="eve.evans@example.com",
    )
    study = StudyFactory(name="Delete Report Study")
    template = StudyTemplateFactory(study=study)

    await db_session.commit()
    await db_session.refresh(org)
    await db_session.refresh(user)
    await db_session.refresh(study)
    await db_session.refresh(template)

    report = ReportFactory(
        study=study,
        template=template,
        user=user,
        prompt_text="Report to be deleted",
        result_text="This report will be deleted",
        status=ReportStatus.draft.value,
    )

    await db_session.commit()
    await db_session.refresh(report)
    report_id = report.id

    mutation = """
    mutation($id: ID!) {
        deleteReport(id: $id)
    }
    """

    variables = {"id": str(report_id)}

    response = await test_client.post(
        "/graphql/", json={"query": mutation, "variables": variables}
    )
    assert response.status_code == 200

    data = response.json()
    assert "data" in data
    assert "deleteReport" in data["data"]
    assert data["data"]["deleteReport"] == True

    # Verify the report is deleted by trying to query it
    query = """
    query($id: ID!) {
        report(id: $id) {
            id
        }
    }
    """

    verify_response = await test_client.post(
        "/graphql/", json={"query": query, "variables": {"id": str(report_id)}}
    )
    assert verify_response.status_code == 200

    verify_data = verify_response.json()
    # The report should not be found or should be null
    assert verify_data["data"]["report"] is None


@pytest.mark.asyncio
async def test_report_with_all_status_types(test_client, db_session):
    """Test creating reports with different status types"""
    # Create test data
    org = OrganizationFactory(name="Status Test Org")
    user = UserFactory(
        first_name="Frank",
        last_name="Foster",
        email="frank.foster@example.com",
    )
    study = StudyFactory(name="Status Test Study")
    template = StudyTemplateFactory(study=study)

    await db_session.commit()
    await db_session.refresh(org)
    await db_session.refresh(user)
    await db_session.refresh(study)
    await db_session.refresh(template)

    # Test all status types
    statuses = ["DRAFT", "PRELIMINARY", "SIGNED", "SIGNED_WITH_ADDENDUM"]

    for status in statuses:
        mutation = """
        mutation($input: CreateReportInput!) {
            createReport(input: $input) {
                id
                status
                promptText
            }
        }
        """

        variables = {
            "input": {
                "studyId": str(study.id),
                "templateId": str(template.id),
                "promptText": f"Test report with {status} status",
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
        assert report_data["status"] == "DRAFT"  # Default status on creation
        assert report_data["promptText"] == f"Test report with {status} status"

        # Now update to the desired status
        update_mutation = """
        mutation($id: ID!, $input: UpdateReportInput!) {
            updateReport(id: $id, input: $input) {
                id
                status
            }
        }
        """

        update_variables = {
            "id": report_data["id"],
            "input": {
                "status": status,
            },
        }

        update_response = await test_client.post(
            "/graphql/", json={"query": update_mutation, "variables": update_variables}
        )
        assert update_response.status_code == 200

        update_data = update_response.json()
        assert update_data["data"]["updateReport"]["status"] == status
