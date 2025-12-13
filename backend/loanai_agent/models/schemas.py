"""Data models and schemas for loan application processing."""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


# ==================== Enum Types ====================


class EmploymentStatus(str, Enum):
    """Employment status options."""

    EMPLOYED = "employed"
    SELF_EMPLOYED = "self_employed"
    UNEMPLOYED = "unemployed"


class EducationLevel(str, Enum):
    """Education level options."""

    HIGH_SCHOOL = "high_school"
    BACHELOR = "bachelor"
    MASTER = "master"
    PHD = "phd"


class Gender(str, Enum):
    """Gender options."""

    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class LoanPurpose(str, Enum):
    """Loan purpose options."""

    MORTGAGE = "mortgage"
    VEHICLE = "vehicle"
    PERSONAL = "personal"
    EDUCATION = "education"
    BUSINESS = "business"
    OTHERS = "others"


class DocumentType(str, Enum):
    """Document type options."""

    BANK_STATEMENT = "bank_statement"
    SALARY_STATEMENT = "salary_statement"


# ==================== Personal Information ====================


class PersonalInfo(BaseModel):
    """Customer personal information."""

    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    personal_id: str = Field(..., min_length=1, max_length=50)
    gender: Gender
    birth_year: str = Field(..., min_length=4, max_length=4)
    phone: str = Field(..., min_length=10, max_length=20)
    address: str = Field(..., min_length=5, max_length=500)

    @field_validator("birth_year")
    @classmethod
    def validate_birth_year(cls, v: str) -> str:
        """Validate birth year is numeric and reasonable."""
        try:
            year = int(v)
            current_year = datetime.now().year
            if year < 1900 or year > current_year - 18:
                raise ValueError("Invalid birth year")
        except ValueError:
            raise ValueError("Birth year must be a valid 4-digit number")
        return v


# ==================== Education ====================


class Education(BaseModel):
    """Customer education information."""

    education_level: EducationLevel
    university: str = Field(..., min_length=1, max_length=200)


# ==================== Employment ====================


class Employment(BaseModel):
    """Customer employment information."""

    employment_status: EmploymentStatus
    company_name: Optional[str] = Field(None, max_length=200)
    monthly_salary: Optional[float] = Field(None, gt=0)
    experience_years: Optional[int] = Field(None, ge=0)

    @field_validator("company_name", "monthly_salary", "experience_years", mode="before")
    @classmethod
    def validate_employment_fields(cls, v: object, info) -> object:
        """Validate conditional employment fields."""
        employment_status = info.data.get("employment_status")
        field_name = info.field_name
        if employment_status != EmploymentStatus.UNEMPLOYED:
            if field_name in ["company_name", "monthly_salary", "experience_years"]:
                if v is None:
                    raise ValueError(
                        f"{field_name} is required for {employment_status} status"
                    )
        return v


# ==================== Loan Request ====================


class LoanRequest(BaseModel):
    """Loan request details."""

    loan_purpose: LoanPurpose
    loan_duration: int = Field(..., ge=1, le=360)  # in months
    loan_amount: float = Field(..., gt=0, le=10_000_000)
    additional_info: Optional[str] = Field(None, max_length=5000)


# ==================== Documents ====================


class DocumentInfo(BaseModel):
    """Document information."""

    document_type: DocumentType
    file_name: str = Field(..., min_length=1, max_length=255)
    file_path: str = Field(..., min_length=1, max_length=500)
    file_size: int = Field(..., gt=0)
    mime_type: str = Field(..., max_length=100)
    uploaded_at: datetime


# ==================== Loan Application ====================


class LoanApplication(BaseModel):
    """Complete loan application."""

    customer_id: str = Field(..., min_length=1, max_length=100)
    personal_info: PersonalInfo
    education: Education
    employment: Employment
    loan_request: LoanRequest
    documents: List[DocumentInfo] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    application_status: str = Field(default="pending")

    class Config:
        """Model configuration."""

        use_enum_values = True


# ==================== Agent Analysis Results ====================


class BankStatementAnalysis(BaseModel):
    """Bank statement analysis result."""

    agent_name: str = "bank_statement_agent"
    confidence_score: float = Field(default=0.0, ge=0, le=1)
    document_authenticity: str = "unknown"  # "verified", "suspicious", "rejected", "unknown"
    average_monthly_balance: float = 0.0
    average_monthly_income: float = 0.0
    income_consistency: str = "unknown"  # "high", "moderate", "low", "unknown"
    total_monthly_expenses: float = 0.0
    recurring_obligations: float = 0.0
    red_flags: List[str] = Field(default_factory=list)
    savings_behavior: str = "unknown"  # "positive", "neutral", "negative", "unknown"
    debt_indicators: dict = Field(default_factory=dict)
    recommendation: str = "review"  # "approve", "reject", "review"
    reasoning: str = "Analysis could not be completed"
    risk_score: int = Field(default=50, ge=0, le=100)
    error: Optional[str] = None


class SalaryStatementAnalysis(BaseModel):
    """Salary statement analysis result."""

    agent_name: str = "salary_statement_agent"
    confidence_score: float = Field(default=0.0, ge=0, le=1)
    document_authenticity: str = "unknown"  # "verified", "suspicious", "rejected", "unknown"
    employer_name: str = "unknown"
    employee_name: str = "unknown"
    employee_id: str = "unknown"
    gross_salary: float = 0.0
    net_salary: float = 0.0
    employment_duration_months: int = 0
    employment_period: str = "unknown"
    deductions: dict = Field(default_factory=dict)
    benefits: List[str] = Field(default_factory=list)
    matches_self_reported: bool = False
    salary_variance: float = 0.0
    employment_status_verified: bool = False
    recommendation: str = "review"  # "approve", "reject", "review"
    reasoning: str = "Analysis could not be completed"
    risk_score: int = Field(default=50, ge=0, le=100)
    error: Optional[str] = None


class VerificationAnalysis(BaseModel):
    """External verification analysis result."""

    agent_name: str = "verification_agent"
    confidence_score: float = Field(default=0.0, ge=0, le=1)
    university_verification: dict = Field(default_factory=dict)
    company_verification: dict = Field(default_factory=dict)
    address_verification: dict = Field(default_factory=dict)
    salary_benchmark: dict = Field(default_factory=dict)
    recommendation: str = "review"  # "approve", "reject", "review"
    reasoning: str = "Analysis could not be completed"
    risk_score: int = Field(default=50, ge=0, le=100)
    error: Optional[str] = None


class ConsensusResult(BaseModel):
    """Consensus between agents."""

    overall_recommendation: str  # "approve", "reject", "manual_review"
    confidence_score: float = Field(..., ge=0, le=1)
    risk_score: int = Field(..., ge=0, le=100)
    agent_agreements: dict = Field(default_factory=dict)
    disagreement_details: Optional[str] = None
    discussion_summary: str = ""


# ==================== Final Decision ====================


class DecisionResult(BaseModel):
    """Final loan decision result."""

    decision: str  # "APPROVED", "REJECTED", "MANUAL_REVIEW"
    confidence_score: float = Field(..., ge=0, le=1)
    risk_score: int = Field(..., ge=0, le=100)
    loan_amount: Optional[float] = None
    interest_rate: Optional[float] = None
    loan_duration: Optional[int] = None
    conditions: List[str] = Field(default_factory=list)
    reasoning: str
    detailed_report: dict = Field(default_factory=dict)
    bank_analysis: Optional[BankStatementAnalysis] = None
    salary_analysis: Optional[SalaryStatementAnalysis] = None
    verification_analysis: Optional[VerificationAnalysis] = None
    consensus: Optional[ConsensusResult] = None
    decision_timestamp: datetime = Field(default_factory=datetime.now)
    decision_officer: str = "loan_officer_agent"

    class Config:
        """Model configuration."""

        use_enum_values = True
