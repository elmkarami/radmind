import random
from datetime import datetime

import factory
from factory import Faker, LazyFunction

from src.db.models.report import (
    Report,
    ReportEvent,
    ReportHistory,
    ReportStatus,
    Study,
    StudyTemplate,
)
from tests.factories.base import BaseFactory
from tests.factories.user_factories import UserFactory


class StudyFactory(BaseFactory):
    class Meta:
        model = Study

    name = Faker("catch_phrase")

    @factory.lazy_attribute
    def categories(self):
        categories_options = [
            "CT",
            "MRI",
            "X-ray",
            "Ultrasound",
            "Emergency",
            "Cardiac",
            "Neurological",
        ]
        return random.sample(categories_options, random.randint(1, 3))


class StudyTemplateFactory(BaseFactory):
    class Meta:
        model = StudyTemplate

    study = factory.SubFactory(StudyFactory)
    section_names = factory.LazyFunction(
        lambda: ["Introduction", "Methodology", "Results", "Discussion", "Conclusion"]
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
    event_type = Faker(
        "random_element",
        elements=[
            "created",
            "updated",
            "status_changed",
            "reviewed",
            "signed",
            "archived",
        ],
    )
    details = Faker("sentence", nb_words=10)
