# LoanAI - Quick Start Guide

## 🚀 Backend Setup Complete!

Your LoanAI backend is now configured and ready to use with:
- ✅ Google Cloud SQL (PostgreSQL)
- ✅ Google Cloud Storage
- ✅ Next.js API Routes

## Prerequisites Checklist

Before running the application, ensure you have:

- [ ] Cloud SQL Proxy running
- [ ] Valid `.env` file with all credentials
- [ ] Service account JSON key in `config/gcp-credentials.json`
- [ ] Database schema created in Cloud SQL
- [ ] Cloud Storage bucket created and configured

## Step-by-Step Setup

### 1. Start Cloud SQL Proxy

Open a **new terminal window** and run:

```bash
cd config
./cloud_sql_proxy -instances=fourth-flag-481108-s5:us-central1:loanai-db-dev=tcp:5432
```

Keep this terminal running in the background.

### 2. Test Backend Connectivity

In your main terminal:

```bash
npm run test:backend
```

This will verify:
- ✅ Environment variables are set
- ✅ Database connection works
- ✅ Cloud Storage bucket is accessible

### 3. Run Development Server

```bash
npm run dev
```

Access the application at: http://localhost:3000

## Testing the Application

### Frontend Flow:
1. Fill out the loan application form (5 steps)
2. Upload required documents (bank statement, salary statement)
3. Submit the application
4. View eligibility score

### Backend Flow:
- Files are uploaded to Cloud Storage via `/api/upload-document`
- Form data is saved to Cloud SQL via `/api/loan-application`
- All data is stored with proper relationships and constraints

## API Endpoints

### POST `/api/loan-application`
Submit a complete loan application with all customer data.

### GET `/api/loan-application?customerId={uuid}`
Retrieve a specific application by customer ID.

### POST `/api/upload-document`
Upload documents (PDF, images) to Cloud Storage.

### DELETE `/api/upload-document?filePath={path}`
Delete a document from Cloud Storage.

## Useful Commands

```bash
# Test backend health
npm run test:backend

# Connect to database directly
npm run db:connect

# View database tables
psql -h 127.0.0.1 -U loanai_user -d loanai -c "\dt"

# List files in storage bucket
gcloud storage ls gs://loanai-customer-documents-dev/

# Start development server
npm run dev
```

## Project Structure

```
LoanAI/
├── src/
│   ├── app/
│   │   ├── api/
│   │   │   ├── loan-application/route.ts    # Main API endpoint
│   │   │   └── upload-document/route.ts     # File upload endpoint
│   │   └── ...                              # Next.js pages
│   ├── components/                          # React components
│   ├── lib/
│   │   ├── db.ts                           # PostgreSQL client
│   │   └── storage.ts                      # Cloud Storage client
│   └── types/                              # TypeScript interfaces
├── config/
│   └── gcp-credentials.json                # Service account key
├── scripts/
│   └── test-backend.js                     # Health check script
├── .env                                    # Environment variables
└── BACKEND_README.md                       # Detailed documentation
```

## Troubleshooting

### "Database connection failed"
- Ensure Cloud SQL Proxy is running
- Check credentials in `.env` file
- Verify database exists: `psql -h 127.0.0.1 -U loanai_user -l`

### "Storage bucket not found"
- Verify `GCS_BUCKET_NAME` in `.env`
- Check bucket exists: `gcloud storage ls`
- Ensure service account has Storage Object Admin role

### "Cannot find module"
- Run `npm install` to install all dependencies

### "Permission denied"
- Make test script executable: `chmod +x scripts/test-backend.js`
- Check service account permissions in GCP Console

## Next Steps

1. **Test the complete flow**: Submit a loan application through the UI
2. **Verify data in database**: Check that records are created properly
3. **Check uploaded files**: Verify documents appear in Cloud Storage
4. **Review logs**: Monitor console output for any errors

## Database Schema

The application uses 6 tables:

1. `customers` - Main customer records
2. `customer_personal_info` - Personal details
3. `customer_education` - Education history
4. `customer_employment` - Employment details
5. `loan_applications` - Loan requests
6. `customer_documents` - Document references

See `BACKEND_README.md` for detailed schema information.

## Security Notes

- ⚠️ Never commit `.env` or `gcp-credentials.json`
- ⚠️ Database credentials are for development only
- ⚠️ Use signed URLs for production document access
- ⚠️ Enable HTTPS for production deployments

## Support

For detailed backend documentation, see: `BACKEND_README.md`

---

**Status**: ✅ Backend is fully configured and ready to use!
