import asyncio
import random

import factory
from factory import Faker

from src.db import db
from src.db.models.report import (Report, ReportEvent, ReportHistory,
                                  ReportStatus, Study, StudyTemplate)
from src.db.models.user import Organization, User, OrganizationMember, UserRole


class UserFactory(factory.Factory):
    class Meta:
        model = User

    first_name = Faker("first_name")
    last_name = Faker("last_name")
    email = Faker("email")
    phone_number = Faker("phone_number")
    password = "password123"  # Known password for testing
    password_must_change = False


class OrganizationFactory(factory.Factory):
    class Meta:
        model = Organization

    name = Faker("company")
    logo = Faker("image_url")
    address = Faker("address")
    phone_number = Faker("phone_number")


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


radiology_categories = [
    "CT", "MRI", "X-ray", "Ultrasound", "Mammogram", "DEXA", "PET-CT", 
    "Nuclear Medicine", "Fluoroscopy", "Interventional", "Emergency",
    "Pediatric", "Cardiac", "Neurological", "Orthopedic", "Abdominal"
]

class StudyFactory(factory.Factory):
    class Meta:
        model = Study

    name = Faker("random_element", elements=radiology_studies)
    created_at = Faker("date_time_this_year")
    
    @factory.lazy_attribute
    def categories(self):
        import random
        # Return 1-3 random categories for each study
        num_categories = random.randint(1, 3)
        return random.sample(radiology_categories, num_categories)


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
        # Create organizations with owners
        organizations = []
        owners = []
        
        for i in range(5):
            # Create owner user first
            owner = UserFactory(
                first_name=f"Owner{i+1}",
                last_name="Smith", 
                email=f"owner{i+1}@clinic{i+1}.com"
            )
            owner.set_password("password123")  # Known password
            db.session.add(owner)
            owners.append(owner)
            
        await db.session.commit()
        for owner in owners:
            await db.session.refresh(owner)
            
        # Create organizations with created_by_user_id
        for i, owner in enumerate(owners):
            org = OrganizationFactory(
                name=f"Radiology Clinic {i+1}",
                created_by_user_id=owner.id
            )
            db.session.add(org)
            organizations.append(org)

        await db.session.commit()
        for org in organizations:
            await db.session.refresh(org)

        # Create organization memberships for owners
        for owner, org in zip(owners, organizations):
            membership = OrganizationMember(
                user_id=owner.id,
                organization_id=org.id,
                role=UserRole.OWNER.value
            )
            db.session.add(membership)

        await db.session.commit()

        # Create radiologist users and memberships
        radiologists = []
        for i in range(15):  # 3 radiologists per organization on average
            radiologist = UserFactory(
                first_name=f"Dr.{i+1}",
                last_name="Radiologist",
                email=f"radiologist{i+1}@example.com"
            )
            radiologist.set_password("password123")  # Known password
            db.session.add(radiologist)
            radiologists.append(radiologist)

        await db.session.commit()
        for radiologist in radiologists:
            await db.session.refresh(radiologist)

        # Create radiologist memberships
        for radiologist in radiologists:
            org = random.choice(organizations)
            membership = OrganizationMember(
                user_id=radiologist.id,
                organization_id=org.id,
                role=UserRole.RADIOLOGIST.value
            )
            db.session.add(membership)

        await db.session.commit()

        # Create studies
        studies = []
        for _ in range(10):
            study = StudyFactory()
            db.session.add(study)
            studies.append(study)

        await db.session.commit()

        # Create templates
        templates = []
        for _ in range(15):
            template = StudyTemplateFactory()
            template.study_id = random.choice(studies).id
            db.session.add(template)
            templates.append(template)

        await db.session.commit()

        # Create reports (only radiologists can create reports)
        all_users = owners + radiologists
        reports = []
        for _ in range(50):
            report = ReportFactory()
            report.study_id = random.choice(studies).id
            report.template_id = random.choice(templates).id
            report.user_id = random.choice(all_users).id
            db.session.add(report)
            reports.append(report)

        await db.session.commit()

        # Create report histories
        for _ in range(100):
            history = ReportHistoryFactory()
            history.report_id = random.choice(reports).id
            db.session.add(history)

        # Create report events
        for _ in range(80):
            event = ReportEventFactory()
            event.report_id = random.choice(reports).id
            db.session.add(event)

        await db.session.commit()

        print("Fake data created successfully!")
        print(f"Created: {len(organizations)} organizations")
        print(f"Created: {len(owners)} owners, {len(radiologists)} radiologists")
        print(f"Created: {len(studies)} studies, {len(templates)} templates")
        print(f"Created: {len(reports)} reports")
        print("Created: 100 report histories, 80 report events")
        print("\n--- LOGIN CREDENTIALS ---")
        print("All users have password: 'password123'")
        print("\nOwner accounts:")
        for i in range(5):
            print(f"  - owner{i+1}@clinic{i+1}.com (Owner of Radiology Clinic {i+1})")
        print("\nRadiologist accounts:")
        for i in range(15):
            print(f"  - radiologist{i+1}@example.com (Radiologist)")

    except Exception as e:
        await db.session.rollback()
        print(f"Error creating fake data: {e}")
        raise
    finally:
        await db.close_session()


if __name__ == "__main__":
    asyncio.run(create_fake_data())
