"""Demo script showing how to use the LoanAI system."""

import asyncio
from datetime import datetime

from loanai_agent.main import LoanApplicationProcessor
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
from loanai_agent.utils import get_logger

logger = get_logger(__name__)


def create_sample_application() -> LoanApplication:
    """Create a sample loan application for demonstration."""
    
    # Create personal information
    personal_info = PersonalInfo(
        first_name="John",
        last_name="Doe",
        personal_id="123456789",
        gender=Gender.MALE,
        birth_year="1990",
        phone="+1-555-123-4567",
        address="123 Main Street, San Francisco, CA 94102",
    )

    # Create education information
    education = Education(
        education_level=EducationLevel.BACHELOR,
        university="Stanford University",
    )

    # Create employment information
    employment = Employment(
        employment_status=EmploymentStatus.EMPLOYED,
        company_name="Tech Solutions Inc.",
        monthly_salary=5500.00,
        experience_years=5,
    )

    # Create loan request
    loan_request = LoanRequest(
        loan_purpose=LoanPurpose.PERSONAL,
        loan_duration=24,  # 2 years
        loan_amount=25000.00,
        additional_info="Need funds for home renovation",
    )

    # Create document information
    documents = [
        DocumentInfo(
            document_type=DocumentType.BANK_STATEMENT,
            file_name="bank_statement_jan_2024.pdf",
            file_path="gs://loanai-documents/bank_statements/john_doe_jan_2024.pdf",
            file_size=256000,
            mime_type="application/pdf",
            uploaded_at=datetime.now(),
        ),
        DocumentInfo(
            document_type=DocumentType.SALARY_STATEMENT,
            file_name="salary_slip_jan_2024.pdf",
            file_path="gs://loanai-documents/salary_statements/john_doe_jan_2024.pdf",
            file_size=128000,
            mime_type="application/pdf",
            uploaded_at=datetime.now(),
        ),
    ]

    # Create complete application
    application = LoanApplication(
        customer_id="cust-001-2024",
        personal_info=personal_info,
        education=education,
        employment=employment,
        loan_request=loan_request,
        documents=documents,
    )

    return application


async def run_demo():
    """Run the demo application."""
    logger.info("=" * 80)
    logger.info("LoanAI Multi-Agent System - Demo")
    logger.info("=" * 80)

    # Initialize processor
    processor = LoanApplicationProcessor()
    logger.info("✓ Loan Application Processor initialized")

    # Check system status
    status = processor.get_system_status()
    logger.info(f"System Status: {status}")
    logger.info(f"Active Agents: {', '.join(status['agents'])}")

    # Create sample application
    application = create_sample_application()
    logger.info("\n" + "=" * 80)
    logger.info("Loan Application Submitted")
    logger.info("=" * 80)
    logger.info(f"Customer ID: {application.customer_id}")
    logger.info(f"Name: {application.personal_info.first_name} {application.personal_info.last_name}")
    logger.info(f"Company: {application.employment.company_name}")
    logger.info(f"Monthly Salary: ${application.employment.monthly_salary:,.2f}")
    logger.info(f"Loan Amount Requested: ${application.loan_request.loan_amount:,.2f}")
    logger.info(f"Loan Duration: {application.loan_request.loan_duration} months")
    logger.info(f"Education: {application.education.education_level.value}")
    logger.info(f"University: {application.education.university}")

    # Process application
    logger.info("\n" + "=" * 80)
    logger.info("Processing Application Through Multi-Agent System...")
    logger.info("=" * 80)

    try:
        decision = await processor.process(application)

        # Display results
        logger.info("\n" + "=" * 80)
        logger.info("FINAL DECISION")
        logger.info("=" * 80)
        logger.info(f"Decision: {decision.decision}")
        logger.info(f"Confidence Score: {decision.confidence_score:.2%}")
        logger.info(f"Risk Score: {decision.risk_score}/100")

        if decision.loan_amount:
            logger.info(f"\nApproved Loan Terms:")
            logger.info(f"  - Loan Amount: ${decision.loan_amount:,.2f}")
            logger.info(f"  - Interest Rate: {decision.interest_rate:.2f}%")
            logger.info(f"  - Duration: {decision.loan_duration} months")
            if decision.detailed_report.get("loan_terms"):
                monthly_payment = decision.detailed_report["loan_terms"].get("monthly_payment", 0)
                logger.info(f"  - Monthly Payment: ${monthly_payment:,.2f}")

        logger.info(f"\nDecision Reasoning:")
        logger.info(decision.reasoning)

        if decision.conditions:
            logger.info(f"\nLoan Conditions:")
            for i, condition in enumerate(decision.conditions, 1):
                logger.info(f"  {i}. {condition}")

        # Display detailed analysis
        logger.info("\n" + "=" * 80)
        logger.info("DETAILED ANALYSIS SUMMARY")
        logger.info("=" * 80)

        # Helper function to get values from Pydantic models or dicts
        def get_value(obj, key, default=None):
            if obj is None:
                return default
            if isinstance(obj, dict):
                return obj.get(key, default)
            else:
                return getattr(obj, key, default)

        if decision.bank_analysis:
            logger.info(f"\nBank Statement Analysis:")
            logger.info(f"  - Confidence: {get_value(decision.bank_analysis, 'confidence_score', 0):.2%}")
            logger.info(
                f"  - Average Monthly Income: ${get_value(decision.bank_analysis, 'average_monthly_income', 0):,.2f}"
            )
            logger.info(
                f"  - Average Monthly Balance: ${get_value(decision.bank_analysis, 'average_monthly_balance', 0):,.2f}"
            )
            logger.info(
                f"  - Recommendation: {get_value(decision.bank_analysis, 'recommendation', 'N/A')}"
            )

        if decision.salary_analysis:
            logger.info(f"\nSalary Statement Analysis:")
            logger.info(f"  - Confidence: {get_value(decision.salary_analysis, 'confidence_score', 0):.2%}")
            logger.info(
                f"  - Employer: {get_value(decision.salary_analysis, 'employer_name', 'N/A')}"
            )
            logger.info(
                f"  - Gross Salary: ${get_value(decision.salary_analysis, 'gross_salary', 0):,.2f}"
            )
            logger.info(
                f"  - Matches Self-Reported: {get_value(decision.salary_analysis, 'matches_self_reported', False)}"
            )
            logger.info(
                f"  - Recommendation: {get_value(decision.salary_analysis, 'recommendation', 'N/A')}"
            )

        if decision.verification_analysis:
            logger.info(f"\nExternal Verification Analysis:")
            logger.info(f"  - Confidence: {get_value(decision.verification_analysis, 'confidence_score', 0):.2%}")
            uni_data = get_value(decision.verification_analysis, 'university_verification', {})
            if isinstance(uni_data, dict):
                uni_name = uni_data.get('name', 'N/A')
            else:
                uni_name = getattr(uni_data, 'name', 'N/A')
            logger.info(f"  - University: {uni_name}")
            
            company_data = get_value(decision.verification_analysis, 'company_verification', {})
            if isinstance(company_data, dict):
                company_name = company_data.get('name', 'N/A')
            else:
                company_name = getattr(company_data, 'name', 'N/A')
            logger.info(f"  - Company: {company_name}")
            
            logger.info(
                f"  - Recommendation: {get_value(decision.verification_analysis, 'recommendation', 'N/A')}"
            )

        if decision.consensus:
            logger.info(f"\nAgent Consensus:")
            logger.info(
                f"  - Recommendation: {get_value(decision.consensus, 'overall_recommendation', 'N/A')}"
            )
            logger.info(f"  - Confidence: {get_value(decision.consensus, 'confidence_score', 0):.2%}")
            logger.info(
                f"  - Agents Agreement: {get_value(decision.consensus, 'agent_agreements', {})}"
            )

        logger.info("\n" + "=" * 80)
        logger.info("✓ Application Processing Complete")
        logger.info("=" * 80)

    except Exception as e:
        logger.error(f"Error processing application: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(run_demo())
