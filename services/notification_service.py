class NotificationService:
    def __init__(self, repository):
        self.repository = repository

    def create_notification(self, student_id: int, message: str) -> int:
        return self.repository.create_notification(student_id, message)

    def get_notifications(self, student_id: int):
        return self.repository.get_notifications(student_id)

    def mark_as_read(self, notification_id: int) -> None:
        self.repository.mark_notification_read(notification_id)
