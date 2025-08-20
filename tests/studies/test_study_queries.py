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
async def test_query_studies_with_reports(test_client, db_session):
    """Test querying studies with their associated reports"""
    # Create test data
    org = OrganizationFactory(name="Study Reports Test Org")
    user = UserFactory(
        first_name="Grace",
        last_name="Green",
        email="grace.green@example.com",
    )
    study = StudyFactory(name="Study with Reports", categories=["CT", "Emergency"])
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
            categories
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
    assert study_data["categories"] == ["CT", "Emergency"]
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


@pytest.mark.asyncio
async def test_query_studies_paginated(test_client, db_session):
    """Test querying studies with pagination"""
    # Create test data
    org = OrganizationFactory(name="Study Pagination Test Org")

    # Create multiple studies
    studies = []
    for i in range(5):
        study = StudyFactory(name=f"Study {i}")
        studies.append(study)

    await db_session.commit()

    query = """
    query {
        studies(first: 3) {
            edges {
                cursor
                node {
                    id
                    name
                    categories
                    createdAt
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
    assert "studies" in data["data"]

    studies_data = data["data"]["studies"]
    assert len(studies_data["edges"]) == 3
    assert studies_data["totalCount"] == 5
    assert studies_data["pageInfo"]["hasNextPage"] == True
    assert studies_data["pageInfo"]["hasPreviousPage"] == False


@pytest.mark.asyncio
async def test_query_single_study(test_client, db_session):
    """Test querying a single study by ID"""
    study = StudyFactory(
        name="Single Study Test", categories=["Ultrasound", "Pediatric"]
    )
    template = StudyTemplateFactory(study=study)

    await db_session.commit()
    await db_session.refresh(study)
    await db_session.refresh(template)

    query = """
    query($id: ID!) {
        study(id: $id) {
            id
            name
            categories
            createdAt
            templates {
                id
                sectionNames
                createdAt
            }
            reports {
                id
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
    assert study_data["name"] == "Single Study Test"
    assert study_data["categories"] == ["Ultrasound", "Pediatric"]
    assert study_data["createdAt"] is not None
    assert len(study_data["templates"]) == 1
    assert len(study_data["reports"]) == 0  # No reports created for this test

    template_data = study_data["templates"][0]
    assert template_data["id"] == str(template.id)
    assert template_data["sectionNames"] == [
        "Introduction",
        "Methodology",
        "Results",
        "Discussion",
        "Conclusion",
    ]
