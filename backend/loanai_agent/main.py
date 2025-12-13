"""Main application orchestrator and entry point."""

import asyncio
from datetime import datetime
from typing import Any, Dict, Optional

from loanai_agent.agents import (
    BankStatementAgent,
    LoanOfficerAgent,
    SalaryStatementAgent,
    VerificationAgent,
)
from loanai_agent.models import (
    DecisionResult,
    DocumentInfo,
    DocumentType,
    LoanApplication,
)
from loanai_agent.protocols import (
    AgentCommunicationHub,
    DecisionEngine,
    RiskScoringEngine,
)
from loanai_agent.utils import generate_correlation_id, get_logger

logger = get_logger(__name__)


class LoanApplicationProcessor:
    """Main orchestrator for loan application processing."""

    def __init__(self):
        """Initialize the loan processor with all agents."""
        self.loan_officer = LoanOfficerAgent()
        self.bank_agent = BankStatementAgent()
        self.salary_agent = SalaryStatementAgent()
        self.verification_agent = VerificationAgent()

        # Setup communication hub
        self.comm_hub = AgentCommunicationHub(
            [
                self.loan_officer,
                self.bank_agent,
                self.salary_agent,
                self.verification_agent,
            ]
        )

        self.logger = get_logger(__name__)

    async def process(self, application: LoanApplication) -> DecisionResult:
        """Process a loan application through the multi-agent system.
        
        Args:
            application: Loan application to process
            
        Returns:
            Final decision result
        """
        correlation_id = generate_correlation_id()
        self.logger.info(
            f"Starting loan application processing for {application.customer_id} "
            f"(correlation_id={correlation_id})"
        )

        try:
            # Phase 1: Parallel sub-agent analysis
            self.logger.info("Phase 1: Launching parallel analysis")
            analysis_results = await self._run_parallel_analysis(application)

            # Phase 2: Inter-agent deliberation
            self.logger.info("Phase 2: Starting inter-agent deliberation")
            deliberation = await self._facilitate_deliberation(application, analysis_results)

            # Phase 3: Consensus building
            self.logger.info("Phase 3: Building consensus")
            consensus = await self._build_consensus(analysis_results, deliberation)

            # Phase 4: Final decision
            self.logger.info("Phase 4: Making final decision")
            final_decision = await self._make_final_decision(
                application, analysis_results, consensus
            )

            self.logger.info(
                f"Application processing complete. Decision: {final_decision.decision}"
            )

            return final_decision

        except Exception as e:
            self.logger.error(f"Application processing failed: {e}")
            raise

    async def _run_parallel_analysis(
        self, application: LoanApplication
    ) -> Dict[str, Any]:
        """Run parallel analysis from all sub-agents.
        
        Args:
            application: Loan application to analyze
            
        Returns:
            Dictionary of analysis results
        """
        self.logger.info("Executing parallel analysis")

        # Run all analyses concurrently
        tasks = {
            "bank_analysis": asyncio.create_task(self.bank_agent.analyze(application)),
            "salary_analysis": asyncio.create_task(self.salary_agent.analyze(application)),
            "verification_analysis": asyncio.create_task(
                self.verification_agent.analyze(application)
            ),
        }

        results = {}
        for name, task in tasks.items():
            try:
                result = await task
                results[name] = result
                self.logger.info(f"{name} completed successfully")
            except Exception as e:
                self.logger.error(f"{name} failed: {e}")
                results[name] = {"error": str(e), "risk_score": 100, "confidence_score": 0.0}

        return results

    async def _facilitate_deliberation(
        self,
        application: LoanApplication,
        analysis_results: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Facilitate inter-agent deliberation.
        
        Args:
            application: Original application
            analysis_results: Analysis results from all agents
            
        Returns:
            Deliberation transcript
        """
        self.logger.info("Facilitating agent deliberation")

        participants = [
            self.bank_agent.name,
            self.salary_agent.name,
            self.verification_agent.name,
        ]

        deliberation = await self.comm_hub.facilitate_discussion(
            participants=participants,
            topic="Application Risk Assessment and Approval Recommendation",
            context={
                "application": application.dict(),
                "analysis_results": analysis_results,
            },
            max_rounds=2,
        )

        return deliberation

    async def _build_consensus(
        self,
        analysis_results: Dict[str, Any],
        deliberation: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Build consensus from agent inputs.
        
        Args:
            analysis_results: Analysis results from agents
            deliberation: Deliberation transcript
            
        Returns:
            Consensus result
        """
        self.logger.info("Building consensus")

        consensus = await self.comm_hub.build_consensus(
            analysis_results=analysis_results,
            deliberation_transcript=deliberation,
        )

        self.logger.info(
            f"Consensus reached: {consensus.get('overall_recommendation')}"
        )

        return consensus

    async def _make_final_decision(
        self,
        application: LoanApplication,
        analysis_results: Dict[str, Any],
        consensus: Dict[str, Any],
    ) -> DecisionResult:
        """Make final decision by Loan Officer.
        
        Args:
            application: Original application
            analysis_results: Analysis results
            consensus: Consensus result
            
        Returns:
            Final decision result
        """
        self.logger.info("Making final decision")

        # Extract risk scores
        bank_risk = analysis_results.get("bank_analysis", {}).get("risk_score", 50)
        salary_risk = analysis_results.get("salary_analysis", {}).get("risk_score", 50)
        verification_risk = analysis_results.get("verification_analysis", {}).get("risk_score", 50)

        # Calculate aggregate risk
        loan_details = application.loan_request.dict()
        risk_assessment = RiskScoringEngine.calculate_aggregate_risk(
            bank_risk, salary_risk, verification_risk, loan_details
        )

        overall_risk = risk_assessment["total_risk_score"]

        # Extract confidence scores
        bank_conf = analysis_results.get("bank_analysis", {}).get("confidence_score", 0.5)
        salary_conf = analysis_results.get("salary_analysis", {}).get("confidence_score", 0.5)
        verification_conf = analysis_results.get("verification_analysis", {}).get(
            "confidence_score", 0.5
        )

        overall_confidence = (bank_conf + salary_conf + verification_conf) / 3

        # Collect red flags
        red_flags = []
        red_flags.extend(
            analysis_results.get("bank_analysis", {}).get("red_flags", [])
        )
        red_flags.extend(
            analysis_results.get("salary_analysis", {}).get("red_flags", [])
        )
        red_flags.extend(
            analysis_results.get("verification_analysis", {}).get("red_flags", [])
        )

        # Make decision
        consensus_rec = consensus.get("overall_recommendation", "manual_review")
        decision = DecisionEngine.make_decision(
            overall_risk,
            overall_confidence,
            consensus_rec,
            red_flags,
        )

        # Calculate loan terms if approved
        loan_terms = None
        if decision.value == "APPROVED":
            loan_terms = DecisionEngine.calculate_loan_terms(
                decision,
                application.loan_request.loan_amount,
                application.loan_request.loan_duration,
                overall_risk,
            )

        # Generate detailed report
        detailed_report = {
            "risk_assessment": risk_assessment,
            "analysis_results": analysis_results,
            "consensus": consensus,
            "red_flags": red_flags,
            "processing_timestamp": datetime.now().isoformat(),
        }

        # Generate explanation
        explanation = DecisionEngine.generate_explanation(
            decision,
            overall_risk,
            analysis_results.get("bank_analysis", {}).get("reasoning", "N/A"),
            analysis_results.get("salary_analysis", {}).get("reasoning", "N/A"),
            analysis_results.get("verification_analysis", {}).get("reasoning", "N/A"),
        )

        # Create final decision result
        final_decision = DecisionResult(
            decision=decision.value,
            confidence_score=round(overall_confidence, 2),
            risk_score=overall_risk,
            loan_amount=loan_terms.get("loan_amount") if loan_terms else None,
            interest_rate=loan_terms.get("interest_rate") if loan_terms else None,
            loan_duration=loan_terms.get("loan_duration") if loan_terms else None,
            conditions=self._generate_conditions(overall_risk, red_flags),
            reasoning=explanation,
            detailed_report=detailed_report,
            bank_analysis=analysis_results.get("bank_analysis"),
            salary_analysis=analysis_results.get("salary_analysis"),
            verification_analysis=analysis_results.get("verification_analysis"),
            consensus=consensus,
        )

        return final_decision

    def _generate_conditions(self, risk_score: int, red_flags: list) -> list:
        """Generate loan conditions based on risk.
        
        Args:
            risk_score: Overall risk score
            red_flags: List of red flags
            
        Returns:
            List of loan conditions
        """
        conditions = []

        if risk_score > 60:
            conditions.append("Require income verification by third party")
            conditions.append("Require collateral evaluation")

        if risk_score > 40:
            conditions.append("Require additional references")

        if red_flags:
            if len(red_flags) > 2:
                conditions.append("Subject to fraud investigation")
            for flag in red_flags[:2]:
                conditions.append(f"Condition: {flag}")

        return conditions

    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status.
        
        Returns:
            System status information
        """
        return {
            "status": "ready",
            "agents": [
                self.loan_officer.name,
                self.bank_agent.name,
                self.salary_agent.name,
                self.verification_agent.name,
            ],
            "timestamp": datetime.now().isoformat(),
        }
