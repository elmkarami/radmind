from datetime import datetime
from typing import Any, List, Optional

from sqlalchemy import or_, select
from sqlalchemy.orm import joinedload

from src.db import db
from src.db.models.report import (
    Report,
    ReportEvent,
    ReportHistory,
    Study,
    StudyTemplate,
)
from src.utils.pagination import Connection, paginate


async def get_all_studies() -> List[Study]:
    stmt = select(Study)
    result = await db.session.execute(stmt)
    return result.scalars().all()


async def get_studies_paginated(
    first: Optional[int] = None,
    after: Optional[str] = None,
    last: Optional[int] = None,
    before: Optional[str] = None,
    filter: Optional[dict] = None,
) -> Connection[Study]:
    # Build filter conditions
    filters = []
    if filter:
        if filter.get("categories"):
            # Filter studies that have any of the specified categories
            categories_filter = filter["categories"]
            # Check if study.categories array contains any of the specified categories
            category_conditions = []
            for category in categories_filter:
                category_conditions.append(Study.categories.contains([category]))
            if category_conditions:
                filters.append(or_(*category_conditions))

    return await paginate(
        model=Study,
        first=first,
        after=after,
        last=last,
        before=before,
        filters=filters if filters else None,
    )


async def get_study_by_id(study_id: int) -> Optional[Study]:
    stmt = select(Study).where(Study.id == study_id)
    result = await db.session.execute(stmt)
    return result.scalar_one_or_none()


async def create_study(study_data: dict) -> Study:
    study = Study(**study_data)
    db.session.add(study)
    await db.session.commit()
    await db.session.refresh(study)
    return study


async def update_study(study_id: int, study_data: dict) -> Optional[Study]:
    stmt = select(Study).where(Study.id == study_id)
    result = await db.session.execute(stmt)
    study = result.scalar_one_or_none()
    if study:
        for key, value in study_data.items():
            setattr(study, key, value)
        await db.session.commit()
        await db.session.refresh(study)
    return study


async def delete_study(study_id: int) -> bool:
    stmt = select(Study).where(Study.id == study_id)
    result = await db.session.execute(stmt)
    study = result.scalar_one_or_none()
    if study:
        await db.session.delete(study)
        await db.session.commit()
        return True
    return False


async def get_templates_by_study_id(study_id: int) -> List[StudyTemplate]:
    stmt = select(StudyTemplate).where(StudyTemplate.study_id == study_id)
    result = await db.session.execute(stmt)
    return result.scalars().all()


async def get_template_by_id(template_id: int) -> Optional[StudyTemplate]:
    stmt = select(StudyTemplate).where(StudyTemplate.id == template_id)
    result = await db.session.execute(stmt)
    return result.scalar_one_or_none()


async def get_all_reports() -> List[Report]:
    stmt = select(Report)
    result = await db.session.execute(stmt)
    return result.scalars().all()


async def get_reports_paginated(
    first: Optional[int] = None,
    after: Optional[str] = None,
    last: Optional[int] = None,
    before: Optional[str] = None,
    filter: Optional[dict] = None,
) -> Connection[Report]:
    # Build filter conditions
    filters = []
    if filter:
        if filter.get("studyId"):
            filters.append(Report.study_id == int(filter["studyId"]))

        if filter.get("templateId"):
            filters.append(Report.template_id == int(filter["templateId"]))

        if filter.get("studyCategories"):
            # Filter reports whose study has any of the specified categories
            categories_filter = filter["studyCategories"]

            # We need to join with Study table to filter by study categories

            # For this type of filtering, we'll use a subquery approach
            study_subquery = select(Study.id).where(
                or_(
                    *[
                        Study.categories.contains([category])
                        for category in categories_filter
                    ]
                )
            )
            filters.append(Report.study_id.in_(study_subquery))

    return await paginate(
        model=Report,
        first=first,
        after=after,
        last=last,
        before=before,
        filters=filters if filters else None,
    )


async def get_report_by_id(report_id: int) -> Optional[Report]:
    stmt = select(Report).where(Report.id == report_id)
    result = await db.session.execute(stmt)
    return result.scalar_one_or_none()


async def get_reports_by_study_id(study_id: int) -> List[Report]:
    stmt = select(Report).where(Report.study_id == study_id)
    result = await db.session.execute(stmt)
    return result.scalars().all()


async def get_reports_by_user_id(user_id: int) -> List[Report]:
    stmt = select(Report).where(Report.user_id == user_id)
    result = await db.session.execute(stmt)
    return result.scalars().all()


async def create_report(report_data: dict) -> Report:
    report = Report(**report_data)
    db.session.add(report)
    await db.session.commit()
    await db.session.refresh(report)
    return report


async def update_report(report_id: int, report_data: dict) -> Optional[Report]:
    stmt = select(Report).where(Report.id == report_id)
    result = await db.session.execute(stmt)
    report = result.scalar_one_or_none()
    if report:
        for key, value in report_data.items():
            setattr(report, key, value)
        # Set updated_at timestamp
        report.updated_at = datetime.now()
        await db.session.commit()
        await db.session.refresh(report)
    return report


async def delete_report(report_id: int) -> bool:
    stmt = select(Report).where(Report.id == report_id)
    result = await db.session.execute(stmt)
    report = result.scalar_one_or_none()
    if report:
        await db.session.delete(report)
        await db.session.commit()
        return True
    return False


async def get_report_history_by_report_id(report_id: int) -> List[ReportHistory]:
    stmt = select(ReportHistory).where(ReportHistory.report_id == report_id)
    result = await db.session.execute(stmt)
    return result.scalars().all()


async def get_report_events_by_report_id(report_id: int) -> List[ReportEvent]:
    stmt = select(ReportEvent).where(ReportEvent.report_id == report_id)
    result = await db.session.execute(stmt)
    return result.scalars().all()
