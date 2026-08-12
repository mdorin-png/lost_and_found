from flask import Flask
from pathlib import Path

from controllers.general_controller import controller
from repositories.repository_clerk import RepositoryClerk
from services.claim_service import ClaimService
from services.notification_service import NotificationService
from services.report_service import ReportService

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "database" / "lost_and_found.sqlite"

app = Flask(__name__)
app.config["SECRET_KEY"] = "lost-and-found-development-key"

repository = RepositoryClerk(DATABASE_PATH)
repository.initialize()

notification_service = NotificationService(repository)
report_service = ReportService(repository, notification_service)
claim_service = ClaimService(repository, notification_service)

controller.configure(report_service, claim_service, notification_service)

app.register_blueprint(controller)


if __name__ == "__main__":
    app.run(debug=True)
