"""API usage examples and quick start guide."""

# ============================================================================
# LoanAI Multi-Agent System - Quick Start Guide
# ============================================================================

"""
This file demonstrates how to use the LoanAI multi-agent system for
loan application processing.

## Installation

1. Navigate to the backend directory:
   cd backend

2. Create a virtual environment:
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate

3. Install dependencies:
   pip install -r requirements.txt

4. Setup environment variables:
   cp .env.example .env
   # Edit .env with your credentials

## Running the Demo

python demo.py

## Using the System Programmatically

See examples below:
"""

import asyncio
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
from datetime import datetime


# ============================================================================
# Example 1: Basic Application Processing
# ============================================================================

async def example_basic_processing():
    """Basic example of processing a loan application."""
    
    # Initialize the processor
    processor = LoanApplicationProcessor()
    
    # Create application data
    personal_info = PersonalInfo(
        first_name="Alice",
        last_name="Johnson",
        personal_id="555123456",
        gender=Gender.FEMALE,
        birth_year="1988",
        phone="+1-555-555-5555",
        address="789 Pine Road, Los Angeles, CA 90001",
    )
    
    education = Education(
        education_level=EducationLevel.BACHELOR,
        university="UCLA",
    )
    
    employment = Employment(
        employment_status=EmploymentStatus.EMPLOYED,
        company_name="Adobe Inc.",
        monthly_salary=7500.00,
        experience_years=7,
    )
    
    loan_request = LoanRequest(
        loan_purpose=LoanPurpose.VEHICLE,
        loan_duration=60,  # 5 years
        loan_amount=45000.00,
        additional_info="Looking to purchase a hybrid vehicle",
    )
    
    documents = [
        DocumentInfo(
            document_type=DocumentType.BANK_STATEMENT,
            file_name="bank_statement.pdf",
            file_path="gs://loanai/documents/bank_001.pdf",
            file_size=200000,
            mime_type="application/pdf",
            uploaded_at=datetime.now(),
        ),
        DocumentInfo(
            document_type=DocumentType.SALARY_STATEMENT,
            file_name="salary_statement.pdf",
            file_path="gs://loanai/documents/salary_001.pdf",
            file_size=100000,
            mime_type="application/pdf",
            uploaded_at=datetime.now(),
        ),
    ]
    
    # Create application
    application = LoanApplication(
        customer_id="app-001",
        personal_info=personal_info,
        education=education,
        employment=employment,
        loan_request=loan_request,
        documents=documents,
    )
    
    # Process application
    decision = await processor.process(application)
    
    # Access decision
    print(f"Decision: {decision.decision}")
    print(f"Risk Score: {decision.risk_score}")
    print(f"Confidence: {decision.confidence_score:.2%}")
    
    return decision


# ============================================================================
# Example 2: Accessing Detailed Analysis
# ============================================================================

async def example_detailed_analysis():
    """Example showing how to access detailed analysis."""
    
    processor = LoanApplicationProcessor()
    
    # ... (create application as in example 1)
    
    # Get system status
    status = processor.get_system_status()
    print(f"Active Agents: {status['agents']}")
    
    # After processing (see example 1):
    # decision = await processor.process(application)
    
    # Access individual agent analysis
    # bank_analysis = decision.bank_analysis
    # salary_analysis = decision.salary_analysis
    # verification_analysis = decision.verification_analysis
    
    # print(f"Bank Analysis Risk: {bank_analysis['risk_score']}")
    # print(f"Salary Analysis Risk: {salary_analysis['risk_score']}")
    # print(f"Verification Risk: {verification_analysis['risk_score']}")


# ============================================================================
# Example 3: Batch Processing Multiple Applications
# ============================================================================

async def example_batch_processing():
    """Example of processing multiple applications."""
    
    processor = LoanApplicationProcessor()
    decisions = []
    
    # Create multiple applications
    for i in range(3):
        # ... create application (similar to example 1)
        pass
    
    # Process all applications
    # for app in applications:
    #     decision = await processor.process(app)
    #     decisions.append(decision)
    
    # Analyze results
    # approved = sum(1 for d in decisions if d.decision == "APPROVED")
    # rejected = sum(1 for d in decisions if d.decision == "REJECTED")
    # review = sum(1 for d in decisions if d.decision == "MANUAL_REVIEW")
    
    # print(f"Approved: {approved}, Rejected: {rejected}, Review: {review}")


# ============================================================================
# Example 4: Error Handling
# ============================================================================

async def example_error_handling():
    """Example showing error handling."""
    
    from loanai_agent.utils import (
        AgentException,
        DecisionException,
        ValidationException,
    )
    
    processor = LoanApplicationProcessor()
    
    try:
        # Create application (may raise validation error)
        personal_info = PersonalInfo(
            first_name="Bob",
            last_name="Smith",
            personal_id="123456789",
            gender=Gender.MALE,
            birth_year="2020",  # This will raise an error!
            phone="+1-555-1234",
            address="123 Main St",
        )
    except ValidationException as e:
        print(f"Validation Error: {e}")
    
    try:
        # Process application (may raise agent exception)
        # decision = await processor.process(application)
        pass
    except AgentException as e:
        print(f"Agent Error: {e}")
    except DecisionException as e:
        print(f"Decision Error: {e}")
    except Exception as e:
        print(f"Unexpected Error: {e}")


# ============================================================================
# Example 5: Custom Configuration
# ============================================================================

def example_custom_configuration():
    """Example showing how to use custom configuration."""
    
    from config.settings import settings
    
    # Access settings
    print(f"GCP Project: {settings.gcp_project_id}")
    print(f"ADK Model: {settings.google_adk_model}")
    print(f"Debug Mode: {settings.debug}")
    print(f"Log Level: {settings.log_level}")
    
    # Modify settings (at runtime)
    # settings.debug = False
    # settings.log_level = "INFO"


# ============================================================================
# Main Execution
# ============================================================================

if __name__ == "__main__":
    """
    Run the examples:
    
    python api_examples.py
    """
    
    # Uncomment the example you want to run:
    
    # asyncio.run(example_basic_processing())
    # asyncio.run(example_detailed_analysis())
    # asyncio.run(example_batch_processing())
    # asyncio.run(example_error_handling())
    # example_custom_configuration()
    
    print("API Examples - Uncomment the example you want to run in the main section")
