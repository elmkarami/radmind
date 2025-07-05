import asyncio
import random

import factory
from factory import Faker

from src.db import db
from src.db.models.report import (Report, ReportEvent, ReportHistory,
                                  ReportStatus, Study, StudyTemplate)
from src.db.models.user import Organization, User


class OrganizationFactory(factory.Factory):
    class Meta:
        model = Organization

    name = Faker("company")
    logo = Faker("image_url")
    address = Faker("address")
    phone_number = Faker("phone_number")


class UserFactory(factory.Factory):
    class Meta:
        model = User

    first_name = Faker("first_name")
    last_name = Faker("last_name")
    email = Faker("email")
    phone_number = Faker("phone_number")
    password = "hashed_password"
    role = Faker("random_element", elements=["admin", "doctor", "technician", "viewer"])


radiology_studies = [
    # CT
    "CT Head Without Contrast",
    "CT Head With Contrast",
    "CT Chest Without Contrast",
    "CT Chest With Contrast",
    "CT Abdomen and Pelvis Without Contrast",
    "CT Abdomen and Pelvis With Contrast",
    "CT Cervical Spine",
    "CT Thoracic Spine",
    "CT Lumbar Spine",
    "CT Angiogram Pulmonary",
    "CT Angiogram Head and Neck",
    "CT Sinuses Without Contrast",
    "CT Temporal Bones",
    "CT Facial Bones",
    "CT Maxillofacial With Contrast",
    "CT Enterography",
    "CT Urogram",
    "CT Colonography",
    # MRI
    "MRI Brain Without Contrast",
    "MRI Brain With and Without Contrast",
    "MRI Cervical Spine Without Contrast",
    "MRI Thoracic Spine Without Contrast",
    "MRI Lumbar Spine Without Contrast",
    "MRI Knee Right",
    "MRI Knee Left",
    "MRI Shoulder Right",
    "MRI Shoulder Left",
    "MRI Pelvis With Contrast",
    "MRI Abdomen With and Without Contrast",
    "MRI Orbits With Contrast",
    "MRI Wrist Right",
    "MRI Wrist Left",
    "MRI Elbow Right",
    "MRI Breast Bilateral",
    "MRI Prostate Multiparametric",
    "MRCP (Magnetic Resonance Cholangiopancreatography)",
    "MRA Brain",
    "MRA Neck",
    # X-ray
    "X-ray Chest PA and Lateral",
    "X-ray Chest Portable AP",
    "X-ray Abdomen Supine",
    "X-ray Abdomen Upright",
    "X-ray Hand Right",
    "X-ray Hand Left",
    "X-ray Foot Right",
    "X-ray Foot Left",
    "X-ray Ankle Right",
    "X-ray Ankle Left",
    "X-ray Cervical Spine",
    "X-ray Thoracic Spine",
    "X-ray Lumbar Spine",
    "X-ray Pelvis",
    "X-ray Shoulder Right",
    "X-ray Shoulder Left",
    # Ultrasound
    "Ultrasound Abdomen Complete",
    "Ultrasound Pelvis Transabdominal",
    "Ultrasound Pelvis Transvaginal",
    "Ultrasound Thyroid",
    "Ultrasound Scrotum",
    "Ultrasound Renal",
    "Ultrasound Carotid Doppler",
    "Ultrasound Lower Extremity Venous Doppler",
    "Ultrasound Gallbladder (RUQ)",
    # Other Modalities
    "Mammogram Screening Bilateral",
    "Mammogram Diagnostic Unilateral",
    "DEXA Scan Lumbar Spine and Hip",
    "PET-CT Whole Body",
    "Nuclear Medicine Bone Scan",
    "Fluoroscopy Barium Swallow",
    "Fluoroscopy VCUG (Voiding Cystourethrogram)",
]


class StudyFactory(factory.Factory):
    class Meta:
        model = Study

    name = Faker("random_element", elements=radiology_studies)
    created_at = Faker("date_time_this_year")


class StudyTemplateFactory(factory.Factory):
    class Meta:
        model = StudyTemplate

    section_names = ["History", "Findings", "Impression"]


class ReportFactory(factory.Factory):
    class Meta:
        model = Report

    prompt_text = Faker("text", max_nb_chars=200)
    result_text = Faker("text", max_nb_chars=500)
    status = Faker(
        "random_element",
        elements=[
            ReportStatus.draft.value,
            ReportStatus.preliminary.value,
            ReportStatus.signed.value,
            ReportStatus.signed_with_addendum.value,
        ],
    )


class ReportHistoryFactory(factory.Factory):
    class Meta:
        model = ReportHistory

    timestamp = Faker("date_time_this_year")
    status = Faker(
        "random_element",
        elements=[
            ReportStatus.draft.value,
            ReportStatus.preliminary.value,
            ReportStatus.signed.value,
            ReportStatus.signed_with_addendum.value,
        ],
    )
    result_text = Faker("text", max_nb_chars=500)


class ReportEventFactory(factory.Factory):
    class Meta:
        model = ReportEvent

    event_type = Faker(
        "random_element", elements=["created", "updated", "signed", "reviewed"]
    )
    timestamp = Faker("date_time_this_year")
    details = Faker("text", max_nb_chars=100)


async def create_fake_data():
    await db.start_session()

    try:
        organizations = []
        for _ in range(5):
            org = OrganizationFactory()
            db.session.add(org)
            organizations.append(org)

        await db.session.commit()

        users = []
        for _ in range(20):
            user = UserFactory()
            user.organization_id = random.choice(organizations).id
            user.set_password("password123")
            db.session.add(user)
            users.append(user)

        await db.session.commit()

        studies = []
        for _ in range(10):
            study = StudyFactory()
            db.session.add(study)
            studies.append(study)

        await db.session.commit()

        templates = []
        for _ in range(15):
            template = StudyTemplateFactory()
            template.study_id = random.choice(studies).id
            db.session.add(template)
            templates.append(template)

        await db.session.commit()

        reports = []
        for _ in range(50):
            report = ReportFactory()
            report.study_id = random.choice(studies).id
            report.template_id = random.choice(templates).id
            report.user_id = random.choice(users).id
            db.session.add(report)
            reports.append(report)

        await db.session.commit()

        for _ in range(100):
            history = ReportHistoryFactory()
            history.report_id = random.choice(reports).id
            db.session.add(history)

        for _ in range(80):
            event = ReportEventFactory()
            event.report_id = random.choice(reports).id
            db.session.add(event)

        await db.session.commit()

        print("Fake data created successfully!")
        print(
            f"Created: {len(organizations)} organizations, {len(users)} users, {len(studies)} studies"
        )
        print(f"Created: {len(templates)} templates, {len(reports)} reports")
        print("Created: 100 report histories, 80 report events")

    except Exception as e:
        await db.session.rollback()
        print(f"Error creating fake data: {e}")
        raise
    finally:
        await db.close_session()


if __name__ == "__main__":
    asyncio.run(create_fake_data())
