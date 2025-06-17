from ariadne import EnumType

from src.db.models.report import ReportStatus

report_status_enum = EnumType(
    "ReportStatus",
    {
        "DRAFT": ReportStatus.draft.value,
        "PRELIMINARY": ReportStatus.preliminary.value,
        "SIGNED": ReportStatus.signed.value,
        "SIGNED_WITH_ADDENDUM": ReportStatus.signed_with_addendum.value,
    },
)
