import factory
from factory import Faker, LazyFunction
from datetime import datetime

from src.db.models.report import (
    Study,
    StudyTemplate,
    Report,
    ReportHistory,
    ReportEvent,
    ReportStatus,
)
from .user_factories import UserFactory
from .base import BaseFactory


class StudyFactory(BaseFactory):
    class Meta:
        model = Study

    name = Faker("catch_phrase")


class StudyTemplateFactory(BaseFactory):
    class Meta:
        model = StudyTemplate

    study = factory.SubFactory(StudyFactory)
    section_names = factory.LazyFunction(
        lambda: [
            "Introduction",
            "Methodology", 
            "Results",
            "Discussion",
            "Conclusion"
        ]
    )


class ReportFactory(BaseFactory):
    class Meta:
        model = Report

    study = factory.SubFactory(StudyFactory)
    template = factory.SubFactory(StudyTemplateFactory)
    user = factory.SubFactory(UserFactory)
    prompt_text = Faker("paragraph", nb_sentences=5)
    result_text = Faker("text", max_nb_chars=2000)
    status = Faker("random_element", elements=[status.value for status in ReportStatus])
    updated_at = LazyFunction(datetime.now)


class ReportHistoryFactory(BaseFactory):
    class Meta:
        model = ReportHistory

    report = factory.SubFactory(ReportFactory)
    status = Faker("random_element", elements=[status.value for status in ReportStatus])
    result_text = Faker("text", max_nb_chars=2000)


class ReportEventFactory(BaseFactory):
    class Meta:
        model = ReportEvent

    report = factory.SubFactory(ReportFactory)
    event_type = Faker("random_element", elements=[
        "created", 
        "updated", 
        "status_changed", 
        "reviewed", 
        "signed", 
        "archived"
    ])
    details = Faker("sentence", nb_words=10) 