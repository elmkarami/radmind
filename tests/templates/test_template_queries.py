import pytest

from tests.factories import StudyFactory, StudyTemplateFactory


@pytest.mark.asyncio
async def test_query_study_templates(test_client, db_session):
    """Test querying templates associated with a study"""
    # Create study with templates
    study = StudyFactory(name="Template Test Study")
    template1 = StudyTemplateFactory(
        study=study, section_names=["Introduction", "Methods", "Results", "Conclusion"]
    )
    template2 = StudyTemplateFactory(
        study=study, section_names=["Background", "Procedure", "Findings", "Discussion"]
    )

    await db_session.commit()
    await db_session.refresh(study)
    await db_session.refresh(template1)
    await db_session.refresh(template2)

    query = """
    query($id: ID!) {
        study(id: $id) {
            id
            name
            templates {
                id
                sectionNames
                createdAt
                study {
                    id
                    name
                }
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
    assert study_data["name"] == "Template Test Study"
    assert len(study_data["templates"]) == 2

    # Check templates
    templates = study_data["templates"]
    template_sections = [t["sectionNames"] for t in templates]

    assert ["Introduction", "Methods", "Results", "Conclusion"] in template_sections
    assert ["Background", "Procedure", "Findings", "Discussion"] in template_sections

    # Verify template relationships
    for template in templates:
        assert template["study"]["id"] == str(study.id)
        assert template["study"]["name"] == "Template Test Study"
        assert template["createdAt"] is not None


@pytest.mark.asyncio
async def test_query_default_template_sections(test_client, db_session):
    """Test that default template has standard sections"""
    study = StudyFactory(name="Default Template Study")
    template = StudyTemplateFactory(study=study)  # Uses default section_names

    await db_session.commit()
    await db_session.refresh(study)
    await db_session.refresh(template)

    query = """
    query($id: ID!) {
        study(id: $id) {
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
    study_data = data["data"]["study"]

    assert len(study_data["templates"]) == 1
    template_data = study_data["templates"][0]

    # Check default sections
    expected_sections = [
        "Introduction",
        "Methodology",
        "Results",
        "Discussion",
        "Conclusion",
    ]
    assert template_data["sectionNames"] == expected_sections


@pytest.mark.asyncio
async def test_query_multiple_studies_with_templates(test_client, db_session):
    """Test querying multiple studies and their templates"""
    # Create studies with different template configurations
    study1 = StudyFactory(name="Study 1")
    study2 = StudyFactory(name="Study 2")
    study3 = StudyFactory(name="Study 3")

    # Study 1: Default template
    StudyTemplateFactory(study=study1)

    # Study 2: Custom template
    StudyTemplateFactory(
        study=study2, section_names=["Overview", "Analysis", "Summary"]
    )

    # Study 3: Multiple templates
    StudyTemplateFactory(study=study3, section_names=["Template A"])
    StudyTemplateFactory(study=study3, section_names=["Template B"])

    await db_session.commit()

    query = """
    query {
        studies {
            edges {
                node {
                    id
                    name
                    templates {
                        id
                        sectionNames
                    }
                }
            }
        }
    }
    """

    response = await test_client.post("/graphql/", json={"query": query})
    assert response.status_code == 200

    data = response.json()
    studies_data = data["data"]["studies"]["edges"]

    # Should have at least our 3 studies
    study_nodes = [edge["node"] for edge in studies_data]
    study_names = [s["name"] for s in study_nodes]

    assert "Study 1" in study_names
    assert "Study 2" in study_names
    assert "Study 3" in study_names

    # Find our specific studies
    study1_data = next(s for s in study_nodes if s["name"] == "Study 1")
    study2_data = next(s for s in study_nodes if s["name"] == "Study 2")
    study3_data = next(s for s in study_nodes if s["name"] == "Study 3")

    # Verify template counts
    assert len(study1_data["templates"]) == 1
    assert len(study2_data["templates"]) == 1
    assert len(study3_data["templates"]) == 2

    # Verify specific template content
    assert study2_data["templates"][0]["sectionNames"] == [
        "Overview",
        "Analysis",
        "Summary",
    ]

    study3_sections = [t["sectionNames"] for t in study3_data["templates"]]
    assert ["Template A"] in study3_sections
    assert ["Template B"] in study3_sections
