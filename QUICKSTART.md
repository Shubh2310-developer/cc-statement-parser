# Quick Start Guide - CC Statement Parser

## 🚀 Start All Services (One Command)

```bash
./scripts/start-all.sh
```

This will start both the backend API and frontend web app.

---

## 📋 Service URLs

Once started, access the application at:

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:5173 | Main web application |
| **Backend API** | http://localhost:8000 | REST API server |
| **API Documentation** | http://localhost:8000/docs | Interactive API docs (Swagger) |
| **Health Check** | http://localhost:8000/api/v1/health | API health status |

---

## 🛠️ Management Scripts

All scripts are located in the `scripts/` directory:

### Start Services
```bash
./scripts/start-all.sh
```
- Initializes database
- Starts FastAPI backend on port 8000
- Starts React frontend on port 5173

### Stop Services
```bash
./scripts/stop-all.sh
```
- Gracefully stops all services
- Cleans up processes and PID files

### Restart Services
```bash
./scripts/restart-all.sh
```
- Stops all services
- Waits 2 seconds
- Starts all services fresh

### Check Status
```bash
./scripts/status.sh
```
- Shows running status of each service
- Displays PID and port information
- Checks API health
- Verifies frontend accessibility

---

## 📁 Logs & PIDs

### Log Files
```bash
# Backend logs
tail -f logs/backend.log

# Frontend logs
tail -f logs/frontend.log
```

### Process IDs
PID files are stored in `pids/`:
- `backend.pid` - Backend server process ID
- `frontend.pid` - Frontend server process ID

---

## 🧪 Testing

### Supported Banks
The parser supports credit card statements from:
- ✅ **HDFC Bank** - 76.75% confidence
- ✅ **ICICI Bank** - 69% confidence
- ✅ **Axis Bank** - 73.17% confidence
- ✅ **American Express** - 74.33% confidence

### Test with Sample PDFs
Sample PDFs are included in the root directory:
- `HDFCCCSAMPLE.pdf`
- `ICICICCSAMPLE.pdf`
- `AXISCCSAMPLE.pdf`
- `AmexCCSample.pdf`

### API Testing
```bash
# Upload a PDF via API
curl -X POST http://localhost:8000/api/v1/parse \
  -F "file=@HDFCCCSAMPLE.pdf"

# Check health
curl http://localhost:8000/api/v1/health
```

---

## 🔧 Troubleshooting

### Port Already in Use
```bash
# Check what's using the port
lsof -i :8000  # backend
lsof -i :5173  # frontend

# Stop all services
./scripts/stop-all.sh
```

### Services Won't Start
1. Check logs for errors
2. Ensure dependencies are installed:
   ```bash
   # Backend
   cd backend
   pip install -r requirements.txt

   # Frontend
   cd frontend
   npm install
   ```
3. Restart services:
   ```bash
   ./scripts/restart-all.sh
   ```

### Database Issues
```bash
cd backend
python3 -c "
import asyncio
from app.database.connection import init_db
asyncio.run(init_db())
"
```

---

## 📊 Features

### Extracted Fields
The parser extracts the following information:
- ✓ Card last 4 digits
- ✓ Card type/variant
- ✓ Statement period dates
- ✓ Payment due date
- ✓ Minimum amount due
- ✓ Total amount due
- ✓ Available credit
- ✓ Confidence scores for each field

### Confidence Scoring
Each extracted field includes a confidence score (0-100%) indicating the reliability of the extraction.

---

## 🎯 Next Steps

1. **Upload a Statement**: Go to http://localhost:5173 and upload a PDF
2. **View Results**: See extracted fields with confidence scores
3. **Check API Docs**: Visit http://localhost:8000/docs for API details
4. **Monitor Logs**: Use `tail -f logs/backend.log` to see processing details

---

## 💡 Tips

- The system automatically detects which bank issued the statement
- Higher confidence scores (>90%) indicate very reliable extractions
- Check backend logs if processing seems slow
- Frontend updates in real-time as the backend processes

---

For more details, see:
- `scripts/README.md` - Detailed script documentation
- `backend/README.md` - Backend architecture
- `frontend/README.md` - Frontend details
