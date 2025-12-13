"""Agent communication and coordination protocol."""

from datetime import datetime
from typing import Any, Dict, List, Optional

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
        """Initialize communication hub.
        
        Args:
            agents: List of agents to coordinate
        """
        self.agents = {agent.name: agent for agent in agents}
        self.message_history: List[AgentMessage] = []
        self.logger = get_logger(__name__)

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
        """Get input from an agent for discussion.
        
        Args:
            agent_name: Name of agent
            topic: Discussion topic
            context: Context
            previous_rounds: Previous discussion rounds
            
        Returns:
            Agent's response
        """
        # Simulated agent response
        if "bank" in agent_name:
            return "Based on financial analysis, the applicant shows stable income patterns with positive savings."
        elif "salary" in agent_name:
            return "Employment is verified and stable with 5+ years tenure at current employer."
        elif "verification" in agent_name:
            return "External verification confirms all stated information is accurate."
        else:
            return f"Analysis from {agent_name} is complete."

    def _check_consensus(self, discussion_log: Dict[str, Any]) -> bool:
        """Check if consensus has been reached."""
        # Simple check: if all agents agree, we have consensus
        if len(discussion_log.get("rounds", [])) < 1:
            return False

        last_round = discussion_log["rounds"][-1]
        messages = last_round.get("messages", [])

        if len(messages) == 0:
            return False

        # In a real implementation, would parse messages for agreement
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
