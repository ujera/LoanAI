# LoanAI Backend

Backend infrastructure for the LoanAI application, connecting the Next.js frontend with Google Cloud SQL (PostgreSQL) and Google Cloud Storage.

## Architecture

### Technology Stack
- **Database**: PostgreSQL on Google Cloud SQL
- **Storage**: Google Cloud Storage
- **ORM**: Native `pg` library
- **Framework**: Next.js API Routes

### Database Schema

The database consists of 6 main tables:

1. **customers** - Main customer records with application status
2. **customer_personal_info** - Personal information (name, ID, gender, etc.)
3. **customer_education** - Education details (level, university)
4. **customer_employment** - Employment information (status, company, salary)
5. **loan_applications** - Loan details (amount, purpose, duration)
6. **customer_documents** - Document references (stored in GCS)

### API Endpoints

#### POST `/api/loan-application`
Submit a new loan application with all customer data.

**Request Body:**
```json
{
  "firstName": "string",
  "lastName": "string",
  "personalId": "string",
  "gender": "string",
  "birthYear": "string",
  "phone": "string",
  "address": "string",
  "educationLevel": "string",
  "university": "string",
  "employmentStatus": "string",
  "companyName": "string",
  "monthlySalary": "string",
  "experienceYears": "string",
  "loanPurpose": "string",
  "loanDuration": "string",
  "loanAmount": "string",
  "additionalInfo": "string",
  "bankStatementUrl": "string",
  "salaryStatementUrl": "string"
}
```

**Response:**
```json
{
  "success": true,
  "customerId": "uuid",
  "message": "Loan application submitted successfully"
}
```

#### GET `/api/loan-application?customerId={uuid}`
Retrieve a specific loan application by customer ID.

#### GET `/api/loan-application`
Retrieve all loan applications (latest 100).

#### POST `/api/upload-document`
Upload a document to Google Cloud Storage.

**Request:** `multipart/form-data`
- `file`: File object
- `documentType`: string (e.g., "bank_statement", "salary_statement")
- `customerId`: string (optional, for organizing uploads)

**Response:**
```json
{
  "success": true,
  "fileUrl": "gs://bucket-name/path/to/file",
  "fileName": "original-filename.pdf",
  "documentType": "bank_statement",
  "destination": "customers/uuid/document_type_timestamp.pdf"
}
```

#### DELETE `/api/upload-document?filePath={path}`
Delete a document from Google Cloud Storage.

## Setup Instructions

### Prerequisites

1. **Google Cloud SQL Proxy** must be running:
```bash
./cloud_sql_proxy -instances=PROJECT_ID:REGION:INSTANCE_NAME=tcp:5432
```

2. **Environment Variables** (`.env` file):
```env
# Database Configuration
DB_HOST=127.0.0.1
DB_PORT=5432
DB_USER=loanai_user
DB_PASSWORD=loanai_password
DB_NAME=loanai

# Google Cloud Storage
GCS_BUCKET_NAME=loanai-customer-documents-dev
GCS_PROJECT_ID=fourth-flag-481108-s5
GOOGLE_APPLICATION_CREDENTIALS=./config/gcp-credentials.json
```

3. **Google Cloud Credentials**:
   - Place your service account JSON key in `config/gcp-credentials.json`
   - Ensure the service account has:
     - Cloud SQL Client role
     - Storage Object Admin role for the bucket

### Database Setup

1. Create the database schema:
```bash
psql -h 127.0.0.1 -U loanai_user -d loanai -f schema.sql
```

2. Verify tables:
```bash
psql -h 127.0.0.1 -U loanai_user -d loanai -c "\dt"
```

### Storage Setup

1. Create the bucket:
```bash
gcloud storage buckets create gs://loanai-customer-documents-dev \
    --location=us-central1 \
    --uniform-bucket-level-access
```

2. Grant permissions:
```bash
gcloud storage buckets add-iam-policy-binding gs://loanai-customer-documents-dev \
    --member="serviceAccount:loanai-sa@PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.objectAdmin"
```

## Development

### Running the Application

1. Install dependencies:
```bash
npm install
```

2. Start Cloud SQL Proxy (in a separate terminal):
```bash
cd config
./cloud_sql_proxy -instances=fourth-flag-481108-s5:us-central1:loanai-db-dev=tcp:5432
```

3. Run the development server:
```bash
npm run dev
```

4. Access the application at `http://localhost:3000`

### Testing the Backend

#### Test Database Connection
```bash
psql -h 127.0.0.1 -U loanai_user -d loanai -c "SELECT version();"
```

#### Test Storage Access
```bash
gcloud storage ls gs://loanai-customer-documents-dev/
```

## File Structure

```
src/
├── app/
│   └── api/
│       ├── loan-application/
│       │   └── route.ts          # Main loan application API
│       └── upload-document/
│           └── route.ts          # Document upload API
├── lib/
│   ├── db.ts                     # PostgreSQL client
│   └── storage.ts                # Google Cloud Storage client
└── types/
    └── form.ts                   # TypeScript interfaces
```

## Security Considerations

1. **Never commit credentials** - `.env` and `config/gcp-credentials.json` are in `.gitignore`
2. **Input validation** - All API endpoints validate input data
3. **SQL injection prevention** - Using parameterized queries
4. **File type validation** - Only allowed file types can be uploaded
5. **File size limits** - Maximum 10MB per file
6. **Signed URLs** - Use signed URLs for accessing private documents

## Troubleshooting

### Database Connection Issues
- Ensure Cloud SQL Proxy is running
- Check database credentials in `.env`
- Verify network connectivity to Cloud SQL instance

### Storage Upload Issues
- Verify service account has `Storage Object Admin` role
- Check bucket name in `.env`
- Ensure `GOOGLE_APPLICATION_CREDENTIALS` path is correct

### API Errors
- Check browser console for detailed error messages
- Review server logs in the terminal running `npm run dev`
- Verify all required fields are being sent in requests

## Next Steps

1. **AI Integration**: Connect Google ADK for eligibility scoring
2. **Document AI**: Implement document verification with Document AI
3. **Consensus Building**: Add multi-agent consensus mechanism
4. **Admin Dashboard**: Create interface for reviewing applications
5. **Email Notifications**: Send confirmation emails to applicants
