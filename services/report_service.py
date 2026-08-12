class ReportService:
    def __init__(self, repository, notification_service):
        self.repository = repository
        self.notification_service = notification_service

    def create_lost_report(
        self,
        student_name: str,
        contact: str,
        description: str,
        category: str,
        location: str,
    ) -> dict:
        student_id = self.repository.create_student(student_name, contact)
        item_id = self.repository.create_item(description, category)
        location_id = self.repository.create_location(location)

        report_id = self.repository.create_lost_report(
            student_id, item_id, location_id
        )

        return {"id": report_id, "student_id": student_id}

    def create_found_report(
        self,
        student_name: str,
        contact: str,
        description: str,
        category: str,
        location: str,
    ) -> dict:
        student_id = self.repository.create_student(student_name, contact)
        item_id = self.repository.create_item(description, category)
        location_id = self.repository.create_location(location)

        report_id = self.repository.create_found_report(
            student_id, item_id, location_id
        )

        matches = self.repository.get_lost_reports_for_matching(
            description, category, location
        )

        for match in matches:
            self.notification_service.create_notification(
                match["student_id"],
                (
                    f"A found item may match your lost report: "
                    f"{description} at {location}."
                ),
            )

        return {
            "id": report_id,
            "student_id": student_id,
            "match_count": len(matches),
        }

    def search_found_reports(
        self,
        description: str = "",
        category: str = "",
        location: str = "",
    ):
        return self.repository.search_found_reports(
            description, category, location
        )
