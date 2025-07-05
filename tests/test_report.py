import pytest

from src.db.models.report import Report, ReportStatus, Study, StudyTemplate
from tests.factories import (OrganizationFactory, ReportFactory, StudyFactory,
                             StudyTemplateFactory, UserFactory)


@pytest.mark.asyncio
async def test_query_reports_paginated(test_client, db_session):
    """Test querying reports with pagination"""
    # Create test data
    org = OrganizationFactory(name="Test Organization")
    user = UserFactory(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        organization=org,
    )
    study = StudyFactory(name="Test Study")
    template = StudyTemplateFactory(study=study)

    await db_session.commit()
    await db_session.refresh(org)
    await db_session.refresh(user)
    await db_session.refresh(study)
    await db_session.refresh(template)

    # Create multiple reports for pagination testing
    reports = []
    for i in range(3):
        report = ReportFactory(
            study=study,
            template=template,
            user=user,
            prompt_text=f"Test prompt {i}",
            result_text=f"Test result {i}",
            status=ReportStatus.draft.value,
        )
        reports.append(report)

    await db_session.commit()
    for report in reports:
        await db_session.refresh(report)

    query = """
    query($first: Int) {
        reports(first: $first) {
            edges {
                cursor
                node {
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
    assert response.status_code == 200

    data = response.json()
    assert "data" in data
    assert "reports" in data["data"]

    reports_data = data["data"]["reports"]
    assert len(reports_data["edges"]) == 2
    assert reports_data["totalCount"] == 3
    assert reports_data["pageInfo"]["hasNextPage"] == True
    assert reports_data["pageInfo"]["hasPreviousPage"] == False
    assert reports_data["pageInfo"]["startCursor"] is not None
    assert reports_data["pageInfo"]["endCursor"] is not None

    # Test first report
    first_report = reports_data["edges"][0]["node"]
    assert first_report["promptText"] == "Test prompt 0"
    assert first_report["resultText"] == "Test result 0"
    assert first_report["status"] == "DRAFT"
    assert first_report["study"]["name"] == "Test Study"
    assert first_report["template"]["sectionNames"] == [
        "Introduction",
        "Methodology",
        "Results",
        "Discussion",
        "Conclusion",
    ]
    assert first_report["user"]["firstName"] == "John"
    assert first_report["user"]["lastName"] == "Doe"
    assert first_report["user"]["email"] == "john.doe@example.com"


@pytest.mark.asyncio
async def test_query_reports_pagination_after(test_client, db_session):
    """Test querying reports with cursor-based pagination"""
    # Create test data
    org = OrganizationFactory(name="Test Organization")
    user = UserFactory(
        first_name="Jane",
        last_name="Smith",
        email="jane.smith@example.com",
        organization=org,
    )
    study = StudyFactory(name="Pagination Test Study")
    template = StudyTemplateFactory(study=study)

    await db_session.commit()
    await db_session.refresh(org)
    await db_session.refresh(user)
    await db_session.refresh(study)
    await db_session.refresh(template)

    # Create multiple reports
    for i in range(5):
        ReportFactory(
            study=study,
            template=template,
            user=user,
            prompt_text=f"Pagination prompt {i}",
            result_text=f"Pagination result {i}",
            status=ReportStatus.draft.value,
        )

    await db_session.commit()

    # First, get the first page
    first_query = """
    query {
        reports(first: 2) {
            edges {
                cursor
                node { 
                    id 
                    promptText
                    resultText
                }
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

    first_data = first_response.json()["data"]["reports"]
    end_cursor = first_data["pageInfo"]["endCursor"]

    # Then get the next page using the cursor
    next_query = """
    query($after: String) {
        reports(first: 2, after: $after) {
            edges {
                node { 
                    id 
                    promptText
                    resultText
                }
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

    next_data = next_response.json()["data"]["reports"]
    assert len(next_data["edges"]) == 2
    assert next_data["pageInfo"]["hasPreviousPage"] == True


@pytest.mark.asyncio
async def test_query_single_report(test_client, db_session):
    """Test querying a single report by ID"""
    # Create test data
    org = OrganizationFactory(name="Single Report Test Org")
    user = UserFactory(
        first_name="Alice",
        last_name="Johnson",
        email="alice.johnson@example.com",
        organization=org,
    )
    study = StudyFactory(name="Single Report Study")
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
        prompt_text="Single report test prompt",
        result_text="Single report test result",
        status=ReportStatus.preliminary.value,
    )

    await db_session.commit()
    await db_session.refresh(report)

    query = """
    query($id: ID!) {
        report(id: $id) {
            id
            promptText
            resultText
            status
            createdAt
            updatedAt
            study {
                id
                name
                createdAt
            }
            template {
                id
                sectionNames
                createdAt
            }
            user {
                id
                firstName
                lastName
                email
            }
            history {
                id
                timestamp
                status
                resultText
            }
            events {
                id
                eventType
                timestamp
                details
            }
        }
    }
    """

    response = await test_client.post(
        "/graphql/", json={"query": query, "variables": {"id": str(report.id)}}
    )
    assert response.status_code == 200

    data = response.json()
    assert "data" in data
    assert "report" in data["data"]

    report_data = data["data"]["report"]
    assert report_data["id"] == str(report.id)
    assert report_data["promptText"] == "Single report test prompt"
    assert report_data["resultText"] == "Single report test result"
    assert report_data["status"] == "PRELIMINARY"
    assert report_data["study"]["name"] == "Single Report Study"
    assert report_data["template"]["sectionNames"] == [
        "Introduction",
        "Methodology",
        "Results",
        "Discussion",
        "Conclusion",
    ]
    assert report_data["user"]["firstName"] == "Alice"
    assert report_data["user"]["lastName"] == "Johnson"
    assert report_data["user"]["email"] == "alice.johnson@example.com"
    assert isinstance(report_data["history"], list)
    assert isinstance(report_data["events"], list)


@pytest.mark.asyncio
async def test_create_report_mutation(test_client, db_session):
    """Test creating a report via GraphQL mutation"""
    # Create test data
    org = OrganizationFactory(name="Create Report Test Org")
    user = UserFactory(
        first_name="Bob",
        last_name="Wilson",
        email="bob.wilson@example.com",
        organization=org,
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
            "userId": str(user.id),
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
    assert report_data["user"]["firstName"] == "Bob"
    assert report_data["user"]["lastName"] == "Wilson"
    assert report_data["user"]["email"] == "bob.wilson@example.com"


@pytest.mark.asyncio
async def test_update_report_mutation(test_client, db_session):
    """Test updating a report via GraphQL mutation"""
    # Create test data
    org = OrganizationFactory(name="Update Report Test Org")
    user = UserFactory(
        first_name="Charlie",
        last_name="Brown",
        email="charlie.brown@example.com",
        organization=org,
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
        organization=org,
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
        organization=org,
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
        organization=org,
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
                "userId": str(user.id),
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


@pytest.mark.asyncio
async def test_query_studies_with_reports(test_client, db_session):
    """Test querying studies with their associated reports"""
    # Create test data
    org = OrganizationFactory(name="Study Reports Test Org")
    user = UserFactory(
        first_name="Grace",
        last_name="Green",
        email="grace.green@example.com",
        organization=org,
    )
    study = StudyFactory(name="Study with Reports")
    template = StudyTemplateFactory(study=study)

    await db_session.commit()
    await db_session.refresh(org)
    await db_session.refresh(user)
    await db_session.refresh(study)
    await db_session.refresh(template)

    # Create multiple reports for the study
    for i in range(3):
        ReportFactory(
            study=study,
            template=template,
            user=user,
            prompt_text=f"Study report {i}",
            result_text=f"Study result {i}",
            status=ReportStatus.draft.value,
        )

    await db_session.commit()

    query = """
    query($id: ID!) {
        study(id: $id) {
            id
            name
            createdAt
            reports {
                id
                promptText
                resultText
                status
                user {
                    firstName
                    lastName
                }
            }
            templates {
                id
                sectionNames
            }
        }
    }
    """

    response = await test_client.post(
        "/graphql/", json={"query": query, "variables": {"id": str(study.id)}}
    )
    assert response.status_code == 200

    data = response.json()
    assert "data" in data
    assert "study" in data["data"]

    study_data = data["data"]["study"]
    assert study_data["id"] == str(study.id)
    assert study_data["name"] == "Study with Reports"
    assert len(study_data["reports"]) == 3
    assert len(study_data["templates"]) == 1

    # Check first report
    first_report = study_data["reports"][0]
    assert first_report["promptText"] == "Study report 0"
    assert first_report["resultText"] == "Study result 0"
    assert first_report["status"] == "DRAFT"
    assert first_report["user"]["firstName"] == "Grace"
    assert first_report["user"]["lastName"] == "Green"

    # Check template
    template_data = study_data["templates"][0]
    assert template_data["sectionNames"] == [
        "Introduction",
        "Methodology",
        "Results",
        "Discussion",
        "Conclusion",
    ]
