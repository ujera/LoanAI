# LoanAI - Intelligent Loan Eligibility System

An AI-powered loan application platform built with Next.js, Google Cloud SQL, and Google Cloud Storage. This application enables users to apply for loans through an intuitive multi-step form, with automatic document upload and eligibility assessment.

## 🌟 Features

- **Multi-Step Loan Application Form**
  - Personal Information Collection
  - Education Background
  - Employment Details
  - Loan Requirements
  - Document Upload (Bank & Salary Statements)

- **Cloud-Native Backend**
  - Google Cloud SQL (PostgreSQL) for data persistence
  - Google Cloud Storage for document management
  - Transaction-based data integrity
  - Real-time file uploads

- **Modern Tech Stack**
  - Next.js 16 with App Router
  - React 19 with Server Components
  - TypeScript for type safety
  - Tailwind CSS for styling

- **Security Features**
  - Input validation
  - File type & size restrictions
  - Parameterized database queries
  - Secure credential management

## 📋 Prerequisites

Before you begin, ensure you have:

- Node.js 20+ installed
- Google Cloud Platform account
- Cloud SQL instance with PostgreSQL
- Cloud Storage bucket
- Service account with appropriate permissions
- Cloud SQL Proxy executable

## 🚀 Quick Start

### 1. Clone and Install

```bash
git clone <your-repo-url>
cd LoanAI
npm install
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

Required environment variables:
- `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`
- `GCS_BUCKET_NAME`, `GCS_PROJECT_ID`
- `GOOGLE_APPLICATION_CREDENTIALS`

### 3. Add GCP Credentials

Place your service account JSON key at:
```
config/gcp-credentials.json
```

### 4. Start Cloud SQL Proxy

In a separate terminal:
```bash
cd config
./cloud_sql_proxy -instances=PROJECT_ID:REGION:INSTANCE=tcp:5432
```

### 5. Test Backend

```bash
npm run test:backend
```

### 6. Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to see the application.

## 📁 Project Structure

```
LoanAI/
├── src/
│   ├── app/
│   │   ├── api/
│   │   │   ├── loan-application/   # Main application API
│   │   │   └── upload-document/    # File upload API
│   │   ├── about/                  # About page
│   │   ├── contact/                # Contact page
│   │   └── ...
│   ├── components/
│   │   ├── feature/                # Core feature components
│   │   │   ├── LoanForm.tsx
│   │   │   ├── steps/              # Form step components
│   │   │   └── ...
│   │   ├── layout/                 # Layout components
│   │   └── ui/                     # Reusable UI components
│   ├── lib/
│   │   ├── db.ts                   # Database client
│   │   └── storage.ts              # Cloud Storage client
│   └── types/
│       └── form.ts                 # TypeScript interfaces
├── scripts/
│   ├── test-backend.js             # Backend health check
│   └── database-queries.sql        # Utility SQL queries
├── config/
│   └── gcp-credentials.json        # GCP service account key
├── .env                            # Environment variables
├── QUICKSTART.md                   # Quick start guide
├── BACKEND_README.md               # Backend documentation
├── ARCHITECTURE.md                 # System architecture
└── DEPLOYMENT_CHECKLIST.md         # Deployment guide
```

## 🔌 API Endpoints

### POST `/api/loan-application`
Submit a complete loan application with customer data.

**Request Body:**
```json
{
  "firstName": "John",
  "lastName": "Doe",
  "personalId": "123456789",
  "gender": "male",
  "birthYear": "1990",
  "phone": "+1234567890",
  "address": "123 Main St",
  "educationLevel": "bachelor",
  "university": "University Name",
  "employmentStatus": "employed",
  "companyName": "Company Inc",
  "monthlySalary": "5000",
  "experienceYears": "5",
  "loanPurpose": "personal",
  "loanAmount": "10000",
  "loanDuration": "24",
  "bankStatementUrl": "gs://bucket/path",
  "salaryStatementUrl": "gs://bucket/path"
}
```

### POST `/api/upload-document`
Upload documents to Cloud Storage.

**Request:** `multipart/form-data`
- `file`: File object
- `documentType`: Document type identifier

## 🗄️ Database Schema

### Tables
- `customers` - Main customer records
- `customer_personal_info` - Personal information
- `customer_education` - Education details
- `customer_employment` - Employment information
- `loan_applications` - Loan requests
- `customer_documents` - Document references

See [BACKEND_README.md](./BACKEND_README.md) for detailed schema.

## 🛠️ Development

### Available Scripts

```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Run ESLint
npm run test:backend # Test backend connectivity
npm run db:connect   # Connect to database
```

### Testing

```bash
# Test backend health
npm run test:backend

# Connect to database
npm run db:connect

# View application logs
tail -f .next/server/app-paths.json
```

## 📚 Documentation

- **[QUICKSTART.md](./QUICKSTART.md)** - Quick setup guide
- **[BACKEND_README.md](./BACKEND_README.md)** - Comprehensive backend documentation
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - System architecture diagrams
- **[DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md)** - Production deployment guide
- **[IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md)** - Implementation details

## 🔒 Security

- Environment variables for sensitive data
- Parameterized database queries (SQL injection prevention)
- File type and size validation
- Secure credential storage
- Transaction-based data integrity
- `.gitignore` for sensitive files

## 🚀 Deployment

### Production Checklist
1. Update environment variables for production
2. Enable Cloud SQL SSL/TLS
3. Configure HTTPS
4. Set up monitoring and logging
5. Configure backup strategy
6. Test rollback procedures

See [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md) for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Next.js team for the amazing framework
- Google Cloud Platform for infrastructure
- React team for the UI library

## 📞 Support

For issues and questions:
- Check the [documentation](./BACKEND_README.md)
- Review the [troubleshooting guide](./QUICKSTART.md#troubleshooting)
- Open an issue on GitHub

---

**Built with ❤️ using Next.js, Google Cloud SQL, and Google Cloud Storage**
