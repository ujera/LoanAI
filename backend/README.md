# LoanAI Agent System - Backend

A sophisticated multi-agent loan processing system built with Google Agent Development Kit (ADK) for intelligent, automated loan application analysis and decision-making.

## 🏗️ Architecture Overview

```
Loan Officer Agent (Orchestrator)
    ├── Bank Statement Analysis Agent
    ├── Salary Statement Analysis Agent
    └── Verification Agent (MCP-Enabled)
         └── Communication Hub & Consensus Mechanism
```

## 📁 Project Structure

```
backend/
├── config/                          # Configuration files
│   ├── agent_config.yaml           # Agent configurations
│   └── settings.py                 # Application settings
├── loanai_agent/                   # Main application package
│   ├── agents/                     # Agent implementations
│   │   ├── __init__.py
│   │   ├── base_agent.py          # Base agent class
│   │   ├── loan_officer.py        # Loan Officer Agent
│   │   ├── bank_statement.py      # Bank Statement Analysis Agent
│   │   ├── salary_statement.py    # Salary Statement Analysis Agent
│   │   └── verification.py        # Verification Agent (MCP)
│   ├── models/                     # Pydantic models & schemas
│   │   ├── __init__.py
│   │   ├── schemas.py             # Data models
│   │   └── decision.py            # Decision models
│   ├── protocols/                  # Communication & consensus
│   │   ├── __init__.py
│   │   ├── communication.py       # Agent communication hub
│   │   ├── consensus.py           # Consensus building
│   │   └── decision_engine.py     # Decision logic
│   ├── tools/                      # Agent tools & utilities
│   │   ├── __init__.py
│   │   ├── document_processor.py  # OCR & document AI
│   │   ├── analysis_tools.py      # Financial analysis
│   │   └── verification_tools.py  # Web verification
│   ├── utils/                      # Utility functions
│   │   ├── __init__.py
│   │   ├── logger.py              # Logging setup
│   │   ├── exceptions.py          # Custom exceptions
│   │   └── helpers.py             # Helper functions
│   ├── __init__.py
│   └── main.py                     # Application entry point
├── tests/                          # Unit and integration tests
│   ├── __init__.py
│   ├── conftest.py                # Pytest fixtures
│   ├── test_agents.py
│   ├── test_models.py
│   └── test_protocols.py
├── logs/                           # Application logs
├── .env.example                    # Environment template
├── .gitignore
├── pyproject.toml                  # Project metadata & dependencies
├── requirements.txt                # Pip dependencies
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Google Cloud Project with ADK enabled
- Google API credentials

### Installation

1. **Clone the repository**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   # Or with development dependencies:
   pip install -e ".[dev]"
   ```

4. **Setup environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

5. **Configure Google Cloud credentials**
   ```bash
   mkdir -p config
   # Place your GCP credentials JSON file at config/gcp-credentials.json
   ```

### Running the Application

```bash
python -m loanai_agent.main
```

### Development

**Code formatting and linting:**
```bash
black loanai_agent/
isort loanai_agent/
ruff check loanai_agent/
```

**Type checking:**
```bash
mypy loanai_agent/
```

**Run tests:**
```bash
pytest tests/ -v --cov=loanai_agent
```

## 🤖 Agent Architecture

### Loan Officer Agent
- **Role**: Chief decision-maker and orchestrator
- **Responsibilities**: Task distribution, result aggregation, final decision-making
- **Model**: Gemini 2.0 Flash (low temperature for consistency)

### Bank Statement Analysis Agent
- **Role**: Financial history analyzer
- **Responsibilities**: OCR extraction, transaction analysis, income verification
- **Outputs**: Income metrics, expense patterns, fraud detection

### Salary Statement Analysis Agent
- **Role**: Employment and income verifier
- **Responsibilities**: Employment validation, salary verification, stability assessment
- **Outputs**: Employment verification, salary consistency, job security score

### Verification Agent
- **Role**: External data validator (MCP-enabled)
- **Responsibilities**: University verification, company validation, address verification
- **Tools**: Brave Search, Google Maps, Clearbit APIs

## 📊 Data Models

### LoanApplication
```python
customer_id: str
personal_info: PersonalInfo
education: Education
employment: Employment
loan_request: LoanRequest
documents: List[DocumentInfo]
```

### DecisionResult
```python
decision: str  # APPROVED, REJECTED, MANUAL_REVIEW
confidence_score: float
risk_score: int
loan_amount: Optional[float]
interest_rate: Optional[float]
reasoning: str
detailed_report: Dict
```

## 🔄 Processing Flow

1. **Phase 1**: Task distribution to sub-agents
2. **Phase 2**: Parallel analysis execution
3. **Phase 3**: Inter-agent deliberation
4. **Phase 4**: Consensus building
5. **Phase 5**: Final decision by Loan Officer

## 🛡️ Risk Scoring

Risk scores range from 0-100:
- **0-20**: LOW (Auto-approve)
- **21-40**: MODERATE-LOW (Auto-approve)
- **41-60**: MODERATE (Manual review)
- **61-75**: MODERATE-HIGH (Auto-reject)
- **76-100**: HIGH (Auto-reject)

## 📝 Configuration

See `.env.example` for all available configuration options.

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_agents.py

# Run with coverage
pytest --cov=loanai_agent --cov-report=html
```

## 📚 Documentation

- [Agent Architecture](../Docs/Loan-agent-architacture.md)
- [Data Flow](../Docs/Agent-Dataflow.md)
- [Database Schema](../Docs/Database-overview.md)

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Run tests and linting
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🙋 Support

For issues and questions, please refer to the project documentation or create an issue on GitHub.
