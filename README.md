# LoanAI - Intelligent Loan Eligibility System

An AI-powered loan application platform built with Next.js, Google Cloud SQL, Google Cloud Storage, and a Multi-Agent AI system. This application enables users to apply for loans through an intuitive multi-step form, with automatic document upload and intelligent AI-driven loan decisions.

## 🌟 Features

- **Multi-Step Loan Application Form**
  - Personal Information Collection
  - Education Background
  - Employment Details
  - Loan Requirements
  - Document Upload (Bank & Salary Statements)

- **AI Multi-Agent Processing System** ⭐ NEW
  - Bank Statement Analysis Agent
  - Salary Statement Verification Agent
  - External Verification Agent
  - Loan Officer Decision Agent
  - Intelligent risk scoring and loan recommendations
  - Detailed reasoning and explanations

- **Cloud-Native Backend**
  - Google Cloud SQL (PostgreSQL) for data persistence
  - Google Cloud Storage for document management
  - Transaction-based data integrity
  - Real-time file uploads
  - Integration with AI Agent API

- **Modern Tech Stack**
  - Next.js 16 with App Router
  - React 19 with Server Components
  - TypeScript for type safety
  - Tailwind CSS for styling
  - FastAPI for AI Agent API
  - Python 3.11+ with Google ADK

- **Security Features**
  - Input validation
  - File type & size restrictions
  - Parameterized database queries
  - Secure credential management

## 📋 Prerequisites

Before you begin, ensure you have:

- Node.js 20+ installed
- Python 3.11+ installed
- Google Cloud Platform account
- Cloud SQL instance with PostgreSQL
- Cloud Storage bucket
- Service account with appropriate permissions
- Cloud SQL Proxy executable

## 🚀 Quick Start

### Easy Start (Recommended)

Start all services with a single command:

```bash
# Make sure you have .env file configured
./start-all.sh
```

This will start:
- ✅ Cloud SQL Proxy (Port 5432)
- ✅ AI Agent API Server (Port 8000)  
- ✅ Next.js Application (Port 3000)

Access the application at: **http://localhost:3000**

To stop all services:
```bash
./stop-all.sh
# or press Ctrl+C in the terminal
```

### Manual Setup

If you prefer to start services individually:

### 1. Clone and Install

```bash
git clone <your-repo-url>
cd LoanAI
npm install

# Install Python dependencies for AI Agent
cd AI_agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
cd ..
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

Required environment variables:
- `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`
- `GCS_BUCKET_NAME`, `GCS_PROJECT_ID`
- `AI_AGENT_API_URL` (default: http://localhost:8000)
- `GOOGLE_APPLICATION_CREDENTIALS`

### 3. Add GCP Credentials

Place your service account JSON key at:
```
config/gcp-credentials.json
```

### 4. Setup Cloud SQL Proxy (if not already done)

```bash
cd config
./setup-proxy.sh
cd ..
```

### 5. Start All Services

```bash
./start-all.sh
```

Or start them individually:

**Terminal 1 - Cloud SQL Proxy:**
```bash
cd config
./cloud_sql_proxy --port 5432 PROJECT_ID:REGION:INSTANCE
```

**Terminal 2 - AI Agent API:**
```bash
cd AI_agent
./start_server.sh
```

**Terminal 3 - Next.js:**
```bash
npm run dev
```

### 6. Access the Application

Open [http://localhost:3000](http://localhost:3000) to see the application.

AI Agent API documentation: [http://localhost:8000/docs](http://localhost:8000/docs)

## 🏗️ System Architecture

```
Customer → Next.js Frontend → Next.js Backend API → Cloud SQL Database
                                      ↓
                                AI Agent API (Port 8000)
                                      ↓
                            Multi-Agent System
                    (Bank, Salary, Verification Agents)
                                      ↓
                            Loan Officer Decision
                                      ↓
                              Decision Result
```

For detailed architecture, see: `INTEGRATION.md`

## 📁 Project Structure

```
LoanAI/
├── src/
│   ├── app/
│   │   ├── api/
│   │   │   ├── loan-application/   # Main application API + AI integration
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
├── AI_agent/                       # ⭐ AI Multi-Agent System
│   ├── api_server.py               # FastAPI server
│   ├── services/                   # Data transformation services
│   ├── loanai_agent/              # Agent system code
│   │   ├── agents/                # Individual agents
│   │   ├── models/                # Data models
│   │   ├── protocols/             # Communication protocols
│   │   └── main.py                # Application orchestrator
│   ├── config/                    # Agent configuration
│   ├── requirements.txt           # Python dependencies
│   └── start_server.sh            # Start AI Agent API
├── config/
│   ├── gcp-credentials.json       # GCP service account
│   ├── cloud_sql_proxy            # Proxy executable
│   └── setup-proxy.sh             # Proxy setup script
├── Docs/                          # Documentation
│   ├── Backend/                   # Backend documentation
│   └── Agent/                     # AI Agent documentation
├── logs/                          # Service logs
├── scripts/
│   ├── test-backend.js            # Backend health check
│   └── database-queries.sql        # Utility SQL queries
├── config/
│   └── gcp-credentials.json        # GCP service account key
├── start-all.sh                    # ⭐ Master startup script
├── stop-all.sh                     # Stop all services
├── .env                            # Environment variables
├── QUICK_START.md                  # ⭐ Quick reference guide
├── INTEGRATION.md                  # ⭐ Integration documentation
└── README.md                       # This file
```

## 🔌 API Endpoints

### Backend API (Next.js - Port 3000)

#### POST `/api/loan-application`
Submit a complete loan application with customer data. Data is saved to Cloud SQL and automatically sent to AI Agent system for processing.

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

**Response:**
```json
{
  "success": true,
  "customerId": "uuid",
  "message": "Loan application submitted successfully and sent for AI processing"
}
```

#### POST `/api/upload-document`
Upload documents to Cloud Storage.

**Request:** `multipart/form-data`
- `file`: File object
- `documentType`: Document type identifier

### AI Agent API (FastAPI - Port 8000)

#### POST `/api/process`
Process loan application through multi-agent system (async).

#### GET `/api/result/{customerId}`
Get AI decision result for a customer.

#### GET `/api/status/{customerId}`
Check processing status (pending/completed/failed).

#### GET `/health`
Health check endpoint.

#### GET `/docs`
Interactive API documentation (Swagger UI).

## 🗄️ Database Schema

### Tables
- `customers` - Main customer records with AI decision results
- `customer_personal_info` - Personal information
- `customer_education` - Education details
- `customer_employment` - Employment information
- `loan_applications` - Loan requests
- `customer_documents` - Document references

See `Docs/Backend/` for detailed schema.

## 🛠️ Development

### Available Scripts

```bash
# Start all services
./start-all.sh       # Start everything (recommended)
./stop-all.sh        # Stop all services

# Individual services
npm run dev          # Start Next.js only
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Run ESLint
npm run test:backend # Test backend connectivity
npm run db:connect   # Connect to database

# AI Agent
cd AI_agent && ./start_server.sh  # Start AI Agent API
```

### Testing

```bash
# Test backend health
npm run test:backend

# Test AI Agent health
curl http://localhost:8000/health

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
