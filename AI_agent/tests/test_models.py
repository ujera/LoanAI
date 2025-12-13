"""Tests for data models."""

import pytest
from loanai_agent.models import (
    EducationLevel,
    EmploymentStatus,
    Gender,
    LoanApplication,
    LoanPurpose,
    PersonalInfo,
)


def test_personal_info_valid():
    """Test creating valid personal information."""
    personal_info = PersonalInfo(
        first_name="John",
        last_name="Doe",
        personal_id="123456789",
        gender=Gender.MALE,
        birth_year="1990",
        phone="+1-555-1234",
        address="123 Main St",
    )
    assert personal_info.first_name == "John"
    assert personal_info.gender == Gender.MALE


def test_personal_info_invalid_birth_year():
    """Test that invalid birth year raises error."""
    with pytest.raises(ValueError):
        PersonalInfo(
            first_name="John",
            last_name="Doe",
            personal_id="123456789",
            gender=Gender.MALE,
            birth_year="2020",  # Too recent
            phone="+1-555-1234",
            address="123 Main St",
        )


def test_employment_conditional_fields():
    """Test that employment conditional fields are required when employed."""
    from loanai_agent.models import Employment
    
    # Should fail without company_name for employed
    with pytest.raises(ValueError):
        Employment(
            employment_status=EmploymentStatus.EMPLOYED,
            company_name=None,
            monthly_salary=5000,
            experience_years=5,
        )


def test_loan_application_creation(sample_application):
    """Test creating a complete loan application."""
    assert sample_application.customer_id == "test-cust-001"
    assert sample_application.personal_info.first_name == "Jane"
    assert sample_application.education.education_level == EducationLevel.MASTER
    assert sample_application.employment.monthly_salary == 8000.00
    assert sample_application.loan_request.loan_amount == 500000.00
    assert len(sample_application.documents) == 2


def test_loan_application_serialization(sample_application):
    """Test serializing loan application to dict."""
    app_dict = sample_application.dict()
    assert isinstance(app_dict, dict)
    assert app_dict["customer_id"] == "test-cust-001"
    assert "personal_info" in app_dict
    assert "loan_request" in app_dict
