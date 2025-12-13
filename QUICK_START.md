# 🚀 LoanAI Quick Reference

## Start/Stop Commands

```bash
# Start everything with one command
./start-all.sh

# Stop everything
./stop-all.sh
# or press Ctrl+C in the terminal running start-all.sh
```

## Service URLs

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:3000 | Web application |
| Backend API | http://localhost:3000/api/* | Next.js API routes |
| AI Agent API | http://localhost:8000 | AI processing API |
| AI Agent Docs | http://localhost:8000/docs | Interactive API docs |
| AI Agent Health | http://localhost:8000/health | Health check |
| Database | localhost:5432 | PostgreSQL via proxy |

## Key Files

| File | Purpose |
|------|---------|
| `start-all.sh` | Master startup script (all services) |
| `stop-all.sh` | Stop all services |
| `AI_agent/start_server.sh` | Start AI Agent only |
| `AI_agent/api_server.py` | AI Agent FastAPI server |
| `AI_agent/services/data_transformer.py` | Data format converter |
| `src/app/api/loan-application/route.ts` | Backend API with AI integration |
| `INTEGRATION.md` | Complete integration documentation |

## Common Tasks

### Check if Services are Running
```bash
lsof -i :3000  # Next.js
lsof -i :8000  # AI Agent
lsof -i :5432  # Database Proxy
```

### View Live Logs
```bash
tail -f logs/nextjs.log
tail -f logs/ai-agent.log
tail -f logs/proxy.log
```

### Test AI Agent Health
```bash
curl http://localhost:8000/health
```

### Test Backend
```bash
npm run test:backend
```

### Connect to Database
```bash
npm run db:connect
```

## Architecture Overview

```
Customer → Next.js (Port 3000) → Cloud SQL (via Proxy :5432)
                ↓
         AI Agent API (Port 8000)
                ↓
         Multi-Agent System
                ↓
         Decision Result
```

## Data Flow

1. **Customer submits application** → Next.js Frontend
2. **Data saved to database** → Cloud SQL via Proxy
3. **Data sent to AI system** → AI Agent API (Port 8000)
4. **Multi-agent processing** → Bank, Salary, Verification Agents
5. **Decision generated** → Loan Officer Agent
6. **Result stored** → Available via `/api/result/{customerId}`

## Troubleshooting

### Service Won't Start
```bash
# Check if port is in use
lsof -i :[PORT]

# Kill process on port
kill $(lsof -ti:[PORT])
```

### Can't Connect to Database
1. Check proxy is running: `lsof -i :5432`
2. Verify credentials: `cat config/gcp-credentials.json`
3. Check .env file exists and has correct values

### AI Agent Errors
1. Check Python version: `python3 --version` (need 3.11+)
2. Activate venv: `cd AI_agent && source venv/bin/activate`
3. Install deps: `pip install -r requirements.txt`
4. Check logs: `tail -f logs/ai-agent.log`

## Installation (First Time Only)

```bash
# 1. Install Node dependencies
npm install

# 2. Create Python environment
cd AI_agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
cd ..

# 3. Setup Cloud SQL Proxy
cd config
./setup-proxy.sh
cd ..

# 4. Create .env file
cp .env.example .env
# Edit .env with your credentials

# 5. Add GCP credentials
# Place your service account JSON at config/gcp-credentials.json

# 6. Start everything!
./start-all.sh
```

## API Quick Reference

### Submit Application (Backend)
```bash
POST http://localhost:3000/api/loan-application
Content-Type: application/json

{
  "firstName": "John",
  "lastName": "Doe",
  "personalId": "123456",
  "gender": "male",
  "birthYear": "1990",
  "phone": "+1234567890",
  "address": "123 Main St",
  "educationLevel": "bachelor",
  "university": "Stanford",
  "employmentStatus": "employed",
  "companyName": "Tech Corp",
  "monthlySalary": 5000,
  "experienceYears": 5,
  "loanPurpose": "personal",
  "loanAmount": 10000,
  "loanDuration": 12
}
```

### Check Processing Status
```bash
GET http://localhost:8000/api/status/{customerId}
```

### Get Decision Result
```bash
GET http://localhost:8000/api/result/{customerId}
```

## Development Workflow

1. Make changes to code
2. Services auto-reload (Next.js and AI Agent)
3. Check logs for errors: `tail -f logs/*.log`
4. Test changes via frontend or API
5. Review AI decisions at `/api/result/{customerId}`

## Production Checklist

- [ ] Update .env with production credentials
- [ ] Change CORS settings in `api_server.py`
- [ ] Set up proper database (not via proxy)
- [ ] Configure logging to external service
- [ ] Add monitoring (Prometheus/Grafana)
- [ ] Set up webhook for AI results
- [ ] Implement job queue (Redis/RabbitMQ)
- [ ] Add rate limiting
- [ ] Set up SSL/HTTPS
- [ ] Configure firewall rules

## Support

For detailed information:
- Full integration guide: `INTEGRATION.md`
- Backend docs: `Docs/Backend/`
- AI Agent docs: `AI_agent/README.md`
- Architecture: `Docs/Agent/Loan-agent-architecture.md`

---

**Happy Building! 🎉**
