"""Decision framework and risk scoring."""

from typing import Any, Dict, Optional

from loanai_agent.models import DecisionResult, DecisionStatus
from loanai_agent.utils import DecisionException, get_logger

logger = get_logger(__name__)


class RiskScoringEngine:
    """Engine for calculating comprehensive risk scores."""

    # Risk thresholds
    RISK_THRESHOLDS = {
        "low": (0, 20),
        "moderate_low": (21, 40),
        "moderate": (41, 60),
        "moderate_high": (61, 75),
        "high": (76, 100),
    }

    # Decision thresholds
    DECISION_THRESHOLD_APPROVE = 40
    DECISION_THRESHOLD_REVIEW = 60
    DECISION_THRESHOLD_REJECT = 75

    @staticmethod
    def calculate_aggregate_risk(
        bank_risk: int,
        salary_risk: int,
        verification_risk: int,
        loan_details: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Calculate aggregate risk score from all factors.
        
        Args:
            bank_risk: Bank analysis risk score (0-100)
            salary_risk: Salary analysis risk score (0-100)
            verification_risk: Verification risk score (0-100)
            loan_details: Loan request details
            
        Returns:
            Risk assessment result
        """
        # Weighted average of agent risks
        agent_weights = {
            "bank": 0.4,
            "salary": 0.35,
            "verification": 0.25,
        }

        total_risk = (
            (bank_risk * agent_weights["bank"])
            + (salary_risk * agent_weights["salary"])
            + (verification_risk * agent_weights["verification"])
        )

        # Adjust for loan factors
        loan_risk_adjustment = RiskScoringEngine._calculate_loan_risk(loan_details)
        final_risk = min(100, int(total_risk + loan_risk_adjustment))

        # Determine risk level
        risk_level = RiskScoringEngine._get_risk_level(final_risk)

        return {
            "total_risk_score": final_risk,
            "risk_level": risk_level,
            "agent_risks": {
                "bank": bank_risk,
                "salary": salary_risk,
                "verification": verification_risk,
            },
            "loan_risk_adjustment": loan_risk_adjustment,
        }

    @staticmethod
    def _calculate_loan_risk(loan_details: Dict[str, Any]) -> float:
        """Calculate risk based on loan characteristics.
        
        Args:
            loan_details: Loan request details
            
        Returns:
            Risk adjustment value
        """
        risk_adjustment = 0.0

        # Risk based on loan amount
        loan_amount = loan_details.get("loan_amount", 0)
        if loan_amount > 500_000:
            risk_adjustment += 15
        elif loan_amount > 250_000:
            risk_adjustment += 10
        elif loan_amount > 100_000:
            risk_adjustment += 5

        # Risk based on loan duration
        loan_duration = loan_details.get("loan_duration", 24)
        if loan_duration > 240:  # > 20 years
            risk_adjustment += 10
        elif loan_duration < 12:  # < 1 year
            risk_adjustment += 5

        # Risk based on loan purpose
        loan_purpose = loan_details.get("loan_purpose", "personal")
        purpose_risk = {
            "mortgage": 5,
            "vehicle": 10,
            "personal": 15,
            "education": 8,
            "business": 20,
            "others": 15,
        }
        risk_adjustment += purpose_risk.get(loan_purpose, 15)

        return min(risk_adjustment, 25)

    @staticmethod
    def _get_risk_level(risk_score: int) -> str:
        """Get risk level classification.
        
        Args:
            risk_score: Numerical risk score (0-100)
            
        Returns:
            Risk level string
        """
        for level, (min_score, max_score) in RiskScoringEngine.RISK_THRESHOLDS.items():
            if min_score <= risk_score <= max_score:
                return level
        return "high"


class DecisionEngine:
    """Engine for making final loan decisions."""

    @staticmethod
    def make_decision(
        risk_score: int,
        confidence_score: float,
        consensus_recommendation: str,
        red_flags: list,
    ) -> DecisionStatus:
        """Make final decision based on metrics.
        
        Args:
            risk_score: Calculated risk score (0-100)
            confidence_score: Overall confidence (0-1)
            consensus_recommendation: Consensus from agents
            red_flags: List of identified red flags
            
        Returns:
            Decision status
        """
        logger.info(
            f"Making decision: risk={risk_score}, confidence={confidence_score}, "
            f"consensus={consensus_recommendation}"
        )

        # Check for reject conditions
        if red_flags and len(red_flags) > 3:
            return DecisionStatus.REJECTED

        if risk_score > RiskScoringEngine.DECISION_THRESHOLD_REJECT:
            return DecisionStatus.REJECTED

        # Check for approve conditions
        if (
            risk_score <= RiskScoringEngine.DECISION_THRESHOLD_APPROVE
            and confidence_score > 0.8
            and consensus_recommendation == "approve"
        ):
            return DecisionStatus.APPROVED

        # Check for review conditions
        if (
            risk_score <= RiskScoringEngine.DECISION_THRESHOLD_REVIEW
            and confidence_score > 0.6
        ):
            return DecisionStatus.MANUAL_REVIEW

        # Default
        if risk_score > RiskScoringEngine.DECISION_THRESHOLD_REVIEW:
            return DecisionStatus.REJECTED

        return DecisionStatus.MANUAL_REVIEW

    @staticmethod
    def calculate_loan_terms(
        decision: DecisionStatus,
        requested_amount: float,
        requested_duration: int,
        risk_score: int,
    ) -> Optional[Dict[str, Any]]:
        """Calculate loan terms if approved.
        
        Args:
            decision: Decision status
            requested_amount: Requested loan amount
            requested_duration: Requested loan duration (months)
            risk_score: Risk score (0-100)
            
        Returns:
            Loan terms or None if not approved
        """
        if decision != DecisionStatus.APPROVED:
            return None

        # Calculate interest rate based on risk
        base_rate = 5.0
        risk_adjusted_rate = base_rate + (risk_score / 100) * 15

        # May adjust loan amount based on risk
        approved_amount = requested_amount
        if risk_score > 70:
            approved_amount = requested_amount * 0.8
        elif risk_score > 50:
            approved_amount = requested_amount * 0.9

        # May adjust duration
        approved_duration = requested_duration
        if risk_score > 70:
            approved_duration = min(requested_duration, 120)  # Max 10 years

        return {
            "loan_amount": round(approved_amount, 2),
            "interest_rate": round(risk_adjusted_rate, 2),
            "loan_duration": approved_duration,
            "monthly_payment": DecisionEngine._calculate_monthly_payment(
                approved_amount, risk_adjusted_rate, approved_duration
            ),
        }

    @staticmethod
    def _calculate_monthly_payment(
        principal: float, annual_rate: float, months: int
    ) -> float:
        """Calculate monthly payment using standard formula.
        
        Args:
            principal: Loan principal
            annual_rate: Annual interest rate
            months: Loan duration in months
            
        Returns:
            Monthly payment amount
        """
        if months <= 0:
            return 0.0

        monthly_rate = annual_rate / 100 / 12
        if monthly_rate == 0:
            return principal / months

        payment = (
            principal
            * (monthly_rate * (1 + monthly_rate) ** months)
            / ((1 + monthly_rate) ** months - 1)
        )
        return round(payment, 2)

    @staticmethod
    def generate_explanation(
        decision: DecisionStatus,
        risk_score: int,
        bank_reasoning: str,
        salary_reasoning: str,
        verification_reasoning: str,
    ) -> str:
        """Generate decision explanation.
        
        Args:
            decision: Final decision
            risk_score: Risk score
            bank_reasoning: Bank analysis reasoning
            salary_reasoning: Salary analysis reasoning
            verification_reasoning: Verification reasoning
            
        Returns:
            Formatted explanation
        """
        # Determine risk level description
        risk_level = RiskScoringEngine._get_risk_level(risk_score)
        risk_descriptions = {
            "low": "excellent financial standing",
            "moderate_low": "good financial standing with minor concerns",
            "moderate": "acceptable financial standing with some areas requiring attention",
            "moderate_high": "concerning financial indicators",
            "high": "significant financial risks identified"
        }
        risk_desc = risk_descriptions.get(risk_level, "")
        
        # Create decision summary
        decision_summaries = {
            DecisionStatus.APPROVED: f"✓ Application Approved - The applicant demonstrates {risk_desc}. All verification checks have been successfully completed.",
            DecisionStatus.REJECTED: f"✗ Application Declined - The applicant shows {risk_desc}. The risk assessment indicates this application does not meet our lending criteria at this time.",
            DecisionStatus.MANUAL_REVIEW: f"⚠ Manual Review Required - The applicant shows {risk_desc}. Additional review by a loan officer is recommended to make a final determination."
        }
        
        decision_summary = decision_summaries.get(decision, "Decision pending further review.")
        
        explanation_parts = [
            f"## Decision Summary\n{decision_summary}",
            f"\n## Risk Assessment",
            f"Overall Risk Score: {risk_score}/100 ({risk_level.replace('_', ' ').title()})",
            f"\n## Detailed Analysis",
            f"\n### Financial Health\n{bank_reasoning}",
            f"\n### Employment & Income\n{salary_reasoning}",
            f"\n### Identity Verification\n{verification_reasoning}",
        ]

        return "\n".join(explanation_parts)
