"""Verification Agent implementation (MCP-Enabled)."""

from typing import Any, Dict, List, Optional

from loanai_agent.agents.base_agent import AnalysisAgent
from loanai_agent.models import LoanApplication, VerificationAnalysis
from loanai_agent.tools import ExternalDataFetcher, WebVerificationTools
from loanai_agent.utils import get_logger

logger = get_logger(__name__)


class VerificationAgent(AnalysisAgent):
    """Agent specialized in external verification using web search and APIs."""

    def __init__(self):
        """Initialize Verification Agent."""
        super().__init__(
            name="verification_agent",
            description="External verification specialist using web search and APIs",
            model="gemini-2.0-flash-exp",
            temperature=0.2,
        )
        self.web_tools = WebVerificationTools()
        self.data_fetcher = ExternalDataFetcher()

    async def _perform_analysis(
        self, application: LoanApplication, **kwargs: Any
    ) -> Dict[str, Any]:
        """Perform external verification analysis.
        
        Args:
            application: Loan application to verify
            **kwargs: Additional arguments
            
        Returns:
            Verification analysis result
        """
        try:
            self.logger.info(
                f"Starting external verification for customer: {application.customer_id}"
            )

            # Perform parallel verifications
            university_result = self.web_tools.verify_university(
                application.education.university
            )
            company_result = self.web_tools.verify_company(
                application.employment.company_name or ""
            )
            address_result = self.web_tools.verify_address(application.personal_info.address)
            salary_benchmark = self.web_tools.benchmark_salary(
                "Software Engineer",  # Example, would be extracted from data
                "San Francisco",
                company_result.get("name", ""),
            )

            # Compile results
            analysis = await self._compile_verification_results(
                university_result,
                company_result,
                address_result,
                salary_benchmark,
                application,
            )

            return analysis

        except Exception as e:
            self.logger.error(f"Verification analysis failed: {e}")
            raise

    async def _compile_verification_results(
        self,
        university_result: Dict[str, Any],
        company_result: Dict[str, Any],
        address_result: Dict[str, Any],
        salary_benchmark: Dict[str, Any],
        application: LoanApplication,
    ) -> Dict[str, Any]:
        """Compile all verification results into a single analysis.
        
        Args:
            university_result: University verification result
            company_result: Company verification result
            address_result: Address verification result
            salary_benchmark: Salary benchmark result
            application: Original application
            
        Returns:
            Compiled verification analysis
        """
        self.logger.info("Compiling verification results")

        # Calculate confidence and risk based on verification results
        verification_scores = []

        # University verification
        university_verified = university_result.get("legitimacy") == "verified"
        if university_verified:
            verification_scores.append(1.0)
        else:
            verification_scores.append(0.6)

        # Company verification
        company_verified = company_result.get("legitimacy") == "verified"
        if company_verified:
            verification_scores.append(1.0)
        else:
            verification_scores.append(0.6)

        # Address verification
        address_verified = address_result.get("valid", False)
        if address_verified:
            verification_scores.append(1.0)
        else:
            verification_scores.append(0.5)

        # Average confidence
        avg_confidence = (
            sum(verification_scores) / len(verification_scores)
            if verification_scores
            else 0.5
        )

        # Calculate risk score
        risk_score = int((1 - avg_confidence) * 100)

        # Detect red flags
        red_flags = self._detect_verification_red_flags(
            university_result, company_result, address_result, salary_benchmark, application
        )

        if red_flags:
            risk_score = min(100, risk_score + 15)
            avg_confidence *= 0.8

        recommendation = self._determine_recommendation(
            avg_confidence, red_flags, university_verified, company_verified
        )

        analysis = {
            "agent_name": self.name,
            "confidence_score": round(avg_confidence, 2),
            "university_verification": {
                "name": university_result.get("name"),
                "country": university_result.get("country"),
                "ranking": university_result.get("ranking"),
                "accredited": university_result.get("accredited"),
                "legitimacy": university_result.get("legitimacy"),
            },
            "company_verification": {
                "name": company_result.get("name"),
                "industry": company_result.get("industry"),
                "employees": company_result.get("employees"),
                "founded": company_result.get("founded"),
                "legitimacy": company_result.get("legitimacy"),
                "rating": company_result.get("rating"),
            },
            "address_verification": {
                "address": address_result.get("address"),
                "valid": address_result.get("valid"),
                "geocoded": address_result.get("geocoded"),
                "city": address_result.get("city"),
                "state": address_result.get("state"),
                "zip_code": address_result.get("zip_code"),
            },
            "salary_benchmark": {
                "job_title": salary_benchmark.get("job_title"),
                "location": salary_benchmark.get("location"),
                "salary_range": salary_benchmark.get("salary_range"),
                "data_points": salary_benchmark.get("data_points"),
                "confidence": salary_benchmark.get("confidence"),
            },
            "red_flags": red_flags,
            "recommendation": recommendation,
            "reasoning": self._generate_reasoning(
                university_verified, company_verified, address_verified, red_flags
            ),
            "risk_score": min(100, risk_score),
        }

        return analysis

    def _detect_verification_red_flags(
        self,
        university_result: Dict[str, Any],
        company_result: Dict[str, Any],
        address_result: Dict[str, Any],
        salary_benchmark: Dict[str, Any],
        application: LoanApplication,
    ) -> List[str]:
        """Detect red flags from verification results."""
        red_flags = []

        # University red flags
        if university_result.get("legitimacy") != "verified":
            red_flags.append("University could not be verified")

        # Company red flags
        if company_result.get("legitimacy") != "verified":
            red_flags.append("Company could not be verified")

        # Address red flags
        if not address_result.get("valid"):
            red_flags.append("Address could not be verified")

        # Salary benchmark red flags
        if (
            application.employment.monthly_salary
            and salary_benchmark.get("salary_range")
        ):
            salary_range = salary_benchmark.get("salary_range", {})
            if (
                application.employment.monthly_salary
                < salary_range.get("min", 0) * 0.8
            ):
                red_flags.append("Salary significantly below market rate")
            elif (
                application.employment.monthly_salary
                > salary_range.get("max", 0) * 2
            ):
                red_flags.append("Salary significantly above market rate")

        return red_flags

    def _determine_recommendation(
        self,
        confidence: float,
        red_flags: List[str],
        university_verified: bool,
        company_verified: bool,
    ) -> str:
        """Determine recommendation based on verification."""
        if red_flags or not (university_verified and company_verified):
            return "review"
        if confidence > 0.85:
            return "approve"
        elif confidence > 0.6:
            return "review"
        else:
            return "reject"

    def _generate_reasoning(
        self,
        university_verified: bool,
        company_verified: bool,
        address_verified: bool,
        red_flags: List[str],
    ) -> str:
        """Generate reasoning text for analysis."""
        reasoning_parts = []

        if university_verified:
            reasoning_parts.append("University verified as legitimate")
        else:
            reasoning_parts.append("University verification inconclusive")

        if company_verified:
            reasoning_parts.append("Company verified as legitimate")
        else:
            reasoning_parts.append("Company verification inconclusive")

        if address_verified:
            reasoning_parts.append("Address verified")
        else:
            reasoning_parts.append("Address could not be fully verified")

        if red_flags:
            reasoning_parts.append(f"Concerns: {', '.join(red_flags)}")

        return ". ".join(reasoning_parts)

    def get_system_prompt(self) -> str:
        """Get system prompt for this agent."""
        return """You are a verification specialist with access to web search and external APIs.
Your job is to verify customer-provided information using reliable external sources.

Key responsibilities:
1. Verify university reputation and accreditation
2. Validate company existence and legitimacy
3. Check employer reviews and financial health
4. Verify address authenticity using geocoding
5. Benchmark salary against market data
6. Cross-reference identity information
7. Gather market intelligence for assessment

Use multiple sources and cite your references. Be thorough and objective.
Clearly distinguish between verified, partially verified, and unverified information."""
