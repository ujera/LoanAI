# LoanAI Multi-Agent System Architecture
## Intelligent Loan Application Processing with Google ADK

**Document Version**: 1.0  
**Date**: December 13, 2025  
**Architecture Type**: Hierarchical Multi-Agent System  
**Framework**: Google Agent Development Kit (ADK)

---

## Table of Contents
1. System Overview
2. Agent Architecture
3. Data Flow & Communication
4. Implementation with Google ADK
5. MCP Integration
6. Decision Framework
7. Security & Compliance

---

## 1. System Overview

### 1.1 Architecture Pattern
**Hierarchical Multi-Agent System with Collaborative Decision Making**

```
                    ┌─────────────────────────────┐
                    │   LOAN OFFICER AGENT        │
                    │   (Main Orchestrator)       │
                    │   - Final Decision Maker    │
                    │   - Risk Assessment         │
                    │   - Compliance Check        │
                    └─────────────┬───────────────┘
                                  │
                    ┌─────────────┴───────────────┐
                    │    Agent Communication      │
                    │    & Collaboration Layer    │
                    └─────────────┬───────────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
┌───────▼────────┐    ┌──────────▼──────────┐   ┌─────────▼─────────┐
│  BANK STATEMENT│    │ SALARY STATEMENT    │   │ VERIFICATION      │
│  ANALYSIS AGENT│    │ ANALYSIS AGENT      │   │ AGENT (MCP)       │
│                │    │                     │   │                   │
│ • OCR Extract  │    │ • OCR Extract       │   │ • University      │
│ • Verify Income│    │ • Verify Employment │   │ • Company         │
│ • Pattern Check│    │ • Income Validation │   │ • Address         │
│ • Risk Score   │    │ • Employment Status │   │ • Identity        │
└────────────────┘    └─────────────────────┘   └───────────────────┘
        │                         │                         │
        └─────────────────────────┼─────────────────────────┘
                                  │
                    ┌─────────────▼───────────────┐
                    │   CONSENSUS & DELIBERATION  │
                    │   MECHANISM                 │
                    │   - Agent Discussion        │
                    │   - Conflict Resolution     │
                    │   - Confidence Scoring      │
                    └─────────────────────────────┘
```

### 1.2 System Objectives
- **Automated Decision Making**: Process loan applications with minimal human intervention
- **Multi-Source Verification**: Cross-validate customer data from multiple sources
- **Intelligent Risk Assessment**: Calculate risk scores based on comprehensive analysis
- **Explainable AI**: Provide detailed reasoning for every decision
- **Fraud Detection**: Identify inconsistencies and potential fraud

---

## 2. Agent Architecture

### 2.1 Main Agent: Loan Officer Agent

**Role**: Chief Decision Maker & Orchestrator

**Responsibilities**:
- Orchestrate all sub-agents
- Aggregate sub-agent results
- Make final approval/rejection decision
- Generate comprehensive decision report
- Handle edge cases and exceptions
- Ensure compliance with lending regulations

**Input Data Sources**:
```json
{
  "personal_info": {
    "first_name": "string",
    "last_name": "string",
    "personal_id": "string",
    "gender": "enum",
    "birth_year": "string",
    "phone": "string",
    "address": "string"
  },
  "education": {
    "education_level": "enum",
    "university": "string"
  },
  "employment": {
    "employment_status": "enum",
    "company_name": "string",
    "monthly_salary": "number",
    "experience_years": "number"
  },
  "loan_request": {
    "loan_purpose": "enum",
    "loan_duration": "number",
    "loan_amount": "number",
    "additional_info": "text"
  }
}
```

**Decision Factors**:
1. Sub-agent consensus score (40%)
2. Debt-to-Income ratio (25%)
3. Document verification status (20%)
4. External verification results (15%)

**Google ADK Configuration**:
```python
from google.adk import Agent, AgentConfig, LLMConfig

loan_officer_config = AgentConfig(
    name="loan_officer_agent",
    description="Senior loan officer responsible for final loan decisions",
    llm_config=LLMConfig(
        model="gemini-2.0-flash-exp",
        temperature=0.2,  # Low temperature for consistent decisions
        max_tokens=4096
    ),
    system_prompt="""You are a senior loan officer with 20 years of experience.
    Your role is to review loan applications, analyze sub-agent reports, and make
    final decisions. You must be fair, thorough, and compliant with regulations.
    Always provide detailed explanations for your decisions.""",
    tools=[
        "aggregate_sub_agent_results",
        "calculate_risk_score",
        "check_compliance",
        "generate_decision_report"
    ]
)
```

---

### 2.2 Sub-Agent 1: Bank Statement Analysis Agent

**Role**: Financial History Analyzer

**Responsibilities**:
- Extract data from bank statements (OCR)
- Analyze transaction patterns
- Calculate average monthly balance
- Identify income sources and frequency
- Detect unusual activities or red flags
- Verify stated salary vs actual deposits

**Input Data**:
- Bank statement document (PDF/Image) from Cloud Storage
- Self-reported monthly salary for verification
- Loan amount requested

**Analysis Output**:
```json
{
  "agent_name": "bank_statement_agent",
  "confidence_score": 0.85,
  "analysis_result": {
    "document_authenticity": "verified",
    "average_monthly_balance": 12500.00,
    "average_monthly_income": 5200.00,
    "income_consistency": "high",
    "expense_patterns": {
      "total_monthly_expenses": 3800.00,
      "recurring_obligations": 1200.00,
      "discretionary_spending": 2600.00
    },
    "red_flags": [],
    "savings_behavior": "positive",
    "debt_indicators": {
      "credit_card_payments": 300.00,
      "loan_payments": 500.00
    }
  },
  "recommendation": "approve",
  "reasoning": "Consistent income, healthy savings, manageable expenses",
  "risk_score": 15  // out of 100 (lower is better)
}
```

**Google ADK Configuration**:
```python
from google.adk import Agent, AgentConfig, Tool
from google.cloud import vision, documentai

bank_statement_config = AgentConfig(
    name="bank_statement_agent",
    description="Expert in analyzing bank statements and financial patterns",
    llm_config=LLMConfig(
        model="gemini-2.0-flash-exp",
        temperature=0.1,
        max_tokens=2048
    ),
    system_prompt="""You are a financial analyst specialized in bank statement analysis.
    Extract and analyze financial data, identify patterns, detect fraud, and assess
    financial health. Be thorough and detail-oriented.""",
    tools=[
        Tool(name="ocr_extract", function=extract_document_text),
        Tool(name="pattern_analysis", function=analyze_transaction_patterns),
        Tool(name="fraud_detection", function=detect_anomalies),
        Tool(name="income_verification", function=verify_income_consistency)
    ]
)
```

**Key Metrics Calculated**:
- **Income Stability Index** (ISI): Measures consistency of income over 3 months
- **Expense-to-Income Ratio** (EIR): Total expenses / Total income
- **Savings Rate**: (Income - Expenses) / Income
- **Debt Service Coverage**: (Income - Expenses) / Existing Debt Payments

---

### 2.3 Sub-Agent 2: Salary Statement Analysis Agent

**Role**: Employment & Income Verifier

**Responsibilities**:
- Extract data from salary slips/payslips
- Verify employment status and duration
- Validate employer information
- Cross-check salary with self-reported data
- Analyze tax deductions and benefits
- Identify employment stability

**Input Data**:
- Salary statement document (PDF/Image) from Cloud Storage
- Self-reported company name and salary
- Employment status and experience years

**Analysis Output**:
```json
{
  "agent_name": "salary_statement_agent",
  "confidence_score": 0.92,
  "analysis_result": {
    "document_authenticity": "verified",
    "employer_name": "Tech Solutions Inc.",
    "employee_name": "John Doe",
    "employee_id": "EMP12345",
    "gross_salary": 5500.00,
    "net_salary": 4200.00,
    "employment_period": "2019-03-01 to present",
    "employment_duration_months": 69,
    "deductions": {
      "tax": 900.00,
      "social_security": 250.00,
      "health_insurance": 150.00
    },
    "benefits": [
      "401k matching",
      "health insurance",
      "performance bonus"
    ],
    "consistency_check": {
      "matches_self_reported": true,
      "salary_variance": 0.02,
      "employment_status_verified": true
    }
  },
  "recommendation": "approve",
  "reasoning": "Stable employment, verified income, legitimate employer",
  "risk_score": 10
}
```

**Google ADK Configuration**:
```python
salary_statement_config = AgentConfig(
    name="salary_statement_agent",
    description="Expert in employment verification and salary analysis",
    llm_config=LLMConfig(
        model="gemini-2.0-flash-exp",
        temperature=0.1,
        max_tokens=2048
    ),
    system_prompt="""You are an HR and employment verification specialist.
    Analyze salary statements, verify employment details, and assess employment
    stability. Cross-reference with self-reported data to identify discrepancies.""",
    tools=[
        Tool(name="ocr_extract", function=extract_salary_document),
        Tool(name="employer_validation", function=validate_employer),
        Tool(name="salary_verification", function=cross_check_salary),
        Tool(name="employment_stability", function=calculate_stability_score)
    ]
)
```

---

### 2.4 Sub-Agent 3: Verification Agent (MCP-Enabled)

**Role**: External Data Verifier & Web Intelligence Gatherer

**Responsibilities**:
- Verify university reputation and accreditation (via web search)
- Validate company existence and legitimacy
- Check employer reviews and financial health
- Verify address authenticity
- Cross-reference identity information
- Gather market intelligence for salary benchmarking

**Input Data**:
- University name
- Company name
- Address
- Education level
- Job title/role (if available)

**MCP Tools Required**:
```yaml
mcp_servers:
  web_search:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-brave-search"]
    env:
      BRAVE_API_KEY: "${BRAVE_API_KEY}"
  
  geocoding:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-google-maps"]
    env:
      GOOGLE_MAPS_API_KEY: "${GOOGLE_MAPS_API_KEY}"
  
  company_data:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-clearbit"]
    env:
      CLEARBIT_API_KEY: "${CLEARBIT_API_KEY}"
```

**Analysis Output**:
```json
{
  "agent_name": "verification_agent",
  "confidence_score": 0.88,
  "verification_results": {
    "university_verification": {
      "name": "Stanford University",
      "accreditation_status": "accredited",
      "ranking": {
        "world_rank": 3,
        "national_rank": 2
      },
      "reputation_score": 98,
      "legitimacy": "verified",
      "sources": [
        "QS World Rankings",
        "Official university website",
        "Department of Education"
      ]
    },
    "company_verification": {
      "name": "Tech Solutions Inc.",
      "industry": "Information Technology",
      "employee_count": "500-1000",
      "founded_year": 2010,
      "financial_health": "stable",
      "glassdoor_rating": 4.2,
      "legitimacy": "verified",
      "website": "https://techsolutions.com",
      "address_match": true
    },
    "address_verification": {
      "address": "123 Main St, San Francisco, CA",
      "geocoded": true,
      "valid": true,
      "residential_type": "apartment",
      "area_type": "urban"
    },
    "salary_benchmark": {
      "position_estimated": "Software Engineer",
      "market_salary_range": {
        "min": 4500,
        "median": 5800,
        "max": 8500
      },
      "reported_salary": 5200,
      "salary_percentile": 55,
      "reasonable": true
    }
  },
  "recommendation": "approve",
  "reasoning": "All external verifications passed. Reputable university, legitimate employer, valid address",
  "risk_score": 8
}
```

**Google ADK Configuration with MCP**:
```python
from google.adk import Agent, AgentConfig, MCPClient

verification_config = AgentConfig(
    name="verification_agent",
    description="External verification specialist using web search and APIs",
    llm_config=LLMConfig(
        model="gemini-2.0-flash-exp",
        temperature=0.2,
        max_tokens=3072
    ),
    system_prompt="""You are a verification specialist with access to web search
    and external APIs. Your job is to verify customer-provided information using
    reliable external sources. Be thorough and cite your sources.""",
    mcp_clients=[
        MCPClient(name="brave_search", server="web_search"),
        MCPClient(name="google_maps", server="geocoding"),
        MCPClient(name="clearbit", server="company_data")
    ],
    tools=[
        Tool(name="search_university", function=verify_university_reputation),
        Tool(name="search_company", function=verify_company_legitimacy),
        Tool(name="validate_address", function=geocode_and_validate_address),
        Tool(name="benchmark_salary", function=get_market_salary_data)
    ]
)
```

**MCP Search Queries**:
```python
# University Verification
university_queries = [
    f"Is {university_name} an accredited university?",
    f"{university_name} world ranking",
    f"{university_name} official website",
    f"{university_name} department of education"
]

# Company Verification
company_queries = [
    f"{company_name} company profile",
    f"{company_name} glassdoor reviews",
    f"{company_name} linkedin company",
    f"Is {company_name} a legitimate company?"
]

# Salary Benchmarking
salary_queries = [
    f"average salary {job_title} {location}",
    f"salary range {company_name} {job_title}",
    f"{industry} salary statistics {location}"
]
```

---
