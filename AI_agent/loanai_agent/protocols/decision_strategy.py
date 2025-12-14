"""Decision strategy patterns for loan approval logic."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional

from loanai_agent.models import LoanApplication


class DecisionStatus(str, Enum):
    """Decision status for loan applications."""

    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    MANUAL_REVIEW = "MANUAL_REVIEW"


@dataclass
class DecisionContext:
    """Context for decision making with all relevant information."""

    risk_score: int
    confidence_score: float
    consensus: Optional[Dict[str, Any]]
    bank_analysis: Optional[Dict[str, Any]]
    salary_analysis: Optional[Dict[str, Any]]
    verification_analysis: Optional[Dict[str, Any]]
    application: LoanApplication


class DecisionStrategy(ABC):
    """Abstract base class for decision strategies."""

    @abstractmethod
    def make_decision(self, context: DecisionContext) -> DecisionStatus:
        """Make loan decision based on context.
        
        Args:
            context: Decision context with all analysis data
            
        Returns:
            Decision status (APPROVED, REJECTED, or MANUAL_REVIEW)
        """
        pass

    @abstractmethod
    def explain_decision(
        self, context: DecisionContext, decision: DecisionStatus
    ) -> str:
        """Generate human-readable explanation for the decision.
        
        Args:
            context: Decision context
            decision: Decision made
            
        Returns:
            Explanation text
        """
        pass

    @abstractmethod
    def calculate_loan_terms(
        self, context: DecisionContext
    ) -> Optional[Dict[str, Any]]:
        """Calculate loan terms if approved.
        
        Args:
            context: Decision context
            
        Returns:
            Loan terms dictionary or None if rejected
        """
        pass


class ConservativeDecisionStrategy(DecisionStrategy):
    """Conservative lending strategy with strict thresholds."""

    # Threshold configuration
    THRESHOLDS = {
        "approve_risk_max": 30,
        "approve_confidence_min": 0.8,
        "review_risk_max": 50,
        "review_confidence_min": 0.6,
    }

    # Interest rate configuration
    BASE_INTEREST_RATE = 8.0
    RISK_PREMIUM_PER_10_POINTS = 0.5

    def make_decision(self, context: DecisionContext) -> DecisionStatus:
        """Make conservative loan decision.
        
        Approval criteria:
        - Risk score <= 30
        - Confidence >= 0.8
        
        Review criteria:
        - 30 < Risk score <= 50
        - Confidence >= 0.6
        
        Otherwise: Reject
        """
        # Check for immediate rejection
        if (
            context.risk_score > self.THRESHOLDS["review_risk_max"]
            or context.confidence_score < self.THRESHOLDS["review_confidence_min"]
        ):
            return DecisionStatus.REJECTED

        # Check for approval
        if (
            context.risk_score <= self.THRESHOLDS["approve_risk_max"]
            and context.confidence_score >= self.THRESHOLDS["approve_confidence_min"]
        ):
            return DecisionStatus.APPROVED

        # Default to manual review
        return DecisionStatus.MANUAL_REVIEW

    def explain_decision(
        self, context: DecisionContext, decision: DecisionStatus
    ) -> str:
        """Generate conservative strategy explanation."""
        parts = [
            f"Decision: {decision.value}",
            f"Strategy: Conservative Lending",
            f"Risk Score: {context.risk_score}/100",
            f"Confidence: {context.confidence_score:.1%}",
            "",
            "Rationale:",
        ]

        if decision == DecisionStatus.APPROVED:
            parts.append(
                f"✓ Low risk profile (score {context.risk_score} ≤ {self.THRESHOLDS['approve_risk_max']})"
            )
            parts.append(
                f"✓ High confidence ({context.confidence_score:.1%} ≥ {self.THRESHOLDS['approve_confidence_min']:.0%})"
            )
            parts.append("✓ All analysis agents completed successfully")
        elif decision == DecisionStatus.REJECTED:
            if context.risk_score > self.THRESHOLDS["review_risk_max"]:
                parts.append(
                    f"✗ High risk score ({context.risk_score} > {self.THRESHOLDS['review_risk_max']})"
                )
            if context.confidence_score < self.THRESHOLDS["review_confidence_min"]:
                parts.append(
                    f"✗ Low confidence ({context.confidence_score:.1%} < {self.THRESHOLDS['review_confidence_min']:.0%})"
                )
        else:  # MANUAL_REVIEW
            parts.append(
                f"⚠ Moderate risk score ({context.risk_score}), requires human review"
            )
            parts.append(
                f"⚠ Confidence level ({context.confidence_score:.1%}) is acceptable but not high"
            )

        return "\n".join(parts)

    def calculate_loan_terms(
        self, context: DecisionContext
    ) -> Optional[Dict[str, Any]]:
        """Calculate conservative loan terms."""
        if context.risk_score > self.THRESHOLDS["approve_risk_max"]:
            return None  # No terms for non-approved applications

        # Calculate interest rate based on risk
        interest_rate = self.BASE_INTEREST_RATE + (
            context.risk_score / 10 * self.RISK_PREMIUM_PER_10_POINTS
        )

        # Calculate maximum loan amount (conservative: 3x monthly salary)
        monthly_salary = context.application.employment.monthly_salary
        max_loan = monthly_salary * 3

        # Apply requested loan amount with maximum cap
        approved_amount = min(context.application.loan_amount, max_loan)

        # Determine loan duration based on amount
        if approved_amount <= monthly_salary * 2:
            duration_months = 12
        else:
            duration_months = 18

        return {
            "loan_amount": round(approved_amount, 2),
            "interest_rate": round(interest_rate, 2),
            "loan_duration": duration_months,
            "monthly_payment": round(
                self._calculate_monthly_payment(
                    approved_amount, interest_rate, duration_months
                ),
                2,
            ),
            "conditions": self._generate_conditions(context),
        }

    def _calculate_monthly_payment(
        self, principal: float, annual_rate: float, months: int
    ) -> float:
        """Calculate monthly loan payment using standard amortization formula."""
        monthly_rate = annual_rate / 100 / 12
        if monthly_rate == 0:
            return principal / months

        return principal * (
            monthly_rate * (1 + monthly_rate) ** months
        ) / ((1 + monthly_rate) ** months - 1)

    def _generate_conditions(self, context: DecisionContext) -> list:
        """Generate loan conditions based on risk factors."""
        conditions = []

        if context.risk_score > 20:
            conditions.append("Maintain stable employment throughout loan period")

        if context.risk_score > 25:
            conditions.append("Provide monthly bank statement updates")

        bank_analysis = context.bank_analysis
        if bank_analysis and bank_analysis.get("red_flags"):
            conditions.append("Clear any identified red flags before disbursement")

        return conditions


class AggressiveDecisionStrategy(DecisionStrategy):
    """Aggressive lending strategy for growth and market expansion."""

    THRESHOLDS = {
        "approve_risk_max": 45,
        "approve_confidence_min": 0.7,
        "review_risk_max": 65,
        "review_confidence_min": 0.5,
    }

    BASE_INTEREST_RATE = 9.5
    RISK_PREMIUM_PER_10_POINTS = 0.75

    def make_decision(self, context: DecisionContext) -> DecisionStatus:
        """Make aggressive loan decision."""
        if (
            context.risk_score > self.THRESHOLDS["review_risk_max"]
            or context.confidence_score < self.THRESHOLDS["review_confidence_min"]
        ):
            return DecisionStatus.REJECTED

        if (
            context.risk_score <= self.THRESHOLDS["approve_risk_max"]
            and context.confidence_score >= self.THRESHOLDS["approve_confidence_min"]
        ):
            return DecisionStatus.APPROVED

        return DecisionStatus.MANUAL_REVIEW

    def explain_decision(
        self, context: DecisionContext, decision: DecisionStatus
    ) -> str:
        """Generate aggressive strategy explanation."""
        parts = [
            f"Decision: {decision.value}",
            f"Strategy: Aggressive Growth Lending",
            f"Risk Score: {context.risk_score}/100",
            f"Confidence: {context.confidence_score:.1%}",
            "",
            "Note: Higher risk tolerance for market expansion",
        ]
        return "\n".join(parts)

    def calculate_loan_terms(
        self, context: DecisionContext
    ) -> Optional[Dict[str, Any]]:
        """Calculate aggressive loan terms."""
        if context.risk_score > self.THRESHOLDS["approve_risk_max"]:
            return None

        interest_rate = self.BASE_INTEREST_RATE + (
            context.risk_score / 10 * self.RISK_PREMIUM_PER_10_POINTS
        )

        # More generous: up to 4x monthly salary
        monthly_salary = context.application.employment.monthly_salary
        max_loan = monthly_salary * 4
        approved_amount = min(context.application.loan_amount, max_loan)

        # Longer durations available
        if approved_amount <= monthly_salary * 2:
            duration_months = 12
        elif approved_amount <= monthly_salary * 3:
            duration_months = 18
        else:
            duration_months = 24

        return {
            "loan_amount": round(approved_amount, 2),
            "interest_rate": round(interest_rate, 2),
            "loan_duration": duration_months,
            "monthly_payment": round(
                self._calculate_monthly_payment(
                    approved_amount, interest_rate, duration_months
                ),
                2,
            ),
            "conditions": ["Standard loan terms apply"],
        }

    def _calculate_monthly_payment(
        self, principal: float, annual_rate: float, months: int
    ) -> float:
        """Calculate monthly loan payment."""
        monthly_rate = annual_rate / 100 / 12
        if monthly_rate == 0:
            return principal / months

        return principal * (
            monthly_rate * (1 + monthly_rate) ** months
        ) / ((1 + monthly_rate) ** months - 1)


class BalancedDecisionStrategy(DecisionStrategy):
    """Balanced lending strategy for standard operations."""

    THRESHOLDS = {
        "approve_risk_max": 35,
        "approve_confidence_min": 0.75,
        "review_risk_max": 55,
        "review_confidence_min": 0.55,
    }

    BASE_INTEREST_RATE = 8.5
    RISK_PREMIUM_PER_10_POINTS = 0.6

    def make_decision(self, context: DecisionContext) -> DecisionStatus:
        """Make balanced loan decision."""
        if (
            context.risk_score > self.THRESHOLDS["review_risk_max"]
            or context.confidence_score < self.THRESHOLDS["review_confidence_min"]
        ):
            return DecisionStatus.REJECTED

        if (
            context.risk_score <= self.THRESHOLDS["approve_risk_max"]
            and context.confidence_score >= self.THRESHOLDS["approve_confidence_min"]
        ):
            return DecisionStatus.APPROVED

        return DecisionStatus.MANUAL_REVIEW

    def explain_decision(
        self, context: DecisionContext, decision: DecisionStatus
    ) -> str:
        """Generate balanced strategy explanation."""
        parts = [
            f"Decision: {decision.value}",
            f"Strategy: Balanced Lending",
            f"Risk Score: {context.risk_score}/100",
            f"Confidence: {context.confidence_score:.1%}",
            "",
            "Balanced approach between growth and risk management",
        ]
        return "\n".join(parts)

    def calculate_loan_terms(
        self, context: DecisionContext
    ) -> Optional[Dict[str, Any]]:
        """Calculate balanced loan terms."""
        if context.risk_score > self.THRESHOLDS["approve_risk_max"]:
            return None

        interest_rate = self.BASE_INTEREST_RATE + (
            context.risk_score / 10 * self.RISK_PREMIUM_PER_10_POINTS
        )

        # Balanced: 3.5x monthly salary
        monthly_salary = context.application.employment.monthly_salary
        max_loan = monthly_salary * 3.5
        approved_amount = min(context.application.loan_amount, max_loan)

        if approved_amount <= monthly_salary * 2:
            duration_months = 12
        elif approved_amount <= monthly_salary * 3:
            duration_months = 18
        else:
            duration_months = 21

        return {
            "loan_amount": round(approved_amount, 2),
            "interest_rate": round(interest_rate, 2),
            "loan_duration": duration_months,
            "monthly_payment": round(
                self._calculate_monthly_payment(
                    approved_amount, interest_rate, duration_months
                ),
                2,
            ),
            "conditions": self._generate_conditions(context),
        }

    def _calculate_monthly_payment(
        self, principal: float, annual_rate: float, months: int
    ) -> float:
        """Calculate monthly loan payment."""
        monthly_rate = annual_rate / 100 / 12
        if monthly_rate == 0:
            return principal / months

        return principal * (
            monthly_rate * (1 + monthly_rate) ** months
        ) / ((1 + monthly_rate) ** months - 1)

    def _generate_conditions(self, context: DecisionContext) -> list:
        """Generate balanced loan conditions."""
        conditions = []

        if context.risk_score > 25:
            conditions.append("Maintain employment stability")

        if context.risk_score > 30:
            conditions.append("Quarterly bank statement reviews")

        return conditions if conditions else ["Standard loan terms apply"]
