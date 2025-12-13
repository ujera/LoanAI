"""Custom exceptions for the LoanAI application."""


class LoanAIException(Exception):
    """Base exception for LoanAI."""

    pass


class AgentException(LoanAIException):
    """Exception raised by agents."""

    pass


class CommunicationException(LoanAIException):
    """Exception raised during agent communication."""

    pass


class ConsensusException(LoanAIException):
    """Exception raised during consensus building."""

    pass


class DocumentProcessingException(LoanAIException):
    """Exception raised during document processing."""

    pass


class VerificationException(LoanAIException):
    """Exception raised during verification."""

    pass


class DecisionException(LoanAIException):
    """Exception raised during decision making."""

    pass


class ValidationException(LoanAIException):
    """Exception raised during data validation."""

    pass


class TimeoutException(LoanAIException):
    """Exception raised when operation times out."""

    pass


class ConfigurationException(LoanAIException):
    """Exception raised due to configuration issues."""

    pass
