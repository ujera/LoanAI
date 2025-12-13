"""Test fixtures and configuration for pytest."""

import pytest
from loanai_agent.models import (
    DocumentInfo,
    DocumentType,
    Education,
    EducationLevel,
    Employment,
    EmploymentStatus,
    Gender,
    LoanApplication,
    LoanPurpose,
    LoanRequest,
    PersonalInfo,
)


@pytest.fixture
def sample_personal_info():
    """Create sample personal information."""
    return PersonalInfo(
        first_name="Jane",
        last_name="Smith",
        personal_id="987654321",
        gender=Gender.FEMALE,
        birth_year="1992",
        phone="+1-555-987-6543",
        address="456 Oak Avenue, New York, NY 10001",
    )


@pytest.fixture
def sample_education():
    """Create sample education information."""
    return Education(
        education_level=EducationLevel.MASTER,
        university="Harvard University",
    )


@pytest.fixture
def sample_employment():
    """Create sample employment information."""
    return Employment(
        employment_status=EmploymentStatus.EMPLOYED,
        company_name="Google LLC",
        monthly_salary=8000.00,
        experience_years=6,
    )


@pytest.fixture
def sample_loan_request():
    """Create sample loan request."""
    return LoanRequest(
        loan_purpose=LoanPurpose.MORTGAGE,
        loan_duration=240,  # 20 years
        loan_amount=500000.00,
        additional_info="Home purchase in San Francisco",
    )


@pytest.fixture
def sample_documents():
    """Create sample documents."""
    from datetime import datetime
    
    return [
        DocumentInfo(
            document_type=DocumentType.BANK_STATEMENT,
            file_name="bank_statement.pdf",
            file_path="gs://loanai/bank_statement.pdf",
            file_size=256000,
            mime_type="application/pdf",
            uploaded_at=datetime.now(),
        ),
        DocumentInfo(
            document_type=DocumentType.SALARY_STATEMENT,
            file_name="salary_statement.pdf",
            file_path="gs://loanai/salary_statement.pdf",
            file_size=128000,
            mime_type="application/pdf",
            uploaded_at=datetime.now(),
        ),
    ]


@pytest.fixture
def sample_application(sample_personal_info, sample_education, sample_employment, sample_loan_request, sample_documents):
    """Create a complete sample application."""
    return LoanApplication(
        customer_id="test-cust-001",
        personal_info=sample_personal_info,
        education=sample_education,
        employment=sample_employment,
        loan_request=sample_loan_request,
        documents=sample_documents,
    )
