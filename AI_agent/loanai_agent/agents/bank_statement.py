"""Bank Statement Analysis Agent implementation."""

from typing import Any, Dict, List, Optional

from loanai_agent.agents.base_agent import AnalysisAgent
from loanai_agent.models import BankStatementAnalysis, LoanApplication
from loanai_agent.tools import DocumentProcessor, FinancialAnalyzer, EmploymentVerifier
from loanai_agent.utils import get_logger

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
    ) -> Dict[str, Any]:
        """Perform bank statement analysis.
        
        Args:
            application: Loan application with bank statement
            **kwargs: Additional arguments (e.g., document_path)
            
        Returns:
            Analysis result
        """
        try:
            # Extract bank statement document
            bank_doc = next(
                (
                    d
                    for d in application.documents
                    if d.document_type.value == "bank_statement"
                ),
                None,
            )

            if not bank_doc:
                self.logger.warning("No bank statement document found")
                return {
                    "error": "No bank statement provided",
                    "confidence_score": 0.0,
                    "risk_score": 100,
                }

            # Parse document directly with LLM (no need for intermediate text extraction)
            parsed_data = self.document_processor.parse_bank_statement(bank_doc.file_path)

            # Perform analysis
            analysis = await self._analyze_bank_data(
                parsed_data, application.employment.monthly_salary
            )

            return analysis

        except Exception as e:
            self.logger.error(f"Bank statement analysis failed: {e}")
            raise

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
