# LoanAI Quick Reference Sheet

## ⚡ Commands

### Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate          # macOS/Linux
# or
venv\Scripts\activate             # Windows
pip install -r requirements.txt
cp .env.example .env
```

### Run Demo
```bash
python demo.py
```

### Run Tests
```bash
pytest tests/ -v
pytest tests/ --cov=loanai_agent
pytest tests/test_models.py::test_name
```

### Code Quality
```bash
black loanai_agent/
isort loanai_agent/
ruff check loanai_agent/
mypy loanai_agent/
```

### View Logs
```bash
tail -f logs/loanai.log
tail -f logs/loanai_errors.log
```

## 📦 Key Imports

```python
# Main processor
from loanai_agent.main import LoanApplicationProcessor

# Agents
from loanai_agent.agents import (
    BankStatementAgent,
    SalaryStatementAgent,
    VerificationAgent,
    LoanOfficerAgent,
)

# Models
from loanai_agent.models import (
    LoanApplication,
    DecisionResult,
    PersonalInfo,
    Employment,
    Education,
)

# Protocols
from loanai_agent.protocols import (
    AgentCommunicationHub,
    RiskScoringEngine,
    DecisionEngine,
)

# Utilities
from loanai_agent.utils import (
    get_logger,
    generate_correlation_id,
)
```

## 🏃 Basic Usage Pattern

```python
import asyncio
from loanai_agent.main import LoanApplicationProcessor
from loanai_agent.models import LoanApplication

async def main():
    # 1. Initialize
    processor = LoanApplicationProcessor()
    
    # 2. Create application
    app = LoanApplication(...)
    
    # 3. Process
    decision = await processor.process(app)
    
    # 4. Use results
    print(f"Decision: {decision.decision}")
    print(f"Risk: {decision.risk_score}")
    print(f"Reason: {decision.reasoning}")

asyncio.run(main())
```

## 📊 Decision Values

```
APPROVED      - Loan approved with terms
REJECTED      - Loan rejected
MANUAL_REVIEW - Requires human review
```

## ⚠️ Risk Scores

```
0-20    → LOW           → APPROVED
21-40   → MODERATE_LOW  → APPROVED
41-60   → MODERATE      → MANUAL_REVIEW
61-75   → MODERATE_HIGH → REJECTED
76-100  → HIGH          → REJECTED
```

## 🔧 Configuration

### Environment Variables (.env)
```
GCP_PROJECT_ID=your-project
GOOGLE_API_KEY=your-key
ADK_TEMPERATURE=0.1
ADK_MAX_TOKENS=4096
LOG_LEVEL=DEBUG
ENABLE_DOCUMENT_AI=true
```

### Agent Configuration (agent_config.yaml)
- Modify agent system prompts
- Set LLM parameters
- Configure risk thresholds
- Define override conditions

## 📁 File Organization

```
loanai_agent/
├── agents/          # Agent implementations
├── models/          # Data models
├── protocols/       # Communication & decisions
├── tools/           # Analysis tools
└── utils/           # Helper functions

tests/               # Unit tests
config/              # Configuration
logs/                # Application logs
```

## 🆘 Common Issues

| Issue | Solution |
|-------|----------|
| ImportError | Activate venv: `source venv/bin/activate` |
| No module named X | Install: `pip install X` |
| Google auth fails | Set GOOGLE_APPLICATION_CREDENTIALS |
| Pydantic validation error | Check required fields |
| Async error | Use `await` or `asyncio.run()` |

## 🎯 Agent Methods

### All Agents
```python
agent.analyze(application)              # Analyze application
agent.get_system_prompt()                # Get agent prompt
```

### Analysis Agents
```python
agent.get_confidence_score(analysis)     # Get confidence
agent.get_risk_score(analysis)           # Get risk score
agent.get_recommendation(analysis)       # Get recommendation
```

### Loan Officer Agent
```python
agent.make_decision(analysis, context)   # Make decision
```

## 📋 Decision Result Fields

```python
decision.decision           # APPROVED, REJECTED, MANUAL_REVIEW
decision.confidence_score   # 0.0 - 1.0
decision.risk_score         # 0 - 100
decision.loan_amount        # Approved amount (if approved)
decision.interest_rate      # Interest rate %
decision.loan_duration      # Duration in months
decision.conditions         # List of conditions
decision.reasoning          # Detailed explanation
decision.bank_analysis      # Bank agent results
decision.salary_analysis    # Salary agent results
decision.verification_analysis  # Verification results
decision.consensus          # Agent consensus info
```

## 🔌 Creating New Agent

```python
from loanai_agent.agents import AnalysisAgent

class MyAgent(AnalysisAgent):
    def __init__(self):
        super().__init__(
            name="my_agent",
            description="My custom agent",
        )
    
    async def _perform_analysis(self, app, **kwargs):
        # Your analysis logic
        return {
            'confidence_score': 0.85,
            'risk_score': 35,
            'recommendation': 'approve',
            'reasoning': 'Your reasoning here',
        }
```

## 🧰 Common Helpers

```python
from loanai_agent.utils import (
    get_logger,                              # Get logger
    generate_correlation_id(),               # UUID string
    format_currency(1000),                   # "$1,000.00"
    calculate_debt_to_income_ratio(5000, 1500),  # DTI %
    calculate_savings_rate(5000, 3000),     # Savings %
    calculate_age(1990),                     # Age from year
)
```

## 🔑 Quick Tips

1. **Enable Debug Logging**
   ```
   LOG_LEVEL=DEBUG
   ```

2. **Skip Agent Certification**
   - Agents return simulated results in demo

3. **Check Error Logs**
   ```
   tail logs/loanai_errors.log
   ```

4. **Type Check Your Code**
   ```bash
   mypy loanai_agent/
   ```

5. **Format Code Before Commit**
   ```bash
   black loanai_agent/ && isort loanai_agent/
   ```

## 📞 Getting Help

1. Check `README.md` for overview
2. Read `USAGE.md` for setup help
3. Review `ARCHITECTURE.md` for design info
4. Check `demo.py` for examples
5. View logs for error details

## 🎓 Code Examples

### Example: Custom Risk Calculator
```python
from loanai_agent.protocols import RiskScoringEngine

risk = RiskScoringEngine.calculate_aggregate_risk(
    bank_risk=25,
    salary_risk=30,
    verification_risk=20,
    loan_details={
        'loan_amount': 50000,
        'loan_duration': 60,
        'loan_purpose': 'personal',
    }
)
print(f"Total Risk: {risk['total_risk_score']}")
```

### Example: Manual Decision
```python
from loanai_agent.protocols import DecisionEngine
from loanai_agent.models import DecisionStatus

decision = DecisionEngine.make_decision(
    risk_score=45,
    confidence_score=0.75,
    consensus_recommendation='review',
    red_flags=['salary_variance'],
)
print(f"Decision: {decision.value}")  # MANUAL_REVIEW
```

---

**Pro Tip**: Save this file in your IDE bookmarks for quick reference!
