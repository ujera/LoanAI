"""Document processing and analysis tools."""

import json
from typing import Any, Dict, List, Optional

from loanai_agent.utils.logger import get_logger

logger = get_logger(__name__)


class DocumentProcessor:
    """Handles document OCR and text extraction."""

    @staticmethod
    def extract_text_from_document(
        document_path: str, document_type: str = "pdf"
    ) -> str:
        """
        Extract text from document using Document AI.
        In a real implementation, this would use Google Cloud Document AI.
        For demo purposes, we simulate the extraction.
        """
        logger.info(f"Extracting text from {document_path}")

        # Simulated OCR extraction
        simulated_extraction = f"""
        Extracted text from {document_type.upper()} document:
        {document_path}
        
        [SIMULATED OCR OUTPUT]
        This is a demonstration of OCR extraction.
        In production, this would use Google Cloud Document AI
        to extract real document content.
        """

        return simulated_extraction

    @staticmethod
    def parse_bank_statement(extracted_text: str) -> Dict[str, Any]:
        """Parse bank statement text into structured data."""
        logger.info("Parsing bank statement")

        # Simulated parsing
        parsed_data = {
            "account_holder": "John Doe",
            "account_number": "****1234",
            "statement_period": "2024-01-01 to 2024-01-31",
            "opening_balance": 5000.00,
            "closing_balance": 12500.00,
            "total_credits": 12000.00,
            "total_debits": 4500.00,
            "transactions": [
                {
                    "date": "2024-01-05",
                    "description": "Salary Deposit",
                    "amount": 5000.00,
                    "type": "credit",
                },
                {
                    "date": "2024-01-10",
                    "description": "Rent Payment",
                    "amount": 1200.00,
                    "type": "debit",
                },
                {
                    "date": "2024-01-15",
                    "description": "Grocery Store",
                    "amount": 150.00,
                    "type": "debit",
                },
            ],
        }

        return parsed_data

    @staticmethod
    def parse_salary_statement(extracted_text: str) -> Dict[str, Any]:
        """Parse salary statement text into structured data."""
        logger.info("Parsing salary statement")

        # Simulated parsing
        parsed_data = {
            "employee_name": "John Doe",
            "employee_id": "EMP12345",
            "employer": "Tech Solutions Inc.",
            "salary_period": "2024-01",
            "gross_salary": 5500.00,
            "deductions": {"tax": 900.00, "social_security": 250.00, "health": 150.00},
            "net_salary": 4200.00,
            "employment_type": "Full-time",
            "department": "Engineering",
            "job_title": "Senior Software Engineer",
        }

        return parsed_data


class FinancialAnalyzer:
    """Tools for financial analysis and metrics calculation."""

    @staticmethod
    def calculate_income_consistency(transactions: List[Dict]) -> float:
        """Calculate income consistency score (0-1)."""
        logger.info("Calculating income consistency")

        if not transactions:
            return 0.0

        income_transactions = [
            t for t in transactions if t.get("type") == "credit" and "salary" in t.get("description", "").lower()
        ]

        if not income_transactions:
            return 0.0

        # Simple consistency check: if we have multiple regular deposits, high consistency
        if len(income_transactions) >= 3:
            return 0.9
        elif len(income_transactions) >= 2:
            return 0.7
        else:
            return 0.4

    @staticmethod
    def detect_fraud_indicators(transactions: List[Dict]) -> List[str]:
        """Detect potential fraud indicators in transaction data."""
        logger.info("Detecting fraud indicators")

        red_flags = []

        # Check for unusual transaction patterns
        large_transactions = [
            t for t in transactions if abs(t.get("amount", 0)) > 10000
        ]
        if large_transactions:
            red_flags.append("Large unusual transactions detected")

        # Check for rapid account draining
        debits = [t for t in transactions if t.get("type") == "debit"]
        if debits and sum(t.get("amount", 0) for t in debits) > 50000:
            red_flags.append("Unusually high debit activity")

        return red_flags

    @staticmethod
    def calculate_financial_health_score(
        monthly_income: float, monthly_expenses: float, savings: float
    ) -> float:
        """Calculate overall financial health score (0-100)."""
        if monthly_income <= 0:
            return 0.0

        # Savings rate
        savings_rate = (savings / monthly_income) * 100 if monthly_income > 0 else 0
        savings_score = min(savings_rate / 30 * 40, 40)  # Max 40 points

        # Debt to income ratio
        debt_to_income = (monthly_expenses / monthly_income) * 100
        if debt_to_income < 30:
            debt_score = 40
        elif debt_to_income < 50:
            debt_score = 30
        elif debt_to_income < 70:
            debt_score = 15
        else:
            debt_score = 0

        # Income stability (bonus points)
        stability_score = 20

        return min(savings_score + debt_score + stability_score, 100)


class EmploymentVerifier:
    """Tools for employment verification and validation."""

    @staticmethod
    def verify_employment_consistency(
        self_reported_salary: float, documented_salary: float, threshold: float = 0.1
    ) -> bool:
        """Verify employment salary consistency."""
        if documented_salary == 0:
            return False

        variance = abs(
            (self_reported_salary - documented_salary) / documented_salary
        )
        return variance <= threshold

    @staticmethod
    def calculate_employment_stability_score(
        tenure_months: int, job_title: str = ""
    ) -> float:
        """Calculate employment stability score (0-1)."""
        logger.info(f"Calculating employment stability for {tenure_months} months tenure")

        if tenure_months < 3:
            return 0.3
        elif tenure_months < 12:
            return 0.5
        elif tenure_months < 24:
            return 0.7
        elif tenure_months < 60:
            return 0.85
        else:
            return 1.0

    @staticmethod
    def detect_employment_red_flags(
        employment_data: Dict[str, Any]
    ) -> List[str]:
        """Detect red flags in employment data."""
        red_flags = []

        # Check for very recent employment
        tenure = employment_data.get("tenure_months", 0)
        if tenure < 3:
            red_flags.append("Very recent employment (less than 3 months)")

        # Check for frequent job changes
        job_changes = employment_data.get("job_changes_last_2_years", 0)
        if job_changes > 3:
            red_flags.append("Frequent job changes detected")

        # Check for employment gaps
        employment_gaps = employment_data.get("employment_gaps", [])
        for gap in employment_gaps:
            if gap.get("duration_months", 0) > 6:
                red_flags.append(f"Employment gap of {gap.get('duration_months')} months")

        return red_flags
