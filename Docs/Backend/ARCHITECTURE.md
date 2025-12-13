# LoanAI Architecture Diagram

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (Next.js)                       │
│                                                                   │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌───────────┐│
│  │ Landing    │  │ Loan Form  │  │ Document   │  │  Result   ││
│  │ Page       │  │ (5 Steps)  │  │ Upload     │  │  Page     ││
│  └────────────┘  └────────────┘  └────────────┘  └───────────┘│
│                          │                │                      │
└──────────────────────────┼────────────────┼──────────────────────┘
                           │                │
                           ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND (API Routes)                        │
│                                                                   │
│  ┌──────────────────────────┐  ┌───────────────────────────┐   │
│  │ POST /api/loan-application│  │ POST /api/upload-document │   │
│  │  - Validate data          │  │  - Validate file type     │   │
│  │  - Create customer        │  │  - Check file size        │   │
│  │  - Save all info          │  │  - Upload to GCS          │   │
│  │  - Link documents         │  │  - Return file URL        │   │
│  │  - Return customer ID     │  │                           │   │
│  └──────────────────────────┘  └───────────────────────────┘   │
│           │                               │                      │
└───────────┼───────────────────────────────┼──────────────────────┘
            │                               │
            ▼                               ▼
┌─────────────────────────┐    ┌──────────────────────────────┐
│    DATABASE CLIENT      │    │    STORAGE CLIENT            │
│    (src/lib/db.ts)      │    │    (src/lib/storage.ts)      │
│                         │    │                              │
│  - Connection pool      │    │  - File upload               │
│  - Query helpers        │    │  - File deletion             │
│  - Transaction mgmt     │    │  - Signed URLs               │
│  - Error handling       │    │  - Bucket operations         │
└─────────────────────────┘    └──────────────────────────────┘
            │                               │
            ▼                               ▼
┌─────────────────────────┐    ┌──────────────────────────────┐
│   CLOUD SQL PROXY       │    │   GOOGLE CLOUD STORAGE       │
│   (localhost:5432)      │    │   (loanai-customer-docs)     │
└─────────────────────────┘    └──────────────────────────────┘
            │                               │
            ▼                               ▼
┌─────────────────────────┐    ┌──────────────────────────────┐
│   GOOGLE CLOUD SQL      │    │   GCS BUCKET                 │
│   PostgreSQL Database   │    │   Organized by customer ID   │
│                         │    │                              │
│   Tables:               │    │   Structure:                 │
│   - customers           │    │   customers/                 │
│   - customer_personal   │    │   ├── {uuid}/                │
│   - customer_education  │    │   │   ├── bank_statement.pdf │
│   - customer_employment │    │   │   └── salary_slip.pdf    │
│   - loan_applications   │    │   └── ...                    │
│   - customer_documents  │    │                              │
└─────────────────────────┘    └──────────────────────────────┘
```

## Data Flow - Application Submission

```
┌──────────┐
│  User    │
└────┬─────┘
     │ 1. Fill Form
     ▼
┌──────────────────────┐
│  Personal Info Step  │
│  - Name, ID, Gender  │
│  - Birth Year, Phone │
└──────────┬───────────┘
           │ 2. Next
           ▼
┌──────────────────────┐
│  Education Step      │
│  - Education Level   │
│  - University        │
└──────────┬───────────┘
           │ 3. Next
           ▼
┌──────────────────────┐
│  Employment Step     │
│  - Status, Company   │
│  - Salary, Experience│
└──────────┬───────────┘
           │ 4. Next
           ▼
┌──────────────────────┐
│  Loan Details Step   │
│  - Purpose, Amount   │
│  - Duration          │
└──────────┬───────────┘
           │ 5. Next
           ▼
┌──────────────────────┐
│  Documents Step      │
│  - Upload Bank Stmt  │────┐
│  - Upload Salary     │    │ 6. Upload Files
└──────────┬───────────┘    │
           │                 │
           │                 ▼
           │    ┌──────────────────────────┐
           │    │ POST /api/upload-document│
           │    │  - Validate file         │
           │    │  - Upload to GCS         │
           │    │  - Return URL            │
           │    └────────┬─────────────────┘
           │             │
           │             ▼
           │    ┌─────────────────┐
           │    │ Cloud Storage   │
           │    │ File saved      │
           │    └────────┬────────┘
           │             │
           │◄────────────┘ 7. File URLs returned
           │
           │ 8. Submit Application
           ▼
┌────────────────────────────────┐
│ POST /api/loan-application     │
│  - Receive all form data       │
│  - Begin transaction           │
│  - Insert customer             │
│  - Insert personal info        │
│  - Insert education            │
│  - Insert employment           │
│  - Insert loan application     │
│  - Insert document references  │
│  - Commit transaction          │
└──────────┬─────────────────────┘
           │ 9. Save to Database
           ▼
┌────────────────────────┐
│  Cloud SQL (Postgres)  │
│  All data persisted    │
└──────────┬─────────────┘
           │ 10. Return customer ID
           ▼
┌────────────────────────┐
│  Calculate Score       │
│  Display Result        │
└────────────────────────┘
```

## Database Schema Relationships

```
┌──────────────────────────┐
│       customers          │
│  PK: customer_id (UUID)  │
│      application_status  │
│      eligibility_score   │
│      created_at          │
│      updated_at          │
└────────┬─────────────────┘
         │
         │ 1:1
         ├────────────────┐
         │                │
         │                │
         ▼                ▼
┌─────────────────┐  ┌────────────────────┐
│personal_info    │  │   education        │
│  first_name     │  │   education_level  │
│  last_name      │  │   university       │
│  personal_id    │  └────────────────────┘
│  gender         │
│  birth_year     │       │
│  phone          │       │ 1:1
│  address        │       │
└─────────────────┘       ▼
                    ┌────────────────────┐
         │ 1:1      │   employment       │
         │          │   status           │
         ▼          │   company_name     │
┌─────────────────┐│   monthly_salary   │
│loan_applications││   experience_years │
│  loan_purpose   │└────────────────────┘
│  loan_amount    │
│  duration       │
│  additional_info│
└─────────────────┘
         │
         │ 1:N
         ▼
┌─────────────────┐
│   documents     │
│   document_type │
│   document_url  │
│   upload_date   │
└─────────────────┘
```

## Technology Stack

```
┌─────────────────────────────────┐
│         Frontend Layer           │
│  - Next.js 16                    │
│  - React 19                      │
│  - TypeScript                    │
│  - Tailwind CSS                  │
│  - Lucide Icons                  │
└─────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────┐
│       Application Layer          │
│  - Next.js API Routes            │
│  - Server Components             │
│  - API Middleware                │
└─────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────┐
│         Service Layer            │
│  - Database Client (pg)          │
│  - Storage Client (GCS SDK)      │
│  - Transaction Management        │
│  - Error Handling                │
└─────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────┐
│      Infrastructure Layer        │
│  - Google Cloud SQL (Postgres)   │
│  - Google Cloud Storage          │
│  - Cloud SQL Proxy               │
│  - Service Account Auth          │
└─────────────────────────────────┘
```

## Security Architecture

```
┌─────────────────────────────────────────┐
│              User Browser                │
└──────────────┬──────────────────────────┘
               │ HTTPS (Production)
               ▼
┌─────────────────────────────────────────┐
│         Next.js Application              │
│  - Input Validation                      │
│  - CORS Configuration                    │
│  - Rate Limiting (TODO)                  │
└──────────────┬──────────────────────────┘
               │
               ├─────────────────┐
               │                 │
               ▼                 ▼
┌──────────────────┐  ┌────────────────────┐
│   Database       │  │   Cloud Storage    │
│   - SSL/TLS      │  │   - Private Bucket │
│   - IAM Auth     │  │   - Signed URLs    │
│   - Firewall     │  │   - IAM Policies   │
│   - Encryption   │  │   - File Validation│
└──────────────────┘  └────────────────────┘
```

## Environment Configuration

```
┌─────────────────────────────────┐
│         .env (Local)             │
│  - Database credentials          │
│  - GCS bucket name               │
│  - Service account path          │
│  - API keys                      │
│  - Feature flags                 │
└─────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────┐
│    config/gcp-credentials.json   │
│  - Service account key           │
│  - Project ID                    │
│  - Client email                  │
└─────────────────────────────────┘
```

---

**Note**: This architecture is designed for scalability and can be enhanced with:
- Load balancing
- Caching layer (Redis)
- CDN for static assets
- API Gateway
- Monitoring & Logging
- AI/ML services integration
