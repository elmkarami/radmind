from src.db.dao import report_dao


class ReportService:
    @staticmethod
    async def get_all_studies():
        return await report_dao.get_all_studies()

    @staticmethod
    async def get_studies_paginated(first=None, after=None, last=None, before=None):
        return await report_dao.get_studies_paginated(first, after, last, before)

    @staticmethod
    async def get_study_by_id(study_id: int):
        return await report_dao.get_study_by_id(study_id)

    @staticmethod
    async def create_study(input_data: dict):
        # Validate required fields
        if not input_data.get("name") or not input_data.get("name").strip():
            raise ValueError("Study name is required")

        return await report_dao.create_study(input_data)

    @staticmethod
    async def update_study(study_id: int, input_data: dict):
        return await report_dao.update_study(study_id, input_data)

    @staticmethod
    async def delete_study(study_id: int):
        return await report_dao.delete_study(study_id)

    @staticmethod
    async def get_templates_by_study_id(study_id: int):
        return await report_dao.get_templates_by_study_id(study_id)

    @staticmethod
    async def get_template_by_id(template_id: int):
        return await report_dao.get_template_by_id(template_id)

    @staticmethod
    async def get_all_reports():
        return await report_dao.get_all_reports()

    @staticmethod
    async def get_reports_paginated(first=None, after=None, last=None, before=None):
        return await report_dao.get_reports_paginated(first, after, last, before)

    @staticmethod
    async def get_report_by_id(report_id: int):
        return await report_dao.get_report_by_id(report_id)

    @staticmethod
    async def get_reports_by_study_id(study_id: int):
        return await report_dao.get_reports_by_study_id(study_id)

    @staticmethod
    async def get_reports_by_user_id(user_id: int):
        return await report_dao.get_reports_by_user_id(user_id)

    @staticmethod
    async def create_report(input_data: dict):
        # Validate required fields
        if not input_data.get("studyId"):
            raise ValueError("Study ID is required")
        if not input_data.get("templateId"):
            raise ValueError("Template ID is required")
        if not input_data.get("userId"):
            raise ValueError("User ID is required")
        if not input_data.get("promptText") or not input_data.get("promptText").strip():
            raise ValueError("Prompt text is required")

        return await report_dao.create_report(input_data)

    @staticmethod
    async def update_report(report_id: int, input_data: dict):
        return await report_dao.update_report(report_id, input_data)

    @staticmethod
    async def delete_report(report_id: int):
        return await report_dao.delete_report(report_id)

    @staticmethod
    async def get_report_history_by_report_id(report_id: int):
        return await report_dao.get_report_history_by_report_id(report_id)

    @staticmethod
    async def get_report_events_by_report_id(report_id: int):
        return await report_dao.get_report_events_by_report_id(report_id)
