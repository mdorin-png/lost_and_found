class ClaimService:
    def __init__(self, repository, notification_service):
        self.repository = repository
        self.notification_service = notification_service

    def create_claim(
        self,
        student_name: str,
        contact: str,
        found_report_id: int,
        identifying_information: str,
    ) -> int:
        found_report = self.repository.get_found_report(found_report_id)

        if found_report is None:
            raise ValueError("The selected found item does not exist.")

        if found_report["status"] != "open":
            raise ValueError("This found item is no longer available to claim.")

        student_id = self.repository.create_student(student_name, contact)

        claim_id = self.repository.create_claim(
            student_id,
            found_report_id,
            identifying_information,
        )

        self.notification_service.create_notification(
            found_report["finder_id"],
            f"A claim has been submitted for your found item: "
            f"{found_report['description']}.",
        )

        return claim_id
