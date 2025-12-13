"""LoanAI Quick Start and Development Setup.

This file provides setup instructions for the LoanAI backend system.
"""

# Quick Start Guide
## Installation Steps

### 1. Prerequisites
- Python 3.11 or higher
- pip package manager
- Virtual environment tool (venv)

### 2. Clone and Navigate
```bash
cd backend
```

### 3. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 4. Install Dependencies
```bash
# Install from requirements.txt
pip install -r requirements.txt

# Or install from pyproject.toml with dev dependencies
pip install -e ".[dev]"
```

### 5. Setup Environment Variables
```bash
cp .env.example .env
# Edit .env with your actual credentials
```

### 6. Create Google Cloud Credentials (if using GCP)
```bash
mkdir -p config
# Place your GCP service account JSON file at:
# config/gcp-credentials.json
```

## Running the Demo Application

```bash
python demo.py
```

This will:
1. Create a sample loan application
2. Run it through the multi-agent system
3. Display the analysis from each agent
4. Show the final decision with reasoning

## Project Structure

```
backend/
├── config/
│   ├── __init__.py
│   ├── settings.py              # Configuration settings
│   ├── agent_config.yaml        # Agent configurations
│   └── gcp-credentials.json     # GCP credentials (add your own)
├── loanai_agent/
│   ├── agents/                  # Agent implementations
│   │   ├── base_agent.py
│   │   ├── loan_officer.py
│   │   ├── bank_statement.py
│   │   ├── salary_statement.py
│   │   └── verification.py
│   ├── models/                  # Data models
│   │   ├── schemas.py           # Pydantic schemas
│   │   └── decision.py          # Decision models
│   ├── protocols/               # Communication protocols
│   │   ├── communication.py     # Agent communication hub
│   │   └── decision_engine.py   # Risk scoring & decisions
│   ├── tools/                   # Agent tools
│   │   ├── analysis_tools.py
│   │   ├── verification_tools.py
│   │   └── document_processor.py
│   ├── utils/                   # Utilities
│   │   ├── logger.py
│   │   ├── exceptions.py
│   │   └── helpers.py
│   ├── main.py                  # Main orchestrator
│   └── __init__.py
├── tests/                       # Unit tests
├── logs/                        # Application logs
├── demo.py                      # Demo script
├── api_examples.py              # Usage examples
├── pyproject.toml               # Project metadata
├── requirements.txt             # Dependencies
├── .env.example                 # Environment template
└── README.md
```

## Key Concepts

### Multi-Agent Architecture

The system uses 4 main agents:

1. **Loan Officer Agent** - Main orchestrator, makes final decisions
2. **Bank Statement Agent** - Analyzes financial history
3. **Salary Statement Agent** - Verifies employment and income
4. **Verification Agent** - External verification (universities, companies, addresses)

### Processing Pipeline

1. **Phase 1**: Parallel analysis from all agents
2. **Phase 2**: Inter-agent deliberation
3. **Phase 3**: Consensus building
4. **Phase 4**: Final decision by Loan Officer

### Risk Scoring

Risk scores range from 0-100:
- **0-20**: LOW - Auto-approve
- **21-40**: MODERATE-LOW - Auto-approve
- **41-60**: MODERATE - Manual review
- **61-75**: MODERATE-HIGH - Auto-reject
- **76-100**: HIGH - Auto-reject

## Using the System

### Basic Usage

```python
import asyncio
from loanai_agent.main import LoanApplicationProcessor
from loanai_agent.models import LoanApplication, PersonalInfo, ...

async def process_loan():
    processor = LoanApplicationProcessor()
    
    # Create application
    application = LoanApplication(...)
    
    # Process
    decision = await processor.process(application)
    
    print(f"Decision: {decision.decision}")
    print(f"Risk Score: {decision.risk_score}")
    print(f"Reasoning: {decision.reasoning}")

asyncio.run(process_loan())
```

### Accessing Agent Results

```python
# After processing
decision = await processor.process(application)

# Individual agent analyses
bank_analysis = decision.bank_analysis
salary_analysis = decision.salary_analysis
verification_analysis = decision.verification_analysis

# Consensus result
consensus = decision.consensus

# Detailed report
report = decision.detailed_report
```

## Development

### Running Tests

```bash
pytest tests/ -v
pytest tests/ --cov=loanai_agent  # With coverage
```

### Code Formatting

```bash
black loanai_agent/
isort loanai_agent/
ruff check loanai_agent/
```

### Type Checking

```bash
mypy loanai_agent/
```

## Configuration

See `.env.example` for available configuration options:

- `GCP_PROJECT_ID` - Google Cloud project ID
- `GOOGLE_API_KEY` - Google API key
- `ADK_TEMPERATURE` - Model temperature (0.0-1.0)
- `ADK_MAX_TOKENS` - Maximum tokens for model
- `LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)
- `ENABLE_DOCUMENT_AI` - Enable Document AI processing
- `ENABLE_MCP_VERIFICATION` - Enable MCP-based verification

## Logging

Logs are stored in:
- `logs/loanai.log` - All logs
- `logs/loanai_errors.log` - Error logs only

Change log level in `.env`:
```
LOG_LEVEL=DEBUG  # or INFO, WARNING, ERROR
```

## Troubleshooting

### Import Errors
```bash
# Ensure you're in the correct directory
cd backend

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Missing Dependencies
```bash
# Install specific package
pip install google-adk
pip install pydantic
pip install loguru
```

### Google Cloud Setup Issues
```bash
# Verify credentials file exists
ls config/gcp-credentials.json

# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS=./config/gcp-credentials.json
```

## Next Steps

1. Explore `demo.py` to understand the system
2. Review `api_examples.py` for integration patterns
3. Check `tests/` for example usage
4. Read the agent documentation in `Docs/`

## Support

For issues and questions:
1. Check the documentation in `Docs/`
2. Review error messages in `logs/`
3. Check test files for examples
4. Refer to agent system prompts for behavior details
"""

# Quick Reference

## Demo Script
```bash
python demo.py
```

## View Logs
```bash
tail -f logs/loanai.log
```

## Run Tests
```bash
pytest tests/
```

## Format Code
```bash
black loanai_agent/ && isort loanai_agent/
```

## View Help
```python
from loanai_agent.main import LoanApplicationProcessor
help(LoanApplicationProcessor)
```
