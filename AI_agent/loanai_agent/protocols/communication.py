"""Agent communication and coordination protocol."""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

import google.generativeai as genai

from config.settings import settings
from loanai_agent.agents.base_agent import BaseAgent
from loanai_agent.utils import CommunicationException, get_logger

logger = get_logger(__name__)


class AgentMessage:
    """Represents a message between agents."""

    def __init__(
        self,
        from_agent: str,
        to_agent: str,
        message_type: str,
        payload: Dict[str, Any],
        correlation_id: str,
    ):
        """Initialize an agent message.
        
        Args:
            from_agent: Source agent name
            to_agent: Destination agent name (or "broadcast")
            message_type: Type of message
            payload: Message payload
            correlation_id: Correlation ID for tracking
        """
        self.from_agent = from_agent
        self.to_agent = to_agent
        self.message_type = message_type
        self.payload = payload
        self.timestamp = datetime.now().isoformat()
        self.correlation_id = correlation_id

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "message_type": self.message_type,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "correlation_id": self.correlation_id,
        }


class AgentCommunicationHub:
    """Central hub for agent communication and coordination."""

    def __init__(self, agents: List[BaseAgent]):
        """Initialize communication hub with LLM-powered discussion capability.
        
        Args:
            agents: List of agents to coordinate
        """
        self.agents = {agent.name: agent for agent in agents}
        self.message_history: List[AgentMessage] = []
        self.logger = get_logger(__name__)
        
        # Initialize LLM for facilitation
        self.facilitator_model = None
        if settings.google_api_key:
            try:
                genai.configure(api_key=settings.google_api_key)
                self.facilitator_model = genai.GenerativeModel('gemini-2.0-flash-exp')
                self.logger.info("LLM facilitator initialized successfully")
            except Exception as e:
                self.logger.warning(f"Failed to initialize LLM facilitator: {e}")
                self.logger.warning("Falling back to rule-based consensus")

    async def facilitate_discussion(
        self,
        participants: List[str],
        topic: str,
        context: Dict[str, Any],
        max_rounds: int = 3,
    ) -> Dict[str, Any]:
        """Facilitate multi-agent discussion.
        
        Args:
            participants: List of participating agent names
            topic: Discussion topic
            context: Context for discussion
            max_rounds: Maximum discussion rounds
            
        Returns:
            Discussion result
        """
        self.logger.info(f"Starting discussion on: {topic}")

        discussion_log = {
            "topic": topic,
            "participants": participants,
            "rounds": [],
            "started_at": datetime.now().isoformat(),
        }

        for round_num in range(max_rounds):
            round_result = {
                "round": round_num + 1,
                "messages": [],
            }

            for agent_name in participants:
                if agent_name not in self.agents:
                    self.logger.warning(f"Agent {agent_name} not found")
                    continue

                # Simulate agent response
                response = await self._get_agent_input(
                    agent_name, topic, context, discussion_log.get("rounds", [])
                )

                message = AgentMessage(
                    from_agent=agent_name,
                    to_agent="all",
                    message_type="discussion_contribution",
                    payload={"response": response},
                    correlation_id=f"disc-{id(discussion_log)}",
                )

                round_result["messages"].append(message.to_dict())
                self._log_message(message)

            discussion_log["rounds"].append(round_result)

            # Check for early consensus
            if self._check_consensus(discussion_log):
                self.logger.info("Early consensus reached")
                break

        discussion_log["ended_at"] = datetime.now().isoformat()
        return discussion_log

    async def build_consensus(
        self,
        analysis_results: Dict[str, Any],
        deliberation_transcript: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Build consensus from agent inputs.
        
        Args:
            analysis_results: Individual agent analysis results
            deliberation_transcript: Transcript from discussion
            
        Returns:
            Consensus result
        """
        self.logger.info("Building consensus from agent inputs")

        # Extract recommendations from each agent
        recommendations = {}
        confidence_scores = []
        risk_scores = []

        for agent_name, result in analysis_results.items():
            if isinstance(result, dict):
                rec = result.get("recommendation", "review")
                conf = result.get("confidence_score", 0.5)
                risk = result.get("risk_score", 50)

                recommendations[agent_name] = rec
                confidence_scores.append(conf)
                risk_scores.append(risk)

        # Calculate agreement
        approval_votes = sum(1 for r in recommendations.values() if r == "approve")
        rejection_votes = sum(1 for r in recommendations.values() if r == "reject")
        review_votes = sum(1 for r in recommendations.values() if r == "review")

        total_votes = len(recommendations)

        # Determine consensus recommendation
        if approval_votes > total_votes * 0.66:
            consensus_rec = "approve"
        elif rejection_votes > total_votes * 0.5:
            consensus_rec = "reject"
        else:
            consensus_rec = "manual_review"

        # Calculate metrics
        avg_confidence = (
            sum(confidence_scores) / len(confidence_scores)
            if confidence_scores
            else 0.5
        )
        avg_risk = (
            sum(risk_scores) / len(risk_scores) if risk_scores else 50
        )

        consensus_result = {
            "overall_recommendation": consensus_rec,
            "confidence_score": round(avg_confidence, 2),
            "risk_score": int(avg_risk),
            "agent_agreements": {
                "approve": approval_votes,
                "reject": rejection_votes,
                "review": review_votes,
            },
            "total_agents": total_votes,
            "disagreement_details": (
                self._get_disagreement_details(recommendations)
                if not self._is_unanimous(recommendations)
                else None
            ),
            "discussion_summary": self._summarize_discussion(deliberation_transcript),
        }

        return consensus_result

    async def _get_agent_input(
        self,
        agent_name: str,
        topic: str,
        context: Dict[str, Any],
        previous_rounds: List,
    ) -> str:
        """Get input from an agent for discussion using LLM.
        
        Args:
            agent_name: Name of agent
            topic: Discussion topic
            context: Context including analysis results
            previous_rounds: Previous discussion rounds
            
        Returns:
            Agent's response generated by LLM
        """
        if not self.facilitator_model:
            # Fallback to simple responses if LLM not available
            return self._get_fallback_response(agent_name, context)
        
        try:
            agent = self.agents.get(agent_name)
            if not agent:
                return f"Agent {agent_name} not available"
            
            # Build context for the specific agent
            agent_context = self._build_agent_context(agent_name, context)
            
            # Create prompt for agent's perspective
            prompt = f"""You are {agent.name}, a {agent.description}.

Discussion Topic: {topic}

Your Analysis Results:
{json.dumps(agent_context, indent=2)}

Previous Discussion Rounds:
{json.dumps(previous_rounds[-2:] if len(previous_rounds) > 2 else previous_rounds, indent=2)}

Based on your expertise and analysis, provide your professional opinion on this loan application.
Be specific, cite evidence from your analysis, and make a clear recommendation.
Keep your response concise (2-3 paragraphs)."""

            response = await self.facilitator_model.generate_content_async(prompt)
            return response.text
            
        except Exception as e:
            self.logger.error(f"Failed to generate LLM contribution for {agent_name}: {e}")
            return self._get_fallback_response(agent_name, context)
    
    def _build_agent_context(self, agent_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Build context specific to an agent.
        
        Args:
            agent_name: Name of the agent
            context: Full context dictionary
            
        Returns:
            Agent-specific context
        """
        # Extract relevant analysis for this agent
        if "bank" in agent_name.lower():
            return context.get("bank_analysis", {})
        elif "salary" in agent_name.lower():
            return context.get("salary_analysis", {})
        elif "verification" in agent_name.lower():
            return context.get("verification_analysis", {})
        else:
            return context
    
    def _get_fallback_response(self, agent_name: str, context: Dict[str, Any]) -> str:
        """Provide fallback response when LLM is unavailable.
        
        Args:
            agent_name: Name of the agent
            context: Context dictionary
            
        Returns:
            Simple fallback response
        """
        agent_context = self._build_agent_context(agent_name, context)
        
        if "bank" in agent_name.lower():
            rec = agent_context.get("recommendation", "review")
            risk = agent_context.get("risk_score", 50)
            return f"Based on financial analysis, recommendation: {rec}, risk score: {risk}"
        elif "salary" in agent_name.lower():
            rec = agent_context.get("recommendation", "review")
            verified = agent_context.get("salary_verified", False)
            return f"Employment verification: {'verified' if verified else 'needs review'}, recommendation: {rec}"
        elif "verification" in agent_name.lower():
            rec = agent_context.get("recommendation", "review")
            return f"Verification complete, recommendation: {rec}"
        else:
            return f"Analysis from {agent_name} is complete."

    def _check_consensus(self, discussion_log: Dict[str, Any]) -> bool:
        """Check if consensus has been reached using LLM analysis.
        
        Args:
            discussion_log: Complete discussion log
            
        Returns:
            True if consensus reached, False otherwise
        """
        if len(discussion_log.get("rounds", [])) < 2:
            return False

        if not self.facilitator_model:
            # Fallback to simple check
            return False

        try:
            # Use LLM to evaluate if agents have converged
            prompt = f"""Analyze this multi-agent discussion and determine if the agents have reached consensus.

Discussion:
{json.dumps(discussion_log["rounds"][-2:], indent=2)}

Consider:
1. Are agents making consistent recommendations?
2. Are there significant disagreements remaining?
3. Has the discussion become repetitive (indicating convergence)?

Answer with YES or NO, followed by a brief (1 sentence) explanation."""

            # Use synchronous call for simplicity in consensus check
            response = self.facilitator_model.generate_content(prompt)
            result_text = response.text.strip().upper()
            
            is_converged = result_text.startswith("YES")
            if is_converged:
                self.logger.info(f"Consensus detected: {response.text}")
            
            return is_converged
            
        except Exception as e:
            self.logger.error(f"Convergence check failed: {e}")
            return False

    def _is_unanimous(self, recommendations: Dict[str, str]) -> bool:
        """Check if all agents made the same recommendation."""
        if not recommendations:
            return False
        first_rec = list(recommendations.values())[0]
        return all(rec == first_rec for rec in recommendations.values())

    def _get_disagreement_details(self, recommendations: Dict[str, str]) -> str:
        """Get details of disagreements."""
        unique_recs = set(recommendations.values())
        if len(unique_recs) == 1:
            return None

        details = "Agent disagreements: "
        for rec in unique_recs:
            agents = [a for a, r in recommendations.items() if r == rec]
            details += f"{rec} ({', '.join(agents)}); "

        return details

    def _summarize_discussion(self, deliberation: Dict[str, Any]) -> str:
        """Generate summary of discussion."""
        rounds = deliberation.get("rounds", [])
        summary_parts = []

        for round_num, round_data in enumerate(rounds, 1):
            summary_parts.append(
                f"Round {round_num}: {len(round_data.get('messages', []))} agents contributed"
            )

        return " | ".join(summary_parts) if summary_parts else "No discussion rounds"

    def _log_message(self, message: AgentMessage) -> None:
        """Log a message."""
        self.message_history.append(message)
        self.logger.debug(
            f"Message from {message.from_agent} to {message.to_agent}: "
            f"{message.message_type}"
        )

    def get_message_history(
        self, correlation_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get message history.
        
        Args:
            correlation_id: Optional filter by correlation ID
            
        Returns:
            List of messages
        """
        if correlation_id:
            return [
                m.to_dict()
                for m in self.message_history
                if m.correlation_id == correlation_id
            ]
        return [m.to_dict() for m in self.message_history]
