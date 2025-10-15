# Scripts Directory

Utility scripts to manage the Credit Card Statement Parser application.

## Available Scripts

### 🚀 start-all.sh
Starts both backend and frontend services.

```bash
./scripts/start-all.sh
```

**What it does:**
- Initializes the database (if needed)
- Starts the FastAPI backend server on port 8000
- Starts the React frontend dev server on port 5173
- Creates log files in `logs/` directory
- Stores PIDs in `pids/` directory

**Services:**
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Frontend App: http://localhost:5173

---

### 🛑 stop-all.sh
Stops all running services gracefully.

```bash
./scripts/stop-all.sh
```

**What it does:**
- Stops the backend server
- Stops the frontend server
- Cleans up any remaining processes on ports 8000 and 5173
- Removes PID files

---

### 🔄 restart-all.sh
Restarts all services (stops then starts).

```bash
./scripts/restart-all.sh
```

**What it does:**
- Runs `stop-all.sh`
- Waits 2 seconds
- Runs `start-all.sh`

---

### 📊 status.sh
Check the status of all services.

```bash
./scripts/status.sh
```

**What it does:**
- Shows if backend is running (PID, port status)
- Shows if frontend is running (PID, port status)
- Checks API health endpoint
- Checks frontend accessibility

---

## Directory Structure

After running the scripts, the following directories are created:

```
cc-statement-parser/
├── logs/               # Log files
│   ├── backend.log
│   └── frontend.log
├── pids/               # Process ID files
│   ├── backend.pid
│   └── frontend.pid
└── scripts/
    ├── start-all.sh
    ├── stop-all.sh
    ├── restart-all.sh
    └── status.sh
```

## Quick Start

```bash
# Start everything
./scripts/start-all.sh

# Check status
./scripts/status.sh

# View logs
tail -f logs/backend.log
tail -f logs/frontend.log

# Stop everything
./scripts/stop-all.sh
```

## Troubleshooting

### Port Already in Use

If you get an error that a port is already in use:

```bash
# Check what's using the port
lsof -i :8000  # for backend
lsof -i :5173  # for frontend

# Kill the process
kill -9 <PID>

# Or use stop-all.sh which handles this
./scripts/stop-all.sh
```

### Services Won't Start

1. Check the logs:
   ```bash
   cat logs/backend.log
   cat logs/frontend.log
   ```

2. Make sure dependencies are installed:
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

If the database isn't initialized:

```bash
cd backend
python3 -c "
import asyncio
from app.database.connection import init_db
asyncio.run(init_db())
"
```

## Development

### Logs Location

All logs are stored in `logs/`:
- `backend.log` - Backend API logs
- `frontend.log` - Frontend dev server logs

### PID Files

Process IDs are stored in `pids/`:
- `backend.pid` - Backend server process ID
- `frontend.pid` - Frontend server process ID

These files are used to track running services and should not be edited manually.
