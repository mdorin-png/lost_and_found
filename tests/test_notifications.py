from app import app


def test_notifications_page():
    client = app.test_client()
    response = client.get("/notifications")
    assert response.status_code == 200
    assert b"Notifications" in response.data
