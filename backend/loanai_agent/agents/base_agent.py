"""Base agent class and abstract interfaces."""

import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from loanai_agent.models import DecisionResult, LoanApplication
from loanai_agent.utils import AgentException, get_logger

logger = get_logger(__name__)


class BaseAgent(ABC):
    """Base class for all agents."""

    def __init__(
        self,
        name: str,
        description: str,
        model: str = "gemini-2.0-flash-exp",
        temperature: float = 0.1,
    ):
        """Initialize base agent.
        
        Args:
            name: Agent name identifier
            description: Agent description
            model: LLM model to use
            temperature: Temperature for model randomness
        """
        self.name = name
        self.description = description
        self.model = model
        self.temperature = temperature
        self.logger = get_logger(name)

    async def analyze(
        self, application: LoanApplication, **kwargs: Any
    ) -> Dict[str, Any]:
        """Analyze loan application - to be implemented by subclasses.
        
        Args:
            application: Loan application to analyze
            **kwargs: Additional arguments
            
        Returns:
            Analysis result dictionary
        """
        self.logger.info(f"Starting analysis for customer: {application.customer_id}")
        try:
            result = await self._perform_analysis(application, **kwargs)
            self.logger.info(f"Analysis completed for customer: {application.customer_id}")
            return result
        except Exception as e:
            self.logger.error(f"Analysis failed: {e}")
            raise AgentException(f"{self.name} analysis failed: {str(e)}")

    @abstractmethod
    async def _perform_analysis(
        self, application: LoanApplication, **kwargs: Any
    ) -> Dict[str, Any]:
        """Perform actual analysis - implemented by subclasses."""
        pass

    def get_system_prompt(self) -> str:
        """Get system prompt for the agent."""
        return f"You are a {self.description} agent. Be thorough and objective."

    def __repr__(self) -> str:
        """String representation of agent."""
        return f"{self.__class__.__name__}(name='{self.name}')"


class DecisionAgent(BaseAgent, ABC):
    """Base class for agents that make decisions."""

    async def make_decision(
        self, analysis_results: Dict[str, Any], context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make a decision based on analysis results.
        
        Args:
            analysis_results: Results from analysis
            context: Additional context for decision
            
        Returns:
            Decision result
        """
        self.logger.info(f"Making decision in {self.name}")
        try:
            decision = await self._generate_decision(analysis_results, context)
            return decision
        except Exception as e:
            self.logger.error(f"Decision generation failed: {e}")
            raise AgentException(f"Decision generation in {self.name} failed: {str(e)}")

    @abstractmethod
    async def _generate_decision(
        self, analysis_results: Dict[str, Any], context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Generate decision - implemented by subclasses."""
        pass


class AnalysisAgent(BaseAgent, ABC):
    """Base class for agents that perform analysis."""

    async def get_confidence_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate confidence score for analysis (0-1).
        
        Args:
            analysis: Analysis result
            
        Returns:
            Confidence score between 0 and 1
        """
        # Default implementation - can be overridden
        return analysis.get("confidence_score", 0.5)

    async def get_risk_score(self, analysis: Dict[str, Any]) -> int:
        """Calculate risk score for analysis (0-100).
        
        Args:
            analysis: Analysis result
            
        Returns:
            Risk score between 0 and 100
        """
        # Default implementation - can be overridden
        return analysis.get("risk_score", 50)

    async def get_recommendation(self, analysis: Dict[str, Any]) -> str:
        """Get recommendation from analysis.
        
        Args:
            analysis: Analysis result
            
        Returns:
            Recommendation string (approve, reject, review)
        """
        # Default implementation - can be overridden
        return analysis.get("recommendation", "review")
