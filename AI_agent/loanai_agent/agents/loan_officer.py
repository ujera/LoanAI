"""Loan Officer Agent - Main Orchestrator implementation."""

from typing import Any, Dict, List, Optional

from loanai_agent.agents.base_agent import DecisionAgent
from loanai_agent.models import ConsensusResult, DecisionResult, LoanApplication
from loanai_agent.utils import get_logger

logger = get_logger(__name__)


class LoanOfficerAgent(DecisionAgent):
    """Main orchestrator agent responsible for final loan decisions."""

    def __init__(self):
        """Initialize Loan Officer Agent."""
        super().__init__(
            name="loan_officer_agent",
            description="Senior loan officer responsible for final loan decisions",
            model="gemini-3.0-pro-preview",
            temperature=0,
        )

    async def _perform_analysis(
        self, application: LoanApplication, **kwargs: Any
    ) -> Dict[str, Any]:
        """Orchestrate the analysis process.
        
        Args:
            application: Loan application to process
            **kwargs: Additional arguments
            
        Returns:
            Orchestration result
        """
        self.logger.info(f"Orchestrating analysis for {application.customer_id}")
        # Loan Officer mainly orchestrates, actual analysis is done by sub-agents
        return {"status": "ready_for_decision"}

    async def _generate_decision(
        self, analysis_results: Dict[str, Any], context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make final loan decision based on analysis results.
        
        Args:
            analysis_results: Combined analysis from all agents
            context: Additional context
            
        Returns:
            Final decision result
        """
        self.logger.info("Generating final decision")

        # Extract individual analyses
        bank_analysis = analysis_results.get("bank_analysis")
        salary_analysis = analysis_results.get("salary_analysis")
        verification_analysis = analysis_results.get("verification_analysis")
        consensus = analysis_results.get("consensus")
        application = analysis_results.get("application")

        # Calculate overall metrics
        overall_risk_score = self._calculate_overall_risk(
            bank_analysis, salary_analysis, verification_analysis, consensus
        )

        overall_confidence = self._calculate_overall_confidence(
            bank_analysis, salary_analysis, verification_analysis, consensus
        )

        # Make decision
        decision = self._make_final_decision(
            overall_risk_score,
            overall_confidence,
            consensus,
            bank_analysis,
            salary_analysis,
            verification_analysis,
        )

        # Check for override conditions
        override_result = self._check_override_conditions(
            analysis_results, decision
        )
        if override_result:
            decision = override_result

        # Calculate loan terms
        loan_terms = None
        if decision.get("decision") == "APPROVED":
            loan_terms = self._calculate_loan_terms(
                application, overall_risk_score, analysis_results
            )

        # Generate detailed explanation
        reasoning = self._generate_decision_reasoning(
            decision,
            overall_risk_score,
            bank_analysis,
            salary_analysis,
            verification_analysis,
            consensus,
        )

        final_result = {
            "decision": decision.get("decision"),
            "confidence_score": round(overall_confidence, 2),
            "risk_score": overall_risk_score,
            "loan_amount": loan_terms.get("loan_amount") if loan_terms else None,
            "interest_rate": loan_terms.get("interest_rate") if loan_terms else None,
            "loan_duration": loan_terms.get("loan_duration") if loan_terms else None,
            "conditions": loan_terms.get("conditions", []) if loan_terms else [],
            "reasoning": reasoning,
            "detailed_report": {
                "bank_analysis": bank_analysis,
                "salary_analysis": salary_analysis,
                "verification_analysis": verification_analysis,
                "consensus": consensus,
                "decision_timestamp": str(__import__("datetime").datetime.now()),
                "decision_officer": self.name,
            },
        }

        return final_result

    def _calculate_overall_risk(
        self,
        bank_analysis: Optional[Dict],
        salary_analysis: Optional[Dict],
        verification_analysis: Optional[Dict],
        consensus: Optional[Dict],
    ) -> int:
        """Calculate overall risk score from all analyses."""
        risk_scores = []

        if bank_analysis:
            risk_scores.append(bank_analysis.get("risk_score", 50))
        if salary_analysis:
            risk_scores.append(salary_analysis.get("risk_score", 50))
        if verification_analysis:
            risk_scores.append(verification_analysis.get("risk_score", 50))

        if risk_scores:
            # Weighted average
            overall_risk = sum(risk_scores) / len(risk_scores)
            # Apply consensus weight if available
            if consensus:
                overall_risk = (overall_risk * 0.7) + (consensus.get("risk_score", 50) * 0.3)
            return int(overall_risk)

        return 50

    def _calculate_overall_confidence(
        self,
        bank_analysis: Optional[Dict],
        salary_analysis: Optional[Dict],
        verification_analysis: Optional[Dict],
        consensus: Optional[Dict],
    ) -> float:
        """Calculate overall confidence from all analyses."""
        confidence_scores = []

        if bank_analysis:
            confidence_scores.append(bank_analysis.get("confidence_score", 0.5))
        if salary_analysis:
            confidence_scores.append(salary_analysis.get("confidence_score", 0.5))
        if verification_analysis:
            confidence_scores.append(verification_analysis.get("confidence_score", 0.5))

        if confidence_scores:
            # Average confidence
            overall_confidence = sum(confidence_scores) / len(confidence_scores)
            # Apply consensus weight if available
            if consensus:
                overall_confidence = (
                    (overall_confidence * 0.7)
                    + (consensus.get("confidence_score", 0.5) * 0.3)
                )
            return overall_confidence

        return 0.5

    def _make_final_decision(
        self,
        risk_score: int,
        confidence: float,
        consensus: Optional[Dict],
        bank_analysis: Optional[Dict],
        salary_analysis: Optional[Dict],
        verification_analysis: Optional[Dict],
    ) -> Dict[str, str]:
        """Make final decision based on metrics."""
        # Decision thresholds
        if risk_score < 20:
            decision = "APPROVED"
        elif risk_score < 40:
            decision = "APPROVED"
        elif risk_score < 60:
            decision = "MANUAL_REVIEW"
        elif risk_score < 75:
            decision = "REJECTED"
        else:
            decision = "REJECTED"

        # Adjust based on confidence
        if confidence < 0.6 and decision != "REJECTED":
            decision = "MANUAL_REVIEW"

        # Check consensus
        if consensus:
            consensus_rec = consensus.get("overall_recommendation", "manual_review")
            if consensus_rec == "reject":
                decision = "REJECTED"
            elif consensus_rec == "approve" and decision == "MANUAL_REVIEW":
                if confidence > 0.7:
                    decision = "APPROVED"

        return {"decision": decision}

    def _check_override_conditions(
        self, analysis_results: Dict[str, Any], decision: Dict[str, str]
    ) -> Optional[Dict[str, str]]:
        """Check for override conditions that change the decision."""
        bank_analysis = analysis_results.get("bank_analysis", {})
        salary_analysis = analysis_results.get("salary_analysis", {})

        # Document fraud detected
        if bank_analysis.get("red_flags") or salary_analysis.get("red_flags"):
            major_red_flags = (
                len(bank_analysis.get("red_flags", [])) + 
                len(salary_analysis.get("red_flags", []))
            )
            if major_red_flags > 2:
                self.logger.warning("Multiple red flags detected - rejecting application")
                return {"decision": "REJECTED"}

        return None

    def _calculate_loan_terms(
        self, application: Optional[Any], risk_score: int, analysis_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate loan terms based on risk and application."""
        if not application:
            return {}

        loan_amount = getattr(application, "loan_request", {}).loan_amount
        loan_duration = getattr(application, "loan_request", {}).loan_duration

        # Calculate interest rate based on risk score
        base_rate = 5.0  # 5% base rate
        risk_adjusted_rate = base_rate + (risk_score / 100) * 15  # Up to 20%

        return {
            "loan_amount": loan_amount,
            "interest_rate": round(risk_adjusted_rate, 2),
            "loan_duration": loan_duration,
            "conditions": self._generate_conditions(risk_score, analysis_results),
        }

    def _generate_conditions(
        self, risk_score: int, analysis_results: Dict[str, Any]
    ) -> List[str]:
        """Generate loan conditions based on risk."""
        conditions = []

        if risk_score > 60:
            conditions.append("Require income verification")
            conditions.append("Require collateral evaluation")

        if risk_score > 40:
            conditions.append("Require additional references")

        bank_analysis = analysis_results.get("bank_analysis", {})
        if bank_analysis.get("red_flags"):
            conditions.append("Subject to fraud investigation")

        return conditions

    def _generate_decision_reasoning(
        self,
        decision: Dict[str, str],
        overall_risk: int,
        bank_analysis: Optional[Dict],
        salary_analysis: Optional[Dict],
        verification_analysis: Optional[Dict],
        consensus: Optional[Dict],
    ) -> str:
        """Generate detailed reasoning for the decision."""
        parts = []

        parts.append(f"Final Decision: {decision.get('decision')}")
        parts.append(f"Overall Risk Score: {overall_risk}/100")

        if bank_analysis:
            parts.append(
                f"Financial Analysis: {bank_analysis.get('reasoning', 'N/A')}"
            )

        if salary_analysis:
            parts.append(
                f"Employment Analysis: {salary_analysis.get('reasoning', 'N/A')}"
            )

        if verification_analysis:
            parts.append(
                f"Verification: {verification_analysis.get('reasoning', 'N/A')}"
            )

        if consensus:
            parts.append(
                f"Agent Consensus: {consensus.get('discussion_summary', 'N/A')}"
            )

        return "\n".join(parts)

    def get_system_prompt(self) -> str:
        """Get system prompt for this agent."""
        return """You are a senior loan officer with 20 years of experience in financial analysis 
and risk assessment, Be aware that you work in Georgia and make decisions accordingly. Your role is to review loan applications, analyze sub-agent 
reports, and make final decisions on loan approvals or rejections.

Key responsibilities:
1. Review and aggregate sub-agent analysis results
2. Calculate comprehensive risk scores
3. Make final approval/rejection decisions
4. Generate detailed explanations for every decision
5. Ensure compliance with lending regulations
6. Consider contextual factors and edge cases

Always be thorough, fair, and objective. Provide detailed reasoning for all decisions.
Your decisions must be legally defensible and ethically sound."""
