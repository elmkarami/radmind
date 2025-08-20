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
async def test_query_reports_paginated(test_client, db_session):
    """Test querying reports with pagination"""
    # Create test data
    org = OrganizationFactory(name="Test Organization")
    user = UserFactory(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
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
    query {
        reports(first: 2) {
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

    response = await test_client.post("/graphql/", json={"query": query})
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
