from fastapi import FastAPI, Depends, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from .database import engine, Base, get_db
from . import models
from .schemas import GenerationRequest
from .worker import process_job


app = FastAPI(
    title="Bulk Certificate Generator API"
)


Base.metadata.create_all(bind=engine)


@app.get("/")
def home():
    return {
        "message": "Bulk Certificate Generator API is running"
    }


@app.post("/jobs", status_code=202)
def create_job(
    request: GenerationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    # Create the job
    job = models.Job(
        status="PENDING",
        total=len(request.recipients)
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    # Create certificate records for each recipient
    for recipient in request.recipients:
        certificate = models.Certificate(
            job_id=job.id,
            recipient_name=recipient.name,
            recipient_email=recipient.email,
            status="PENDING"
        )

        db.add(certificate)

    db.commit()

    # Start certificate generation in the background
    background_tasks.add_task(
        process_job,
        job.id,
        request.event_name,
        request.certificate_date
    )

    return {
        "job_id": job.id,
        "status": job.status,
        "total": job.total
    }


@app.get("/jobs/{job_id}")
def get_job_status(
    job_id: int,
    db: Session = Depends(get_db)
):
    job = db.query(models.Job).filter(
        models.Job.id == job_id
    ).first()

    if not job:
        return {
            "error": "Job not found"
        }

    processed = job.successful + job.failed

    progress = 0

    if job.total > 0:
        progress = (processed / job.total) * 100

    return {
        "job_id": job.id,
        "status": job.status,
        "total": job.total,
        "successful": job.successful,
        "failed": job.failed,
        "progress": f"{progress:.0f}%"
    }


@app.get("/jobs/{job_id}/certificates")
def get_job_certificates(
    job_id: int,
    db: Session = Depends(get_db)
):
    job = db.query(models.Job).filter(
        models.Job.id == job_id
    ).first()

    if not job:
        return {
            "error": "Job not found"
        }

    certificates = db.query(models.Certificate).filter(
        models.Certificate.job_id == job_id
    ).all()

    return [
        {
            "certificate_id": certificate.id,
            "recipient_name": certificate.recipient_name,
            "recipient_email": certificate.recipient_email,
            "status": certificate.status,
            "file_path": certificate.file_path,
            "error_message": certificate.error_message
        }
        for certificate in certificates
    ]


@app.get("/certificates/{certificate_id}")
def get_certificate(
    certificate_id: int,
    db: Session = Depends(get_db)
):
    certificate = db.query(models.Certificate).filter(
        models.Certificate.id == certificate_id
    ).first()

    if not certificate:
        return {
            "error": "Certificate not found"
        }

    if certificate.status != "SUCCESS":
        return {
            "error": "Certificate has not been generated successfully"
        }

    if not certificate.file_path:
        return {
            "error": "Certificate file not found"
        }

    return FileResponse(
        path=certificate.file_path,
        media_type="application/pdf",
        filename=f"certificate_{certificate.id}.pdf"
    )