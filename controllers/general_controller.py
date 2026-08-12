from flask import Blueprint, flash, redirect, render_template, request, url_for


controller = Blueprint("controller", __name__)

_report_service = None
_claim_service = None
_notification_service = None


def configure(report_service, claim_service, notification_service):
    global _report_service, _claim_service, _notification_service
    _report_service = report_service
    _claim_service = claim_service
    _notification_service = notification_service


def _require_fields(data, fields):
    missing = [field for field in fields if not data.get(field, "").strip()]
    return missing


@controller.get("/")
def index():
    return render_template("index.html")


@controller.route("/report/lost", methods=["GET", "POST"])
def report_lost():
    if request.method == "POST":
        data = request.form
        required = ["student_name", "contact", "description", "category", "location"]
        missing = _require_fields(data, required)

        if missing:
            flash("Please complete all required fields.", "error")
            return render_template("report_lost.html", form=data)

        result = _report_service.create_lost_report(
            student_name=data["student_name"].strip(),
            contact=data["contact"].strip(),
            description=data["description"].strip(),
            category=data["category"].strip(),
            location=data["location"].strip(),
        )

        flash(
            f"Lost-item report #{result['id']} was submitted.",
            "success",
        )
        return redirect(url_for("controller.index"))

    return render_template("report_lost.html", form={})


@controller.route("/report/found", methods=["GET", "POST"])
def report_found():
    if request.method == "POST":
        data = request.form
        required = ["student_name", "contact", "description", "category", "location"]
        missing = _require_fields(data, required)

        if missing:
            flash("Please complete all required fields.", "error")
            return render_template("report_found.html", form=data)

        result = _report_service.create_found_report(
            student_name=data["student_name"].strip(),
            contact=data["contact"].strip(),
            description=data["description"].strip(),
            category=data["category"].strip(),
            location=data["location"].strip(),
        )

        if result["match_count"]:
            flash(
                f"Found-item report #{result['id']} submitted. "
                f"{result['match_count']} possible lost-item match(es) "
                "generated notifications.",
                "success",
            )
        else:
            flash(
                f"Found-item report #{result['id']} was submitted.",
                "success",
            )

        return redirect(url_for("controller.index"))

    return render_template("report_found.html", form={})


@controller.route("/search", methods=["GET", "POST"])
def search():
    data = request.form if request.method == "POST" else request.args

    results = _report_service.search_found_reports(
        description=data.get("description", "").strip(),
        category=data.get("category", "").strip(),
        location=data.get("location", "").strip(),
    )

    return render_template(
        "results.html",
        results=results,
        search={
            "description": data.get("description", ""),
            "category": data.get("category", ""),
            "location": data.get("location", ""),
        },
    )


@controller.route("/claim/<int:found_report_id>", methods=["GET", "POST"])
def claim(found_report_id):
    found_report = _claim_service.repository.get_found_report(found_report_id)

    if found_report is None:
        flash("Found item not found.", "error")
        return redirect(url_for("controller.search"))

    if request.method == "POST":
        data = request.form
        required = [
            "student_name",
            "contact",
            "identifying_information",
        ]
        missing = _require_fields(data, required)

        if missing:
            flash("Please complete all required fields.", "error")
            return render_template(
                "claim.html",
                found_report=found_report,
                form=data,
            )

        try:
            _claim_service.create_claim(
                student_name=data["student_name"].strip(),
                contact=data["contact"].strip(),
                found_report_id=found_report_id,
                identifying_information=data[
                    "identifying_information"
                ].strip(),
            )
        except ValueError as exc:
            flash(str(exc), "error")
            return render_template(
                "claim.html",
                found_report=found_report,
                form=data,
            )

        flash("Your claim was submitted for verification.", "success")
        return redirect(url_for("controller.search"))

    return render_template(
        "claim.html",
        found_report=found_report,
        form={},
    )


@controller.route("/notifications", methods=["GET", "POST"])
def notifications():
    student_id = request.args.get("student_id", type=int)

    if student_id is None:
        return render_template("notifications.html", notifications=[], student_id=None)

    if request.method == "POST":
        notification_id = request.form.get("notification_id", type=int)
        if notification_id:
            _notification_service.mark_as_read(notification_id)

    return render_template(
        "notifications.html",
        notifications=_notification_service.get_notifications(student_id),
        student_id=student_id,
    )
