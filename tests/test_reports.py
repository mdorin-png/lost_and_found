from pathlib import Path

from app import app


def test_lost_report_page():
    client = app.test_client()
    response = client.get("/report/lost")
    assert response.status_code == 200
    assert b"Report a Lost Item" in response.data


def test_found_report_page():
    client = app.test_client()
    response = client.get("/report/found")
    assert response.status_code == 200
    assert b"Report a Found Item" in response.data
