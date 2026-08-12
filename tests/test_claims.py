from app import app


def test_claim_missing_report():
    client = app.test_client()
    response = client.get("/claim/999999")
    assert response.status_code == 302
