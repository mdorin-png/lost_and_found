from app import app


def test_search_page():
    client = app.test_client()
    response = client.get("/search")
    assert response.status_code == 200
    assert b"Found Item Search" in response.data
