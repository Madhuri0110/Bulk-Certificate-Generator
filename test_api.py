from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.generator import generate_certificate
from app.worker import process_job


client = TestClient(app)


def test_create_job():
    response = client.post(
        "/jobs",
        json={
            "event_name": "Python Workshop 2026",
            "certificate_date": "2026-10-08",
            "recipients": [
                {
                    "name": "Madhuri",
                    "email": "madhuri@example.com"
                },
                {
                    "name": "Rahul",
                    "email": "rahul@example.com"
                }
            ]
        }
    )

    assert response.status_code == 202

    data = response.json()

    assert "job_id" in data
    assert data["total"] == 2


def test_invalid_email():
    response = client.post(
        "/jobs",
        json={
            "event_name": "Python Workshop 2026",
            "certificate_date": "2026-10-08",
            "recipients": [
                {
                    "name": "Madhuri",
                    "email": "not-an-email"
                }
            ]
        }
    )

    assert response.status_code == 422


def test_certificate_generation():
    file_path = generate_certificate(
        certificate_id=9999,
        recipient_name="Test User",
        event_name="Python Workshop 2026",
        certificate_date="2026-10-08"
    )

    assert Path(file_path).exists()

    # Delete the test PDF after checking it was created
    Path(file_path).unlink()


def test_job_progress():
    response = client.post(
        "/jobs",
        json={
            "event_name": "Python Workshop 2026",
            "certificate_date": "2026-10-08",
            "recipients": [
                {
                    "name": "Madhuri",
                    "email": "madhuri@example.com"
                },
                {
                    "name": "Rahul",
                    "email": "rahul@example.com"
                }
            ]
        }
    )

    assert response.status_code == 202

    job_id = response.json()["job_id"]

    status_response = client.get(
        f"/jobs/{job_id}"
    )

    assert status_response.status_code == 200

    data = status_response.json()

    assert data["status"] == "COMPLETED"
    assert data["total"] == 2
    assert data["successful"] == 2
    assert data["failed"] == 0
    assert data["progress"] == "100%"


def test_individual_certificate_failure(monkeypatch):
    response = client.post(
        "/jobs",
        json={
            "event_name": "Python Workshop 2026",
            "certificate_date": "2026-10-08",
            "recipients": [
                {
                    "name": "Good User",
                    "email": "good@example.com"
                },
                {
                    "name": "Bad User",
                    "email": "bad@example.com"
                }
            ]
        }
    )

    assert response.status_code == 202

    job_id = response.json()["job_id"]

    # Import the worker module
    from app import worker

    # Save the original certificate generator
    original_generate = worker.generate_certificate

    # Create a fake generator for this test
    def fake_generate_certificate(
        certificate_id,
        recipient_name,
        event_name,
        certificate_date
    ):
        # Intentionally fail for one recipient
        if recipient_name == "Bad User":
            raise Exception(
                "Simulated certificate generation failure"
            )

        # Generate normally for the other recipient
        return original_generate(
            certificate_id,
            recipient_name,
            event_name,
            certificate_date
        )

    # Replace the real generator with our fake one
    monkeypatch.setattr(
        worker,
        "generate_certificate",
        fake_generate_certificate
    )

    # Run the worker
    process_job(
        job_id=job_id,
        event_name="Python Workshop 2026",
        certificate_date="2026-10-08"
    )

    # Get certificate results
    certificates_response = client.get(
        f"/jobs/{job_id}/certificates"
    )

    assert certificates_response.status_code == 200

    certificates = certificates_response.json()

    assert len(certificates) == 2

    # Find the successful certificate
    good_certificate = next(
        certificate
        for certificate in certificates
        if certificate["recipient_name"] == "Good User"
    )

    # Find the failed certificate
    bad_certificate = next(
        certificate
        for certificate in certificates
        if certificate["recipient_name"] == "Bad User"
    )

    # Good certificate should succeed
    assert good_certificate["status"] == "SUCCESS"

    # Bad certificate should fail
    assert bad_certificate["status"] == "FAILED"

    # The failure reason should be recorded
    assert "Simulated certificate generation failure" in (
        bad_certificate["error_message"]
    )