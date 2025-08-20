import pytest

from tests.factories import (
    ReportFactory,
    StudyFactory,
    StudyTemplateFactory,
    UserFactory,
)


@pytest.mark.asyncio
async def test_filter_studies_by_categories(test_client, db_session):
    """Test filtering studies by categories"""
    # Create studies with different categories
    study1 = StudyFactory(name="CT Brain Study", categories=["CT", "Neurological"])
    study2 = StudyFactory(name="MRI Cardiac Study", categories=["MRI", "Cardiac"])
    study3 = StudyFactory(
        name="X-ray Emergency Study", categories=["X-ray", "Emergency"]
    )
    study4 = StudyFactory(name="CT Cardiac Study", categories=["CT", "Cardiac"])

    await db_session.commit()
    for study in [study1, study2, study3, study4]:
        await db_session.refresh(study)

    # Test filtering by single category
    query = """
    query($filter: StudyFilterInput) {
        studies(first: 10, filter: $filter) {
            edges {
                node {
                    id
                    name
                    categories
                }
            }
            totalCount
        }
    }
    """

    variables = {"filter": {"categories": ["CT"]}}

    response = await test_client.post(
        "/graphql/", json={"query": query, "variables": variables}
    )
    assert response.status_code == 200

    data = response.json()
    studies_data = data["data"]["studies"]

    # Should return 2 studies with CT category
    assert studies_data["totalCount"] == 2
    assert len(studies_data["edges"]) == 2

    returned_names = {edge["node"]["name"] for edge in studies_data["edges"]}
    assert returned_names == {"CT Brain Study", "CT Cardiac Study"}

    # Test filtering by multiple categories (OR logic)
    variables = {"filter": {"categories": ["MRI", "Emergency"]}}

    response = await test_client.post(
        "/graphql/", json={"query": query, "variables": variables}
    )
    assert response.status_code == 200

    data = response.json()
    studies_data = data["data"]["studies"]

    # Should return 2 studies with either MRI or Emergency categories
    assert studies_data["totalCount"] == 2
    assert len(studies_data["edges"]) == 2

    returned_names = {edge["node"]["name"] for edge in studies_data["edges"]}
    assert returned_names == {"MRI Cardiac Study", "X-ray Emergency Study"}


@pytest.mark.asyncio
async def test_filter_reports_by_study(test_client, db_session):
    """Test filtering reports by study ID"""
    # Create test data
    user = UserFactory(first_name="Test", last_name="User")
    study1 = StudyFactory(name="Study 1", categories=["CT"])
    study2 = StudyFactory(name="Study 2", categories=["MRI"])
    template1 = StudyTemplateFactory(study=study1)
    template2 = StudyTemplateFactory(study=study2)

    await db_session.commit()
    for item in [user, study1, study2, template1, template2]:
        await db_session.refresh(item)

    # Create reports for different studies
    report1 = ReportFactory(
        study=study1, template=template1, user=user, prompt_text="Report 1"
    )
    report2 = ReportFactory(
        study=study1, template=template1, user=user, prompt_text="Report 2"
    )
    report3 = ReportFactory(
        study=study2, template=template2, user=user, prompt_text="Report 3"
    )

    await db_session.commit()

    # Test filtering by study ID
    query = """
    query($filter: ReportFilterInput) {
        reports(first: 10, filter: $filter) {
            edges {
                node {
                    id
                    promptText
                    study {
                        name
                    }
                }
            }
            totalCount
        }
    }
    """

    variables = {"filter": {"studyId": str(study1.id)}}

    response = await test_client.post(
        "/graphql/", json={"query": query, "variables": variables}
    )
    assert response.status_code == 200

    data = response.json()
    reports_data = data["data"]["reports"]

    # Should return 2 reports for study1
    assert reports_data["totalCount"] == 2
    assert len(reports_data["edges"]) == 2

    for edge in reports_data["edges"]:
        assert edge["node"]["study"]["name"] == "Study 1"


@pytest.mark.asyncio
async def test_filter_reports_by_template(test_client, db_session):
    """Test filtering reports by template ID"""
    # Create test data
    user = UserFactory(first_name="Test", last_name="User")
    study = StudyFactory(name="Test Study", categories=["CT"])
    template1 = StudyTemplateFactory(study=study)
    template2 = StudyTemplateFactory(study=study)

    await db_session.commit()
    for item in [user, study, template1, template2]:
        await db_session.refresh(item)

    # Create reports for different templates
    report1 = ReportFactory(
        study=study, template=template1, user=user, prompt_text="Report 1"
    )
    report2 = ReportFactory(
        study=study, template=template2, user=user, prompt_text="Report 2"
    )

    await db_session.commit()

    # Test filtering by template ID
    query = """
    query($filter: ReportFilterInput) {
        reports(first: 10, filter: $filter) {
            edges {
                node {
                    id
                    promptText
                    template {
                        id
                    }
                }
            }
            totalCount
        }
    }
    """

    variables = {"filter": {"templateId": str(template1.id)}}

    response = await test_client.post(
        "/graphql/", json={"query": query, "variables": variables}
    )
    assert response.status_code == 200

    data = response.json()
    reports_data = data["data"]["reports"]

    # Should return 1 report for template1
    assert reports_data["totalCount"] == 1
    assert len(reports_data["edges"]) == 1
    assert reports_data["edges"][0]["node"]["template"]["id"] == str(template1.id)


@pytest.mark.asyncio
async def test_filter_reports_by_study_categories(test_client, db_session):
    """Test filtering reports by study categories"""
    # Create test data
    user = UserFactory(first_name="Test", last_name="User")
    study1 = StudyFactory(name="CT Study", categories=["CT", "Emergency"])
    study2 = StudyFactory(name="MRI Study", categories=["MRI", "Cardiac"])
    study3 = StudyFactory(name="X-ray Study", categories=["X-ray", "Orthopedic"])

    template1 = StudyTemplateFactory(study=study1)
    template2 = StudyTemplateFactory(study=study2)
    template3 = StudyTemplateFactory(study=study3)

    await db_session.commit()
    for item in [user, study1, study2, study3, template1, template2, template3]:
        await db_session.refresh(item)

    # Create reports for different studies
    report1 = ReportFactory(
        study=study1, template=template1, user=user, prompt_text="CT Report"
    )
    report2 = ReportFactory(
        study=study2, template=template2, user=user, prompt_text="MRI Report"
    )
    report3 = ReportFactory(
        study=study3, template=template3, user=user, prompt_text="X-ray Report"
    )

    await db_session.commit()

    # Test filtering by study categories
    query = """
    query($filter: ReportFilterInput) {
        reports(first: 10, filter: $filter) {
            edges {
                node {
                    id
                    promptText
                    study {
                        name
                        categories
                    }
                }
            }
            totalCount
        }
    }
    """

    # Filter for reports whose studies have "CT" or "MRI" categories
    variables = {"filter": {"studyCategories": ["CT", "MRI"]}}

    response = await test_client.post(
        "/graphql/", json={"query": query, "variables": variables}
    )
    assert response.status_code == 200

    data = response.json()
    reports_data = data["data"]["reports"]

    # Should return 2 reports (CT and MRI studies)
    assert reports_data["totalCount"] == 2
    assert len(reports_data["edges"]) == 2

    returned_study_names = {
        edge["node"]["study"]["name"] for edge in reports_data["edges"]
    }
    assert returned_study_names == {"CT Study", "MRI Study"}
