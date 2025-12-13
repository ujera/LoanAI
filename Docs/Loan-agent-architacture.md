# LoanAI Customer Data Documentation
## Database Schema for Google Cloud Platform

### Overview
This document outlines all customer data collected through the LoanAI loan eligibility application. The data is collected in a 5-step form process.

---

## 1. Customer Tables Structure

### 1.1 Main Customer Table: `customers`

| Field Name | Data Type | Required | Description | Validation Notes |
|------------|-----------|----------|-------------|------------------|
| `customer_id` | STRING (UUID) | Yes | Primary key, auto-generated | Unique identifier |
| `created_at` | TIMESTAMP | Yes | Record creation timestamp | Auto-generated |
| `updated_at` | TIMESTAMP | Yes | Last update timestamp | Auto-updated |
| `application_status` | STRING | Yes | Status of loan application | ENUM: pending, approved, rejected, processing |
| `eligibility_score` | INTEGER | No | Calculated eligibility score (0-100) | Computed after submission |

---

### 1.2 Personal Information Table: `customer_personal_info`

**Step 1: Personal Details**

| Field Name | Data Type | Required | Description | Input Type | Example |
|------------|-----------|----------|-------------|------------|---------|
| `customer_id` | STRING (UUID) | Yes | Foreign key to customers table | - | - |
| `first_name` | STRING | Yes | Customer's first name | Text input | "John" |
| `last_name` | STRING | Yes | Customer's last name | Text input | "Doe" |
| `personal_id` | STRING | Yes | National ID/SSN | Text input | "1234567890" |
| `gender` | STRING | Yes | Customer's gender | Select | male, female, other |
| `birth_year` | STRING | Yes | Year of birth | Number input | "1990" |
| `phone` | STRING | Yes | Contact phone number | Tel input | "+1 234 567 890" |
| `address` | STRING | Yes | Residential address | Text input | "123 Main St, City, Country" |

**Enums for `gender`:**
- `male`
- `female`
- `other`

---

### 1.3 Education Information Table: `customer_education`

**Step 2: Education Details**

| Field Name | Data Type | Required | Description | Input Type | Options |
|------------|-----------|----------|-------------|------------|---------|
| `customer_id` | STRING (UUID) | Yes | Foreign key to customers table | - | - |
| `education_level` | STRING | Yes | Highest education level | Select dropdown | high_school, bachelor, master, phd |
| `university` | STRING | Yes | Name of educational institution | Text input | "University of ..." |

**Enums for `education_level`:**
- `high_school` - High School
- `bachelor` - Bachelor's Degree
- `master` - Master's Degree
- `phd` - PhD

---

### 1.4 Employment Information Table: `customer_employment`

**Step 3: Employment Details**

| Field Name | Data Type | Required | Description | Input Type | Options/Example |
|------------|-----------|----------|-------------|------------|-----------------|
| `customer_id` | STRING (UUID) | Yes | Foreign key to customers table | - | - |
| `employment_status` | STRING | Yes | Current employment status | Select dropdown | employed, self_employed, unemployed |
| `company_name` | STRING | Conditional* | Name of employer | Text input | "Company Ltd." |
| `monthly_salary` | NUMERIC(10,2) | Conditional* | Monthly income in USD | Number input | 5000.00 |
| `experience_years` | INTEGER | Conditional* | Years of work experience | Number input | 3 |

**Conditional Requirements:**
- `company_name`, `monthly_salary`, and `experience_years` are **required** when `employment_status` is NOT "unemployed"

**Enums for `employment_status`:**
- `employed` - Full-time/Part-time Employment
- `self_employed` - Self-employed/Freelancer
- `unemployed` - Currently Unemployed

---

### 1.5 Loan Details Table: `loan_applications`

**Step 4: Loan Request Details**

| Field Name | Data Type | Required | Description | Input Type | Options/Example |
|------------|-----------|----------|-------------|------------|-----------------|
| `loan_application_id` | STRING (UUID) | Yes | Primary key for loan application | - | Auto-generated |
| `customer_id` | STRING (UUID) | Yes | Foreign key to customers table | - | - |
| `loan_purpose` | STRING | Yes | Purpose of the loan | Select dropdown | mortgage, vehicle, personal, education, business, others |
| `loan_duration` | INTEGER | Yes | Loan term in months | Number input | 24 |
| `loan_amount` | NUMERIC(12,2) | Yes | Requested loan amount in USD | Number input | 10000.00 |
| `additional_info` | TEXT | No | Additional notes from customer | Textarea (optional) | Free text description |
| `application_date` | TIMESTAMP | Yes | When application was submitted | - | Auto-generated |

**Enums for `loan_purpose`:**
- `mortgage` - Home/Mortgage Loan
- `vehicle` - Vehicle/Car Loan
- `personal` - Personal Loan
- `education` - Education/Student Loan
- `business` - Business Loan
- `others` - Other Purposes

---

### 1.6 Documents Table: `customer_documents`

**Step 5: Supporting Documents**

| Field Name | Data Type | Required | Description | Input Type | File Types Accepted |
|------------|-----------|----------|-------------|------------|---------------------|
| `document_id` | STRING (UUID) | Yes | Primary key for document | - | Auto-generated |
| `customer_id` | STRING (UUID) | Yes | Foreign key to customers table | - | - |
| `document_type` | STRING | Yes | Type of document | - | bank_statement, salary_statement |
| `file_name` | STRING | Yes | Original file name | File upload | Various |
| `file_path` | STRING | Yes | Cloud storage path/URL | - | GCS bucket path |
| `file_size` | INTEGER | Yes | File size in bytes | - | Auto-captured |
| `mime_type` | STRING | Yes | File MIME type | - | application/pdf, image/png, image/jpeg |
| `uploaded_at` | TIMESTAMP | Yes | Upload timestamp | - | Auto-generated |

**Document Types Required:**
1. **Bank Statement** - Latest 3 months of bank statements
   - Accepted formats: PDF, PNG, JPG, JPEG
   - Field in form: `bankStatementName`
   
2. **Salary Statement** - Latest payslip or employment proof
   - Accepted formats: PDF, PNG, JPG, JPEG
   - Field in form: `salaryStatementName`

---

## 2. Google Cloud Storage Structure

### 2.1 Cloud Storage Buckets

```
gs://loanai-customer-documents-[environment]/
├── bank-statements/
│   └── {customer_id}/
│       └── {timestamp}_{original_filename}
└── salary-statements/
    └── {customer_id}/
        └── {timestamp}_{original_filename}
```

**Bucket Configuration:**
- **Bucket Name**: `loanai-customer-documents-production`
- **Region**: Multi-region (US, EU, or ASIA based on compliance requirements)
- **Storage Class**: Standard
- **Access Control**: Uniform bucket-level access
- **Lifecycle Rules**: 
  - Archive to Coldline after 90 days
  - Delete after 7 years (or per regulatory requirements)

**Security:**
- Encryption at rest: Google-managed encryption keys
- IAM roles: Limited to application service account
- Signed URLs for temporary access (expires in 1 hour)

---

## 3. Database Relationships

```
customers (1) ──→ (1) customer_personal_info
customers (1) ──→ (1) customer_education
customers (1) ──→ (1) customer_employment
customers (1) ──→ (1..n) loan_applications
customers (1) ──→ (1..n) customer_documents
```

---

## 4. Google Cloud SQL Setup Recommendations

### 4.1 Database Configuration
- **Database Type**: Cloud SQL (PostgreSQL 15+ or MySQL 8.0+)
- **Instance Tier**: db-n1-standard-2 (minimum for production)
- **Storage**: 100GB SSD with automatic storage increase
- **Backups**: Automated daily backups with 7-day retention
- **High Availability**: Enable for production environment

### 4.2 Indexes Recommendations
```sql
-- Primary indexes (automatic)
-- customer_id on all tables

-- Performance indexes
CREATE INDEX idx_customer_personal_id ON customer_personal_info(personal_id);
CREATE INDEX idx_customer_phone ON customer_personal_info(phone);
CREATE INDEX idx_customer_email ON customer_personal_info(email); -- if added
CREATE INDEX idx_loan_application_date ON loan_applications(application_date);
CREATE INDEX idx_loan_status ON customers(application_status);
CREATE INDEX idx_document_type ON customer_documents(document_type);
```

### 4.3 Data Privacy & Compliance
- **PII Fields** (require encryption): 
  - `personal_id`, `phone`, `address`, `first_name`, `last_name`
- **Sensitive Fields**:
  - `monthly_salary`, `bank_statement`, `salary_statement`
- **Compliance**: GDPR, CCPA, SOC 2
- **Data Retention**: Configure per regulatory requirements
- **Audit Logging**: Enable Cloud Audit Logs

---

## 5. Summary Statistics

| Category | Field Count | Required Fields | Optional Fields |
|----------|-------------|-----------------|-----------------|
| Personal Information | 7 | 7 | 0 |
| Education | 2 | 2 | 0 |
| Employment | 4 | 1 | 3 (conditional) |
| Loan Details | 4 | 3 | 1 |
| Documents | 2 | 2 | 0 |
| **Total** | **19** | **15-18*** | **1-4*** |

*Conditional on employment status

---

## 6. Data Flow

1. **Data Collection**: Customer fills out 5-step form
2. **Validation**: Frontend validates all required fields per step
3. **File Upload**: Documents uploaded to Cloud Storage
4. **Database Insert**: Customer data inserted into Cloud SQL
5. **Score Calculation**: Eligibility score computed (50-100 range)
6. **Result**: Customer receives instant eligibility score

---

## 7. API Endpoints (Recommended)

```
POST /api/customers                    # Create customer record
POST /api/customers/{id}/documents     # Upload documents
GET  /api/customers/{id}              # Retrieve customer data
PUT  /api/customers/{id}              # Update customer data
POST /api/loan-applications           # Submit loan application
GET  /api/loan-applications/{id}      # Get application status
```

---

**Document Version**: 1.0  
**Last Updated**: December 13, 2025  
**Prepared for**: LoanAI Google Cloud Database Setup

kurta17: Imagine you are Senior AI engineer, you need to disgin AI agent system which handles all of the data and makes the dicision to approve the costumer application or reject. for that you need one Main AI agent Loan officer which has sub agents. Sub agent salary agent gets salary documents analyzies it and give result back to Loan officer, Sub agnet salary slip document Agent analyzies documents and send back result to Loan officer, Sub agent Self reported Ai agent gets and analyzes it use MCP to performe web search to verify let's say how good is the university which customer reported or the company he works, etc. those sub agents should comunicate each other disscuss and come up final results with reported explanation of the result. So for that use google ADK and use best practices!
Use the previos message to analyze the data we have for agents! give me markdown format! 

GitHub Copilot: I'll design a comprehensive multi-agent AI system for loan application processing using Google's Agent Development Kit (ADK) and best practices. Let me analyze the data structure and create a detailed architecture document. 

Read [](file:///Users/maxsolutions/Documents/GitHub/LoanAI/Docs/Database_overview.md#1-1), lines 1 to 50

Now I'll create a comprehensive multi-agent AI system architecture document:

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
