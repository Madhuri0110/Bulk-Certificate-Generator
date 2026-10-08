from sqlalchemy.orm import Session

from .database import SessionLocal
from .models import Job, Certificate
from .generator import generate_certificate


def process_job(job_id: int, event_name: str, certificate_date: str):
    db: Session = SessionLocal()

    try:
        job = db.query(Job).filter(Job.id == job_id).first()

        if not job:
            return

        job.status = "PROCESSING"
        db.commit()

        certificates = (
            db.query(Certificate)
            .filter(Certificate.job_id == job_id)
            .all()
        )

        for certificate in certificates:
            try:
                file_path = generate_certificate(
                    certificate_id=certificate.id,
                    recipient_name=certificate.recipient_name,
                    event_name=event_name,
                    certificate_date=certificate_date
                )

                certificate.status = "SUCCESS"
                certificate.file_path = file_path

                job.successful += 1

            except Exception as error:
                certificate.status = "FAILED"
                certificate.error_message = str(error)

                job.failed += 1

            db.commit()

        if job.failed == 0:
            job.status = "COMPLETED"
        else:
            job.status = "COMPLETED_WITH_ERRORS"

        db.commit()

    finally:
        db.close()