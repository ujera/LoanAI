"""Prompt templates for document processing with structured output."""

from jinja2 import Template
from pydantic import BaseModel, Field
from typing import List, Optional


# ==================== Structured Data Models ====================


class TransactionData(BaseModel):
    """Individual transaction from bank statement."""
    
    date: str = Field(description="Transaction date in YYYY-MM-DD format")
    description: str = Field(description="Transaction description")
    amount: float = Field(description="Transaction amount (positive for credits, negative for debits)")
    type: str = Field(description="Transaction type: 'credit' or 'debit'")
    balance: Optional[float] = Field(None, description="Balance after transaction")


class BankStatementData(BaseModel):
    """Structured bank statement data extracted from document."""
    
    account_holder: str = Field(description="Full name of account holder")
    account_number: str = Field(description="Last 4 digits of account number (masked)")
    bank_name: Optional[str] = Field(None, description="Name of the bank")
    statement_period: str = Field(description="Statement period (e.g., 'Jan 2024 - Mar 2024')")
    opening_balance: float = Field(description="Opening balance at start of period")
    closing_balance: float = Field(description="Closing balance at end of period")
    total_credits: float = Field(description="Total amount credited during period")
    total_debits: float = Field(description="Total amount debited during period")
    transactions: List[TransactionData] = Field(default_factory=list, description="List of transactions")
    currency: str = Field(default="USD", description="Currency code")


class SalaryStatementData(BaseModel):
    """Structured salary statement data extracted from document."""
    
    employee_name: str = Field(description="Full name of employee")
    employee_id: Optional[str] = Field(None, description="Employee ID")
    employer_name: str = Field(description="Name of employer/company")
    designation: Optional[str] = Field(None, description="Job designation/title")
    basic_salary: float = Field(description="Basic salary amount")
    allowances: float = Field(default=0.0, description="Total allowances")
    deductions: float = Field(default=0.0, description="Total deductions")
    net_salary: float = Field(description="Net salary after deductions")
    pay_period: str = Field(description="Pay period (e.g., 'March 2024')")
    payment_date: Optional[str] = Field(None, description="Payment date")
    currency: str = Field(default="USD", description="Currency code")


# ==================== Prompt Templates ====================


BANK_STATEMENT_PROMPT = Template("""Analyze this bank statement document and extract structured information.

**INSTRUCTIONS:**
1. Extract ALL information accurately from the document
2. For amounts, use ONLY numbers (no currency symbols, no commas)
3. For dates, use YYYY-MM-DD format
4. For transactions: positive amounts for credits, negative for debits
5. Mask account number - show only last 4 digits
6. Return ONLY valid JSON matching the schema below

**REQUIRED JSON SCHEMA:**
```json
{{ schema }}
```

**REQUIREMENTS:**
- opening_balance: Numeric value only
- closing_balance: Numeric value only
- total_credits: Sum of all credit transactions
- total_debits: Sum of all debit transactions (as positive number)
- transactions: Array with at least 3 most recent transactions
- Each transaction must have: date, description, amount, type

**IMPORTANT:** 
- Be precise with numbers - no approximations
- Extract actual data from the document
- If data is unclear, use null for optional fields
- Ensure all numeric fields are actual numbers, not strings

Return ONLY the JSON object, no additional text.""")


SALARY_STATEMENT_PROMPT = Template("""Analyze this salary statement/payslip document and extract structured information.

**INSTRUCTIONS:**
1. Extract employee and employer information accurately
2. Use ONLY numbers for salary amounts (no currency symbols, no commas)
3. Calculate net_salary = basic_salary + allowances - deductions
4. Return ONLY valid JSON matching the schema below

**REQUIRED JSON SCHEMA:**
```json
{{ schema }}
```

**REQUIREMENTS:**
- employee_name: Full name as shown on document
- employer_name: Company/organization name
- basic_salary: Base salary amount (numeric)
- allowances: Total of all allowances (numeric)
- deductions: Total of all deductions (numeric)
- net_salary: Final take-home amount (numeric)
- pay_period: Month and year (e.g., "March 2024")

**IMPORTANT:**
- Be precise with numbers - no approximations
- Extract actual data from the document
- If optional field is unclear, use null
- Ensure numeric fields contain only numbers

Return ONLY the JSON object, no additional text.""")


DOCUMENT_VERIFICATION_PROMPT = Template("""Analyze this {{ document_type }} document for authenticity and quality.

**VERIFICATION CHECKS:**
1. Document quality and readability
2. Presence of official elements (logos, stamps, signatures)
3. Consistency of information
4. Signs of tampering or modification
5. Date validity and recency

**ASSESSMENT CRITERIA:**
- authentic: Document appears genuine and unaltered
- suspicious: Potential red flags detected
- unclear: Poor quality or missing critical information

Return assessment as JSON:
```json
{
  "authenticity": "authentic|suspicious|unclear",
  "quality_score": 0-100,
  "red_flags": ["list of any concerns"],
  "missing_elements": ["list of missing required elements"],
  "confidence": 0.0-1.0,
  "notes": "brief explanation"
}
```

Be objective and thorough in your assessment.""")


# ==================== Template Registry ====================


class PromptTemplates:
    """Registry of all prompt templates."""
    
    BANK_STATEMENT = BANK_STATEMENT_PROMPT
    SALARY_STATEMENT = SALARY_STATEMENT_PROMPT
    DOCUMENT_VERIFICATION = DOCUMENT_VERIFICATION_PROMPT
    
    @classmethod
    def get_template(cls, template_name: str) -> Template:
        """Get template by name.
        
        Args:
            template_name: Name of template
            
        Returns:
            Jinja2 Template object
            
        Raises:
            ValueError: If template not found
        """
        templates = {
            "bank_statement": cls.BANK_STATEMENT,
            "salary_statement": cls.SALARY_STATEMENT,
            "verification": cls.DOCUMENT_VERIFICATION,
        }
        
        template = templates.get(template_name.lower())
        if not template:
            raise ValueError(f"Template '{template_name}' not found")
        
        return template
