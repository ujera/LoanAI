"""Salary Statement Analysis Agent implementation."""

from typing import Any, Dict, List, Optional

from loanai_agent.agents.base_agent import AnalysisAgent
from loanai_agent.models import LoanApplication, SalaryStatementAnalysis
from loanai_agent.tools import DocumentProcessor, EmploymentVerifier
from loanai_agent.utils import get_logger

logger = get_logger(__name__)


class SalaryStatementAgent(AnalysisAgent):
    """Agent specialized in analyzing salary statements and employment verification."""

    def __init__(self):
        """Initialize Salary Statement Agent."""
        super().__init__(
            name="salary_statement_agent",
            description="Expert in employment verification and salary analysis",
            model="gemini-2.0-flash-exp",
            temperature=0.1,
        )
        self.document_processor = DocumentProcessor()
        self.employment_verifier = EmploymentVerifier()

    async def _perform_analysis(
        self, application: LoanApplication, **kwargs: Any
    ) -> Dict[str, Any]:
        """Perform salary statement analysis.
        
        Args:
            application: Loan application with salary statement
            **kwargs: Additional arguments
            
        Returns:
            Analysis result
        """
        try:
            # Extract salary statement document
            salary_doc = next(
                (
                    d
                    for d in application.documents
                    if d.document_type.value == "salary_statement"
                ),
                None,
            )

            if not salary_doc:
                self.logger.warning("No salary statement document found")
                return {
                    "error": "No salary statement provided",
                    "confidence_score": 0.0,
                    "risk_score": 100,
                }

            # Extract text from document
            extracted_text = self.document_processor.extract_text_from_document(
                salary_doc.file_path
            )

            # Parse extracted text
            parsed_data = self.document_processor.parse_salary_statement(
                extracted_text
            )

            # Perform analysis
            analysis = await self._analyze_salary_data(
                parsed_data,
                application.employment,
                application.personal_info.first_name,
                application.personal_info.last_name,
            )

            return analysis

        except Exception as e:
            self.logger.error(f"Salary statement analysis failed: {e}")
            raise

    async def _analyze_salary_data(
        self, salary_data: Dict[str, Any], employment_info: Any, first_name: str, last_name: str
    ) -> Dict[str, Any]:
        """Analyze parsed salary data.
        
        Args:
            salary_data: Parsed salary statement data
            employment_info: Employment information from application
            first_name: Employee's first name
            last_name: Employee's last name
            
        Returns:
            Detailed analysis result
        """
        self.logger.info("Analyzing salary statement data")

        employee_name_match = (
            f"{salary_data.get('employee_name', '')}".lower()
            == f"{first_name} {last_name}".lower()
        )

        gross_salary = salary_data.get("gross_salary", 0)
        net_salary = salary_data.get("net_salary", 0)

        # Verify consistency with self-reported salary
        reported_salary = employment_info.monthly_salary or 0
        salary_matches = self.employment_verifier.verify_employment_consistency(
            reported_salary, gross_salary, threshold=0.15
        )

        if salary_matches:
            salary_variance = abs(
                (reported_salary - gross_salary) / gross_salary * 100
                if gross_salary > 0
                else 0
            )
        else:
            salary_variance = abs(
                (reported_salary - gross_salary) / gross_salary * 100
                if gross_salary > 0
                else 0
            )

        # Calculate employment stability
        tenure_months = employment_info.experience_years * 12 if employment_info.experience_years else 0
        stability_score = self.employment_verifier.calculate_employment_stability_score(
            tenure_months, employment_info.company_name
        )

        # Detect employment red flags
        employment_data = {
            "tenure_months": tenure_months,
            "job_changes_last_2_years": 0,
            "employment_gaps": [],
        }
        red_flags = self.employment_verifier.detect_employment_red_flags(
            employment_data
        )

        # Determine confidence and risk
        confidence_score = 0.9
        if not employee_name_match:
            confidence_score *= 0.7
        if not salary_matches:
            confidence_score *= 0.8

        risk_score = int(100 - (stability_score * 100))
        if red_flags:
            risk_score = min(100, risk_score + 10)

        recommendation = self._determine_recommendation(
            salary_matches, red_flags, tenure_months
        )

        analysis = {
            "agent_name": self.name,
            "confidence_score": round(confidence_score, 2),
            "document_authenticity": "verified" if not red_flags else "suspicious",
            "employer_name": salary_data.get("employer", "Unknown"),
            "employee_name": salary_data.get("employee_name", "Unknown"),
            "employee_id": salary_data.get("employee_id", "Unknown"),
            "gross_salary": round(gross_salary, 2),
            "net_salary": round(net_salary, 2),
            "employment_period": salary_data.get("salary_period", "Unknown"),
            "employment_duration_months": tenure_months,
            "deductions": salary_data.get("deductions", {}),
            "benefits": salary_data.get("benefits", []),
            "matches_self_reported": salary_matches,
            "salary_variance": round(salary_variance, 2),
            "employment_status_verified": salary_data.get("employment_type") in [
                "Full-time",
                "Part-time",
            ],
            "recommendation": recommendation,
            "reasoning": self._generate_reasoning(
                salary_matches, salary_variance, tenure_months, red_flags
            ),
            "risk_score": min(100, risk_score),
        }

        return analysis

    def _determine_recommendation(
        self, salary_matches: bool, red_flags: List[str], tenure_months: int
    ) -> str:
        """Determine recommendation based on analysis."""
        if red_flags or tenure_months < 3:
            return "review"
        if salary_matches and tenure_months > 24:
            return "approve"
        elif tenure_months > 12:
            return "review"
        else:
            return "review"

    def _generate_reasoning(
        self,
        salary_matches: bool,
        salary_variance: float,
        tenure_months: int,
        red_flags: List[str],
    ) -> str:
        """Generate reasoning text for analysis."""
        reasoning_parts = []

        if salary_matches:
            reasoning_parts.append("Salary verified against self-reported amount")
        else:
            reasoning_parts.append(
                f"Salary variance detected: {salary_variance:.1f}%"
            )

        if tenure_months > 24:
            reasoning_parts.append("Stable long-term employment")
        elif tenure_months > 12:
            reasoning_parts.append("Moderate employment duration")
        else:
            reasoning_parts.append("Recent employment")

        if red_flags:
            reasoning_parts.append(f"Concerns: {', '.join(red_flags)}")
        else:
            reasoning_parts.append("No major employment concerns")

        return ". ".join(reasoning_parts)

    def get_system_prompt(self) -> str:
        """Get system prompt for this agent."""
        return """You are an HR specialist and employment verification expert with deep knowledge 
of salary statements, employment law, and compensation structures.

Key responsibilities:
1. Extract and validate employment information from salary statements
2. Verify employer legitimacy and employment status
3. Cross-reference stated salary with actual documented income
4. Calculate employment stability and tenure indicators
5. Assess employment security and risk factors
6. Analyze benefits and deductions for legitimacy
7. Detect employment verification discrepancies

Be thorough in cross-referencing information. Provide confidence scores and 
flag any inconsistencies or concerns."""
