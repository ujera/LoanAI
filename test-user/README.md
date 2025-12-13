# Test User Submission

This directory contains scripts to submit test user data to the backend API and verify the AI agent integration.

## Test User Information

- **Name**: Luka Narsia
- **Personal ID**: 0XX010XXXX
- **Employer**: GeoTech Solutions LLC
- **Position**: Software Engineer
- **Payment Date**: March 5, 2025
- **Currency**: GEL
- **Monthly Salary**: 3,500 GEL
- **Loan Amount**: 15,000 GEL
- **Loan Duration**: 24 months

## Prerequisites

Before running the test script, ensure:

1. **Backend server is running**:
   ```bash
   cd /Users/maxsolutions/Documents/GitHub/LoanAI
   npm run dev
   ```

2. **Cloud SQL Proxy is running**:
   ```bash
   cd /Users/maxsolutions/Documents/GitHub/LoanAI
   ./start-proxy.sh
   ```

3. **AI Agent is running** (optional, but recommended):
   ```bash
   cd /Users/maxsolutions/Documents/GitHub/LoanAI/AI_agent
   python api_server.py
   ```

## Available Scripts

### 1. Submit Test User

Submit the Luka Narsia test user to the backend:

#### Using the automated script (Recommended):
```bash
cd /Users/maxsolutions/Documents/GitHub/LoanAI/test-user
./run-test.sh
```

#### Using Node.js:
```bash
cd /Users/maxsolutions/Documents/GitHub/LoanAI/test-user
node submit-test-user.js
```

#### Using Python:
```bash
cd /Users/maxsolutions/Documents/GitHub/LoanAI/test-user
python3 submit-test-user.py
```

### 2. Verify AI Integration Fix

Test that the AI agent properly updates the application status in the database:

```bash
cd /Users/maxsolutions/Documents/GitHub/LoanAI/test-user
./verify-fix.sh
```

This script will:
- ✅ Check if backend and AI agent are running
- ✅ Submit a test application
- ✅ Wait for AI processing
- ✅ Verify the status was updated from "pending" to final decision
- ✅ Display the results

## Expected Response

If successful, you should see:

```json
{
  "success": true,
  "customerId": "uuid-here",
  "message": "Loan application submitted successfully and sent for AI processing"
}
```

After AI processing (30-60 seconds), the status should update to:
- `approved` - Loan approved
- `rejected` - Loan rejected
- `manual_review` - Requires manual review

## Troubleshooting

### Error: Database connection failed

- Ensure Cloud SQL Proxy is running
- Check `config/gcp-credentials.json` exists
- Verify database configuration in `.env` file

### Error: Connection refused (port 3000)

- Backend server is not running
- Run `npm run dev` in the root directory

### Error: AI Agent processing failed

- AI Agent is not running (this is non-blocking)
- Start the AI agent with `python AI_agent/api_server.py`

### Status stuck at "pending"

This was the bug that has been fixed. If you still see this:
1. Make sure AI agent server was restarted after the fix
2. Check `AI_agent/logs/` for error messages
3. Verify `asyncpg` is installed: `pip3 list | grep asyncpg`
4. Run `./verify-fix.sh` to test the fix

## Checking the Application

After submission, you can check the application status by visiting:

```bash
# Using curl
curl "http://localhost:3000/api/loan-application?customerId=<customer-id>"

# Or in browser
http://localhost:3000/api/loan-application?customerId=<customer-id>
```

Replace `<customer-id>` with the ID returned in the response.

## Files in This Directory

- **`submit-test-user.js`** - Node.js submission script
- **`submit-test-user.py`** - Python submission script  
- **`run-test.sh`** - Automated test runner
- **`verify-fix.sh`** - Fix verification script
- **`FIX_SUMMARY.md`** - Detailed explanation of the bug fix
- **`README.md`** - This file
