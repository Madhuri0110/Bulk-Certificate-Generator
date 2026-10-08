# Bulk Certificate Generator

A FastAPI-based backend service for generating certificates in bulk from a predefined PDF template.

## Features

- Create bulk certificate generation jobs
- Validate recipient names and email addresses
- Generate individual PDF certificates
- Process certificates in the background
- Track job progress
- Handle individual certificate failures without stopping the entire job
- Retrieve certificates belonging to a job
- Download individual generated certificates
- Automated tests using pytest

## Technology Stack

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- ReportLab
- pytest
- HTTPX

## Project Structure

```text
bulk-certificate-generator/
│
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── generator.py
│   └── worker.py
│
├── generated/
│   └── Generated PDF certificates
│
├── test_api.py
├── certificates.db
├── requirements.txt
├── README.md
└── venv/