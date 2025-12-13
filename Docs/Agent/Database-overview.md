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