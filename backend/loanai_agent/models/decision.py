"""Decision-related models and enums."""

from enum import Enum


class RiskLevel(str, Enum):
    """Risk level classification."""

    LOW = "low"
    MODERATE_LOW = "moderate_low"
    MODERATE = "moderate"
    MODERATE_HIGH = "moderate_high"
    HIGH = "high"


class DecisionStatus(str, Enum):
    """Decision status."""

    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    MANUAL_REVIEW = "MANUAL_REVIEW"


class OverrideReason(str, Enum):
    """Reasons for decision override."""

    DOCUMENT_FRAUD = "document_fraud_detected"
    INCOME_VERIFICATION_FAILED = "income_verification_failed"
    MULTIPLE_RED_FLAGS = "multiple_red_flags"
    LOW_CONSENSUS = "low_consensus_strength"
    REGULATORY_VIOLATION = "regulatory_violation"
