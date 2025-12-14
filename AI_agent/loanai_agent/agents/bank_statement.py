"""Bank Statement Analysis Agent implementation."""

import asyncio
from typing import Any, Dict, List, Optional

from loanai_agent.agents.base_agent import AnalysisAgent
from loanai_agent.models import BankStatementAnalysis, DocumentType, LoanApplication
from loanai_agent.tools import DocumentProcessor, EmploymentVerifier, FinancialAnalyzer
from loanai_agent.utils import DocumentProcessingException, get_logger

logger = get_logger(__name__)


class BankStatementAgent(AnalysisAgent):
    """Agent specialized in analyzing bank statements."""

    def __init__(self):
        """Initialize Bank Statement Agent."""
        super().__init__(
            name="bank_statement_agent",
            description="Expert in analyzing bank statements and financial patterns",
            model="gemini-2.0-flash-exp",
            temperature=0.1,
        )
        self.document_processor = DocumentProcessor()
        self.financial_analyzer = FinancialAnalyzer()

    async def _perform_analysis(
        self, application: LoanApplication, **kwargs: Any
    ) -> BankStatementAnalysis:
        """Perform bank statement analysis with proper error handling.
        
        Args:
            application: Loan application with bank statement
            **kwargs: Additional arguments (e.g., document_path)
            
        Returns:
            BankStatementAnalysis object with complete analysis
        """
        try:
            # Extract bank statement document using safe helper
            bank_doc = self._find_document(
                application.documents,
                DocumentType.BANK_STATEMENT
            )

            if not bank_doc:
                self.logger.warning(
                    f"No bank statement found for customer {application.customer_id}"
                )
                return BankStatementAnalysis(
                    agent_name=self.name,
                    error="No bank statement provided",
                    confidence_score=0.0,
                    risk_score=100,
                    recommendation="reject",
                    reasoning="Cannot process application without bank statement",
                    document_authenticity="missing",
                    average_monthly_balance=0.0,
                    average_monthly_income=0.0,
                    income_consistency="unknown",
                    total_monthly_expenses=0.0,
                    recurring_obligations=0.0,
                    red_flags=["No bank statement provided"],
                    savings_behavior="unknown",
                )

            # Parse document with retry logic
            parsed_data = await self._parse_with_retry(bank_doc.file_path)

            # Perform analysis
            analysis = await self._analyze_bank_data(
                parsed_data, application.employment.monthly_salary
            )

            # Return typed BankStatementAnalysis model
            return BankStatementAnalysis(**analysis)

        except DocumentProcessingException as e:
            self.logger.error(f"Document processing failed: {e}", exc_info=True)
            return BankStatementAnalysis(
                agent_name=self.name,
                error=str(e),
                confidence_score=0.0,
                risk_score=100,
                recommendation="review",
                reasoning=f"Document processing error: {str(e)}",
                document_authenticity="unverified",
                average_monthly_balance=0.0,
                average_monthly_income=0.0,
                income_consistency="unknown",
                total_monthly_expenses=0.0,
                recurring_obligations=0.0,
                red_flags=["Document processing failed"],
                savings_behavior="unknown",
            )
        except Exception as e:
            self.logger.error(f"Unexpected error in analysis: {e}", exc_info=True)
            # Re-raise unexpected errors
            raise

    def _find_document(
        self, documents: List, doc_type: DocumentType
    ) -> Optional[Any]:
        """Safely find document by type.
        
        Args:
            documents: List of documents
            doc_type: Document type to find
            
        Returns:
            Document if found, None otherwise
        """
        return next(
            (d for d in documents if d.document_type == doc_type),
            None,
        )

    async def _parse_with_retry(
        self, file_path: str, max_retries: int = 3
    ) -> Dict[str, Any]:
        """Parse document with retry logic and exponential backoff.
        
        Args:
            file_path: Path to document file
            max_retries: Maximum number of retry attempts
            
        Returns:
            Parsed document data
            
        Raises:
            DocumentProcessingException: If parsing fails after all retries
        """
        for attempt in range(max_retries):
            try:
                return self.document_processor.parse_bank_statement(file_path)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise DocumentProcessingException(
                        f"Failed to parse document after {max_retries} attempts: {str(e)}"
                    ) from e
                
                # Exponential backoff: 1s, 2s, 4s
                wait_time = 2 ** attempt
                self.logger.warning(
                    f"Parse attempt {attempt + 1} failed, retrying in {wait_time}s: {e}"
                )
                await asyncio.sleep(wait_time)

    async def _analyze_bank_data(
        self, bank_data: Dict[str, Any], reported_salary: Optional[float] = None
    ) -> Dict[str, Any]:
        """Analyze parsed bank data.
        
        Args:
            bank_data: Parsed bank statement data
            reported_salary: Self-reported monthly salary for verification
            
        Returns:
            Detailed analysis result
        """
        self.logger.info("Analyzing bank statement data")

        transactions = bank_data.get("transactions", [])

        # Calculate financial metrics
        total_credits = sum(
            t.get("amount", 0)
            for t in transactions
            if t.get("type") == "credit"
        )
        total_debits = sum(
            t.get("amount", 0)
            for t in transactions
            if t.get("type") == "debit"
        )

        avg_balance = (
            bank_data.get("opening_balance", 0) + bank_data.get("closing_balance", 0)
        ) / 2

        # Analyze income consistency
        income_consistency_score = self.financial_analyzer.calculate_income_consistency(
            transactions
        )

        # Detect fraud indicators
        red_flags = self.financial_analyzer.detect_fraud_indicators(transactions)

        # Calculate financial health
        avg_monthly_income = total_credits / 3 if transactions else 0
        avg_monthly_expenses = total_debits / 3 if transactions else 0

        financial_health_score = self.financial_analyzer.calculate_financial_health_score(
            avg_monthly_income, avg_monthly_expenses, avg_balance
        )

        # Verify salary if reported
        salary_verified = True
        salary_variance = 0.0
        if reported_salary and avg_monthly_income > 0:
            salary_verified = EmploymentVerifier.verify_employment_consistency(
                reported_salary, avg_monthly_income
            )
            salary_variance = abs(
                (reported_salary - avg_monthly_income) / avg_monthly_income * 100
            )

        # Determine confidence and risk
        confidence_score = 0.85 if not red_flags else 0.65
        if not salary_verified:
            confidence_score *= 0.8

        risk_score = int(100 - financial_health_score)
        if red_flags:
            risk_score = min(100, risk_score + 15)

        recommendation = self._determine_recommendation(
            risk_score, salary_verified, red_flags
        )

        analysis = {
            "agent_name": self.name,
            "confidence_score": round(confidence_score, 2),
            "document_authenticity": "verified" if not red_flags else "suspicious",
            "average_monthly_balance": round(avg_balance, 2),
            "average_monthly_income": round(avg_monthly_income, 2),
            "income_consistency": "high"
            if income_consistency_score > 0.8
            else "moderate"
            if income_consistency_score > 0.5
            else "low",
            "total_monthly_expenses": round(avg_monthly_expenses, 2),
            "recurring_obligations": round(total_debits * 0.6, 2),
            "red_flags": red_flags,
            "savings_behavior": "positive"
            if avg_balance > 0
            else "neutral"
            if avg_balance == 0
            else "negative",
            "debt_indicators": {
                "estimated_monthly_debt": round(total_debits * 0.3, 2),
                "debt_to_income_ratio": round(
                    (total_debits * 0.3) / avg_monthly_income * 100, 2
                )
                if avg_monthly_income > 0
                else 0,
            },
            "recommendation": recommendation,
            "reasoning": self._generate_reasoning(
                financial_health_score, red_flags, salary_verified, salary_variance
            ),
            "risk_score": min(100, risk_score),
        }

        return analysis

    def _determine_recommendation(
        self, risk_score: int, salary_verified: bool, red_flags: List[str]
    ) -> str:
        """Determine recommendation based on analysis."""
        if red_flags or not salary_verified:
            return "review"
        if risk_score < 30:
            return "approve"
        elif risk_score < 60:
            return "review"
        else:
            return "reject"

    def _generate_reasoning(
        self,
        financial_health_score: float,
        red_flags: List[str],
        salary_verified: bool,
        salary_variance: float,
    ) -> str:
        """Generate reasoning text for analysis."""
        reasoning_parts = []

        if financial_health_score > 70:
            reasoning_parts.append("Strong financial health metrics")
        elif financial_health_score > 40:
            reasoning_parts.append("Moderate financial health metrics")
        else:
            reasoning_parts.append("Concerning financial health metrics")

        if salary_verified:
            reasoning_parts.append("Salary verified against bank deposits")
        else:
            reasoning_parts.append(
                f"Salary variance detected: {salary_variance:.1f}%"
            )

        if red_flags:
            reasoning_parts.append(f"Red flags identified: {', '.join(red_flags)}")
        else:
            reasoning_parts.append("No major red flags detected")

        return ". ".join(reasoning_parts)

    def get_system_prompt(self) -> str:
        """Get system prompt for this agent."""
        return """You are a financial analyst specialized in bank statement analysis with expertise 
in detecting fraud and assessing financial health.

Key responsibilities:
1. Extract and analyze transaction data from bank statements
2. Identify income sources and calculate consistent monthly income
3. Analyze spending patterns and expense categories
4. Calculate financial health metrics (savings rate, debt-to-income)
5. Detect potential fraud indicators or unusual activities
6. Verify stated salary against actual deposits
7. Assess creditworthiness based on financial behavior

Be thorough, detail-oriented, and data-driven. Identify red flags and provide 
confidence scores for your analysis."""
