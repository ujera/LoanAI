"""FastAPI server for LoanAI Agent System.

This server exposes the loan processing functionality through REST API endpoints.
"""

import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

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

# Global processor instance
processor: Optional[LoanApplicationProcessor] = None

# In-memory status tracking (replace with database in production)
application_status: Dict[str, Dict[str, Any]] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    global processor
    
    logger.info("Starting LoanAI Agent API Server")
    try:
        processor = LoanApplicationProcessor()
        logger.info("LoanApplicationProcessor initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize processor: {e}")
        raise
    
    yield
    
    logger.info("Shutting down LoanAI Agent API Server")


# Initialize FastAPI app
app = FastAPI(
    title="LoanAI Agent API",
    description="AI Multi-Agent System for Intelligent Loan Processing",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class ProcessLoanRequest(BaseModel):
    """Request model for loan processing."""
    
    customerId: str
    firstName: str
    lastName: str
    personalId: str
    gender: str
    birthYear: str
    phone: str
    address: str
    educationLevel: str
    university: Optional[str] = None
    employmentStatus: str
    companyName: Optional[str] = None
    monthlySalary: float
    experienceYears: int
    loanPurpose: str
    loanAmount: float
    loanDuration: int
    additionalInfo: Optional[str] = None
    bankStatementUrl: Optional[str] = None
    bankStatementSize: Optional[int] = None
    bankStatementMimeType: Optional[str] = None
    salaryStatementUrl: Optional[str] = None
    salaryStatementSize: Optional[int] = None
    salaryStatementMimeType: Optional[str] = None

    @field_validator('gender')
    @classmethod
    def validate_gender(cls, v: str) -> str:
        """Validate gender field."""
        valid_genders = [g.value for g in Gender]
        if v.lower() not in valid_genders:
            raise ValueError(f"Gender must be one of: {valid_genders}")
        return v.lower()

    @field_validator('educationLevel')
    @classmethod
    def validate_education_level(cls, v: str) -> str:
        """Validate education level."""
        valid_levels = [e.value for e in EducationLevel]
        if v.lower() not in valid_levels:
            raise ValueError(f"Education level must be one of: {valid_levels}")
        return v.lower()

    @field_validator('employmentStatus')
    @classmethod
    def validate_employment_status(cls, v: str) -> str:
        """Validate employment status."""
        valid_statuses = [e.value for e in EmploymentStatus]
        if v.lower() not in valid_statuses:
            raise ValueError(f"Employment status must be one of: {valid_statuses}")
        return v.lower()

    @field_validator('loanPurpose')
    @classmethod
    def validate_loan_purpose(cls, v: str) -> str:
        """Validate loan purpose."""
        valid_purposes = [p.value for p in LoanPurpose]
        if v.lower() not in valid_purposes:
            raise ValueError(f"Loan purpose must be one of: {valid_purposes}")
        return v.lower()


class ProcessLoanResponse(BaseModel):
    """Response model for loan processing."""
    
    success: bool
    message: str
    customerId: str
    processingStarted: bool
    estimatedCompletionTime: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""
    
    status: str
    timestamp: str
    version: str
    processor_initialized: bool


# API Endpoints
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0",
        processor_initialized=processor is not None,
    )


@app.post("/api/process", response_model=ProcessLoanResponse, tags=["Loan Processing"])
async def process_loan_application(request: ProcessLoanRequest):
    """Process a loan application through the AI multi-agent system.
    
    This endpoint accepts a loan application and initiates processing through
    the multi-agent system. The processing happens asynchronously.
    
    Args:
        request: Loan application data
        
    Returns:
        Response indicating processing has started
    """
    if processor is None:
        logger.error("Processor not initialized")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Loan processing service is not available"
        )
    
    try:
        logger.info(f"Received loan application for customer: {request.customerId}")
        
        # Initialize status tracking
        application_status[request.customerId] = {
            "customerId": request.customerId,
            "status": "received",
            "message": "Application received and queued for processing",
            "receivedAt": datetime.utcnow().isoformat(),
            "estimatedCompletion": "5-10 minutes",
            "progress": {
                "received": True,
                "validating": False,
                "processing": False,
                "completed": False
            }
        }
        
        # Convert request to LoanApplication model
        application = _convert_to_loan_application(request)
        
        # Update status to processing
        application_status[request.customerId]["status"] = "processing"
        application_status[request.customerId]["message"] = "Application is being processed by AI agents"
        application_status[request.customerId]["progress"]["validating"] = True
        application_status[request.customerId]["progress"]["processing"] = True
        
        # Start processing in background (fire-and-forget)
        asyncio.create_task(_process_application_async(application))
        
        return ProcessLoanResponse(
            success=True,
            message="Loan application received and processing started",
            customerId=request.customerId,
            processingStarted=True,
            estimatedCompletionTime="5-10 minutes",
        )
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error processing loan application: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process loan application"
        )


async def _process_application_async(application: LoanApplication):
    """Process application asynchronously in the background.
    
    Args:
        application: Loan application to process
    """
    customer_id = application.customer_id
    
    try:
        logger.info(f"Starting async processing for customer: {customer_id}")
        
        # Update status
        if customer_id in application_status:
            application_status[customer_id]["status"] = "analyzing"
            application_status[customer_id]["message"] = "AI agents are analyzing your application"
        
        result = await processor.process(application)
        
        logger.info(
            f"Processing complete for customer {customer_id}. "
            f"Decision: {result.decision}, Risk Score: {result.risk_score}, Confidence: {result.confidence_score}"
        )
        
        # Update status with results
        if customer_id in application_status:
            application_status[customer_id]["status"] = "completed"
            application_status[customer_id]["message"] = "Application processing completed"
            application_status[customer_id]["progress"]["completed"] = True
            application_status[customer_id]["completedAt"] = datetime.utcnow().isoformat()
            application_status[customer_id]["result"] = {
                "decision": result.decision,
                "risk_score": result.risk_score,
                "confidence_score": result.confidence_score,
                "loan_amount": result.loan_amount,
                "interest_rate": result.interest_rate,
                "loan_duration": result.loan_duration,
                "conditions": result.conditions,
                "reasoning": result.reasoning
            }
        
        # Update database with decision
        await _update_database_with_decision(customer_id, result)
        
    except Exception as e:
        logger.error(
            f"Error in async processing for customer {customer_id}: {e}",
            exc_info=True
        )
        
        # Update status with error
        if customer_id in application_status:
            application_status[customer_id]["status"] = "failed"
            application_status[customer_id]["message"] = "Processing failed due to an error"
            application_status[customer_id]["error"] = str(e)
            application_status[customer_id]["failedAt"] = datetime.utcnow().isoformat()


async def _update_database_with_decision(customer_id: str, result) -> None:
    """Update database with the AI decision result.
    
    Args:
        customer_id: Customer UUID
        result: DecisionResult object from the AI processor
    """
    try:
        import os
        import asyncpg
        
        # Get database connection parameters from environment
        db_host = os.getenv('DB_HOST', '127.0.0.1')
        db_port = int(os.getenv('DB_PORT', '5432'))
        db_user = os.getenv('DB_USER', 'loanai_user')
        db_password = os.getenv('DB_PASSWORD', 'loanai_password')
        db_name = os.getenv('DB_NAME', 'loanai')
        
        # Connect to database
        conn = await asyncpg.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=db_name
        )
        
        try:
            # Map decision to application status
            status_mapping = {
                "APPROVED": "approved",
                "REJECTED": "rejected",
                "MANUAL_REVIEW": "manual_review"
            }
            application_status_value = status_mapping.get(result.decision, "manual_review")
            
            # Calculate eligibility score (0-100) from confidence and risk
            # Higher confidence and lower risk = higher eligibility
            eligibility_score = int((result.confidence_score * 100) * (1 - result.risk_score / 100))
            
            # Update customers table
            await conn.execute(
                """
                UPDATE customers 
                SET application_status = $1, 
                    eligibility_score = $2,
                    updated_at = CURRENT_TIMESTAMP
                WHERE customer_id = $3
                """,
                application_status_value,
                eligibility_score,
                customer_id
            )
            
            logger.info(
                f"Database updated for customer {customer_id}: "
                f"status={application_status_value}, score={eligibility_score}"
            )
            
        finally:
            await conn.close()
            
    except ImportError:
        logger.warning("asyncpg not installed. Install with: pip install asyncpg")
    except Exception as e:
        logger.error(f"Failed to update database for customer {customer_id}: {e}")
        # Don't raise - this is non-critical, the status is in memory


def _convert_to_loan_application(request: ProcessLoanRequest) -> LoanApplication:
    """Convert API request to LoanApplication model.
    
    Args:
        request: API request data
        
    Returns:
        LoanApplication instance
    """
    # Personal information
    personal_info = PersonalInfo(
        first_name=request.firstName,
        last_name=request.lastName,
        personal_id=request.personalId,
        gender=Gender(request.gender),
        birth_year=request.birthYear,
        phone=request.phone,
        address=request.address,
    )
    
    # Education
    education = Education(
        education_level=EducationLevel(request.educationLevel),
        university=request.university or "Not Specified",
    )
    
    # Employment
    employment = Employment(
        employment_status=EmploymentStatus(request.employmentStatus),
        company_name=request.companyName,
        monthly_salary=request.monthlySalary,
        experience_years=request.experienceYears,
    )
    
    # Loan request
    loan_request = LoanRequest(
        loan_purpose=LoanPurpose(request.loanPurpose),
        loan_duration=request.loanDuration,
        loan_amount=request.loanAmount,
        additional_info=request.additionalInfo,
    )
    
    # Documents
    documents = []
    if request.bankStatementUrl:
        documents.append(
            DocumentInfo(
                document_type=DocumentType.BANK_STATEMENT,
                file_name=f"bank_statement_{request.customerId}.pdf",
                file_path=request.bankStatementUrl,
                file_size=request.bankStatementSize or 0,
                mime_type=request.bankStatementMimeType or "application/pdf",
                uploaded_at=datetime.utcnow(),
            )
        )
    
    if request.salaryStatementUrl:
        documents.append(
            DocumentInfo(
                document_type=DocumentType.SALARY_STATEMENT,
                file_name=f"salary_statement_{request.customerId}.pdf",
                file_path=request.salaryStatementUrl,
                file_size=request.salaryStatementSize or 0,
                mime_type=request.salaryStatementMimeType or "application/pdf",
                uploaded_at=datetime.utcnow(),
            )
        )
    
    # Create complete application
    application = LoanApplication(
        customer_id=request.customerId,
        personal_info=personal_info,
        education=education,
        employment=employment,
        loan_request=loan_request,
        documents=documents,
    )
    
    return application


@app.get("/api/status/{customer_id}", tags=["Status"])
async def get_status(customer_id: str):
    """Get the processing status of a loan application.
    
    Args:
        customer_id: Customer ID to check status for
        
    Returns:
        Processing status information
    """
    if customer_id not in application_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No application found for customer ID: {customer_id}"
        )
    
    return application_status[customer_id]


@app.get("/api/result/{customer_id}", tags=["Results"])
async def get_result(customer_id: str):
    """Get the final result of a loan application.
    
    Args:
        customer_id: Customer ID to get result for
        
    Returns:
        Final decision result if processing is complete
    """
    if customer_id not in application_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No application found for customer ID: {customer_id}"
        )
    
    status_data = application_status[customer_id]
    
    # Check if processing is complete
    if status_data.get("status") != "completed":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application processing not yet complete. Status: {status_data.get('status')}"
        )
    
    # Return the result
    return status_data.get("result", {})


@app.get("/api/applications", tags=["Status"])
async def list_applications():
    """List all loan applications and their statuses.
    
    Returns:
        List of all applications with their current status
    """
    return {
        "count": len(application_status),
        "applications": list(application_status.values())
    }


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "name": "LoanAI Agent API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
