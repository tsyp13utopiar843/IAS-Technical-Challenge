# 6G-MAS-Factory: Complete Setup Guide

This guide provides step-by-step instructions for running the complete **6G-MAS-Factory** system locally, including both the Backend (Multi-Agent System) and Frontend (Next.js Dashboard).

## Table of Contents
- [Prerequisites](#prerequisites)
- [Backend Setup](#backend-setup)
- [Frontend Setup](#frontend-setup)
- [Running the Full System](#running-the-full-system)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

Ensure you have the following installed on your system:

### Software Requirements
- **Python 3.11+** (for Backend agents)
- **Node.js 18+** (for Frontend)
- **pnpm, npm, or yarn** (Node package manager)
- **MQTT Broker** ([Mosquitto](https://mosquitto.org/download/))
- **Git** (for cloning repositories)

### Verify Installations
```bash
# Check Python version
python --version  # Should be 3.11+

# Check Node.js version
node --version    # Should be 18+

# Check pnpm (or npm/yarn)
pnpm --version

# Check Mosquitto
mosquitto -h
```

---

## Backend Setup

### Step 1: Navigate to Backend Directory
```bash
cd "c:/Users/sraye/OneDrive/Desktop/IAS technical Chalenge/ias_tech_challenge/Backend"
```

### Step 2: Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows PowerShell:
.\\venv\\Scripts\\Activate.ps1
# On Windows CMD:
.\\venv\\Scripts\\activate.bat
# On Linux/Mac:
source venv/bin/activate
```

### Step 3: Install Dependencies
Install dependencies for each component:

```bash
# Install Orchestrator dependencies
pip install fastapi uvicorn httpx pydantic python-dotenv

# Install Planner dependencies
pip install fastapi uvicorn httpx pydantic

# Install SCADA Bridge dependencies (if needed)
pip install -r scada_bridge/requirements.txt

# Install Agent dependencies (for each agent: maint, energy, cyber, safety, ppe)
# Common requirements: fastapi, uvicorn, paho-mqtt, numpy, pandas, tensorflow/torch
pip install fastapi uvicorn[standard] paho-mqtt numpy pandas scikit-learn
```

> **Note**: If agents have specific `requirements.txt` files, install them:
```bash
pip install -r agents/maint/requirements.txt
pip install -r agents/energy/requirements.txt
# ... etc.
```

### Step 4: Generate Dummy Models (if models are missing)
If the agents fail to start due to missing ML models:
```bash
# Run the dummy model creation script (if present)
python create_dummy_models.py
```

---

## Frontend Setup

### Step 1: Navigate to Frontend Directory
```bash
cd "c:/Users/sraye/OneDrive/Desktop/IAS technical Chalenge/ias_tech_challenge/Frontend"
```

### Step 2: Install Dependencies
```bash
# Using pnpm (recommended)
pnpm install

# OR using npm
npm install

# OR using yarn
yarn install
```

### Step 3: Create Environment Configuration
Create a `.env.local` file in the `Frontend` directory with the following content:

```env
ORCHESTRATOR_URL=http://localhost:8000
PM_AGENT_URL=http://localhost:8001
ENERGY_AGENT_URL=http://localhost:8002
CYBER_AGENT_URL=http://localhost:8003
SAFETY_AGENT_URL=http://localhost:8004
PPE_AGENT_URL=http://localhost:8005
```

> **Tip**: You can copy from the example file:
```bash
cp .env.local.example .env.local
```

---

## Running the Full System

To run the full system, you need to start multiple processes in **separate terminal tabs/windows**.

### Terminal 1: Start MQTT Broker
```bash
mosquitto -v
```

**Expected Output**: Mosquitto should start and show listening on port 1883.

---

### Terminal 2: Start Orchestrator
```bash
cd Backend/agents/orchestrator
uvicorn main:app --port 8000 --reload
```

**URL**: [http://localhost:8000](http://localhost:8000)  
**Verify**: Visit [http://localhost:8000/status](http://localhost:8000/status)

---

### Terminal 3: Start Planner
```bash
cd Backend/agents/planner
uvicorn main:app --port 8011 --reload
```

**URL**: [http://localhost:8011](http://localhost:8011)

---

### Terminal 4: Start Predictive Maintenance Agent
```bash
cd Backend/agents/maint
python main.py
```

**API URL**: [http://localhost:8001](http://localhost:8001)  
**Verify**: Visit [http://localhost:8001/health](http://localhost:8001/health)

---

### Terminal 5: Start Energy Agent
```bash
cd Backend/agents/energy
python main.py
```

**API URL**: [http://localhost:8002](http://localhost:8002)

---

### Terminal 6: Start Cyber Security Agent
```bash
cd Backend/agents/cyber
python main.py
```

**API URL**: [http://localhost:8003](http://localhost:8003)

---

### Terminal 7: Start Safety Agent
```bash
cd Backend/agents/safety
python main.py
```

**API URL**: [http://localhost:8004](http://localhost:8004)

---

### Terminal 8: Start PPE Agent
```bash
cd Backend/agents/ppe
python main.py
```

**API URL**: [http://localhost:8005](http://localhost:8005)

---

### Terminal 9: Start Data Publisher (Simulator)
```bash
cd Backend/publisher
python main.py
```

This will start publishing sensor data from `manufacturing_6G_dataset.csv` to MQTT topics.

---

### Terminal 10: Start Frontend
```bash
cd Frontend
pnpm run dev
# OR: npm run dev
# OR: yarn dev
```

**URL**: [http://localhost:3000](http://localhost:3000)

---

## Verification

### 1. Verify Backend Services

Check that all backend services are running:

```bash
# Orchestrator
curl http://localhost:8000/system-state

# PM Agent
curl http://localhost:8001/status

# Energy Agent
curl http://localhost:8002/status

# Cyber Agent
curl http://localhost:8003/status

# Safety Agent
curl http://localhost:8004/status

# PPE Agent
curl http://localhost:8005/status
```

### 2. Verify Frontend Integration

1. Open browser to [http://localhost:3000](http://localhost:3000)
2. The dashboard should display **live data** from the backend agents
3. Navigate to different pages:
   - **Dashboard** (`/`): System overview with alerts
   - **Maintenance** (`/maintenance`): PM agent data
   - **Machines** (`/machines`): Machine health data
   - **PPE** (`/PPE`): PPE compliance data

### 3. Verify Data Flow

1. Watch the Publisher terminal - it should be sending MQTT messages
2. Watch agent terminals - they should be processing data
3. Check browser DevTools > Network - you should see API calls to `localhost:800X`
4. Dashboard should update with live predictions

---

## Troubleshooting

### Issue: Port Already in Use

**Error**: `Address already in use` or `Port 8000 is already in use`

**Solution**: Either kill the process using that port or change the port in the config:
```bash
# Windows - Find and kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### Issue: MQTT Broker Not Connected

**Error**: Agents show `Failed to connect to MQTT broker`

**Solution**:
1. Ensure Mosquitto is running: `mosquitto -v`
2. Check if Mosquitto is on port 1883
3. If using a different port, update agent configs

### Issue: Missing ML Models

**Error**: `FileNotFoundError: Model file not found`

**Solution**: Run the dummy model generator:
```bash
cd Backend
python create_dummy_models.py
```

### Issue: Frontend Not Fetching Data

**Error**: Dashboard shows "No data" or stuck on loading

**Solution**:
1. Check `.env.local` exists and has correct URLs
2. Verify all backend agents are running
3. Check browser console for errors (F12 > Console)
4. Verify CORS is enabled on agents
5. Test API manually: `curl http://localhost:8000/system-state`

### Issue: Python Dependencies Not Found

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**: Ensure virtual environment is activated and dependencies are installed:
```bash
# Activate venv
.\\venv\\Scripts\\Activate.ps1  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install fastapi uvicorn paho-mqtt numpy pandas
```

### Issue: Frontend Build Errors

**Error**: `Module not found` or TypeScript errors

**Solution**:
```bash
# Delete node_modules and reinstall
rm -rf node_modules pnpm-lock.yaml
pnpm install

# OR clear cache
pnpm store prune
pnpm install
```

---

## Quick Start (All-in-One Script)

For convenience, you can create scripts to start all services:

### Windows PowerShell Script (`start-backend.ps1`):
```powershell
# Start all backend services
Start-Process -NoNewWindow mosquitto
Start-Sleep -Seconds 2
Start-Process -FilePath "uvicorn" -ArgumentList "main:app --port 8000 --reload" -WorkingDirectory "Backend/agents/orchestrator"
Start-Process -FilePath "uvicorn" -ArgumentList "main:app --port 8011 --reload" -WorkingDirectory "Backend/agents/planner"
Start-Process -FilePath "python" -ArgumentList "main.py" -WorkingDirectory "Backend/agents/maint"
Start-Process -FilePath "python" -ArgumentList "main.py" -WorkingDirectory "Backend/agents/energy"
Start-Process -FilePath "python" -ArgumentList "main.py" -WorkingDirectory "Backend/agents/cyber"
Start-Process -FilePath "python" -ArgumentList "main.py" -WorkingDirectory "Backend/agents/safety"
Start-Process -FilePath "python" -ArgumentList "main.py" -WorkingDirectory "Backend/agents/ppe"
Start-Process -FilePath "python" -ArgumentList "main.py" -WorkingDirectory "Backend/publisher"
```

### Bash Script (`start-backend.sh`) for Linux/Mac:
```bash
#!/bin/bash
mosquitto -v &
sleep 2
cd Backend/agents/orchestrator && uvicorn main:app --port 8000 --reload &
cd Backend/agents/planner && uvicorn main:app --port 8011 --reload &
cd Backend/agents/maint && python main.py &
cd Backend/agents/energy && python main.py &
cd Backend/agents/cyber && python main.py &
cd Backend/agents/safety && python main.py &
cd Backend/agents/ppe && python main.py &
cd Backend/publisher && python main.py &
```

---

## Summary

✅ **Backend**: 9 services running (Mosquitto + Orchestrator + Planner + 5 Agents + Publisher)  
✅ **Frontend**: Next.js dev server on port 3000  
✅ **Integration**: Frontend fetches live data from backend via Server Actions

You're now running the complete 6G-MAS-Factory system! 🎉
