"""Agents package initialization."""

from loanai_agent.agents.bank_statement import BankStatementAgent
from loanai_agent.agents.base_agent import (
    AnalysisAgent,
    BaseAgent,
    DecisionAgent,
)
from loanai_agent.agents.loan_officer import LoanOfficerAgent
from loanai_agent.agents.salary_statement import SalaryStatementAgent
from loanai_agent.agents.verification import VerificationAgent

__all__ = [
    "BaseAgent",
    "AnalysisAgent",
    "DecisionAgent",
    "LoanOfficerAgent",
    "BankStatementAgent",
    "SalaryStatementAgent",
    "VerificationAgent",
]
