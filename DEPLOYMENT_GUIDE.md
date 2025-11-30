# Multi-Service Management & Production Deployment Guide

This guide covers:
1. Running all services efficiently (Docker Compose)
2. Production deployment on Railway (Backend) + Vercel (Frontend)

---

## Part 1: Running All Services Locally with Docker Compose

### Why Docker Compose?
- ✅ Single command to start/stop everything
- ✅ No need for 10 terminals
- ✅ Consistent environment
- ✅ Easy to share with team

### Step 1: Create Dockerfiles

#### Backend Dockerfile
Create `Backend/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements (create a consolidated requirements.txt)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Default command (will be overridden in docker-compose)
CMD ["python", "-m", "uvicorn", "agents.orchestrator.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Frontend Dockerfile (optional for local dev)
Create `Frontend/Dockerfile`:

```dockerfile
FROM node:18-alpine AS deps
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN npm install -g pnpm && pnpm install --frozen-lockfile

FROM node:18-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm install -g pnpm && pnpm build

FROM node:18-alpine AS runner
WORKDIR /app
ENV NODE_ENV production
COPY --from=builder /app/next.config.mjs ./
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

EXPOSE 3000
CMD ["npm", "start"]
```

### Step 2: Create docker-compose.yml

Create `docker-compose.yml` in the root directory:

```yaml
version: '3.8'

services:
  # MQTT Broker
  mosquitto:
    image: eclipse-mosquitto:latest
    container_name: mqtt-broker
    ports:
      - "1883:1883"
      - "9001:9001"
    volumes:
      - ./mosquitto.conf:/mosquitto/config/mosquitto.conf
    networks:
      - mas-network

  # Orchestrator
  orchestrator:
    build:
      context: ./Backend
      dockerfile: Dockerfile
    container_name: orchestrator
    command: uvicorn agents.orchestrator.main:app --host 0.0.0.0 --port 8000 --reload
    ports:
      - "8000:8000"
    environment:
      - CORS_ORIGINS=*
      - PLANNER_URL=http://planner:8011
    depends_on:
      - mosquitto
    networks:
      - mas-network
    restart: unless-stopped

  # Planner
  planner:
    build:
      context: ./Backend
      dockerfile: Dockerfile
    container_name: planner
    command: uvicorn agents.planner.main:app --host 0.0.0.0 --port 8011 --reload
    ports:
      - "8011:8011"
    networks:
      - mas-network
    restart: unless-stopped

  # PM Agent
  pm-agent:
    build:
      context: ./Backend
      dockerfile: Dockerfile
    container_name: pm-agent
    command: python agents/maint/main.py
    ports:
      - "8001:8001"
    environment:
      - MQTT_BROKER=mosquitto
      - MQTT_PORT=1883
    depends_on:
      - mosquitto
    networks:
      - mas-network
    restart: unless-stopped

  # Energy Agent
  energy-agent:
    build:
      context: ./Backend
      dockerfile: Dockerfile
    container_name: energy-agent
    command: python agents/energy/main.py
    ports:
      - "8002:8002"
    environment:
      - MQTT_BROKER=mosquitto
      - MQTT_PORT=1883
    depends_on:
      - mosquitto
    networks:
      - mas-network
    restart: unless-stopped

  # Cyber Agent
  cyber-agent:
    build:
      context: ./Backend
      dockerfile: Dockerfile
    container_name: cyber-agent
    command: python agents/cyber/main.py
    ports:
      - "8003:8003"
    environment:
      - MQTT_BROKER=mosquitto
      - MQTT_PORT=1883
    depends_on:
      - mosquitto
    networks:
      - mas-network
    restart: unless-stopped

  # Safety Agent
  safety-agent:
    build:
      context: ./Backend
      dockerfile: Dockerfile
    container_name: safety-agent
    command: python agents/safety/main.py
    ports:
      - "8004:8004"
    environment:
      - MQTT_BROKER=mosquitto
      - MQTT_PORT=1883
    depends_on:
      - mosquitto
    networks:
      - mas-network
    restart: unless-stopped

  # PPE Agent
  ppe-agent:
    build:
      context: ./Backend
      dockerfile: Dockerfile
    container_name: ppe-agent
    command: python agents/ppe/main.py
    ports:
      - "8005:8005"
    environment:
      - MQTT_BROKER=mosquitto
      - MQTT_PORT=1883
    depends_on:
      - mosquitto
    networks:
      - mas-network
    restart: unless-stopped

  # Publisher (Data Simulator)
  publisher:
    build:
      context: ./Backend
      dockerfile: Dockerfile
    container_name: publisher
    command: python publisher/main.py
    environment:
      - MQTT_BROKER=mosquitto
      - MQTT_PORT=1883
    depends_on:
      - mosquitto
    networks:
      - mas-network
    restart: unless-stopped

  # Frontend (optional for Docker, usually run separately)
  # frontend:
  #   build:
  #     context: ./Frontend
  #     dockerfile: Dockerfile
  #   container_name: frontend
  #   ports:
  #     - "3000:3000"
  #   environment:
  #     - ORCHESTRATOR_URL=http://orchestrator:8000
  #     - PM_AGENT_URL=http://pm-agent:8001
  #     - ENERGY_AGENT_URL=http://energy-agent:8002
  #     - CYBER_AGENT_URL=http://cyber-agent:8003
  #     - SAFETY_AGENT_URL=http://safety-agent:8004
  #     - PPE_AGENT_URL=http://ppe-agent:8005
  #   depends_on:
  #     - orchestrator
  #   networks:
  #     - mas-network

networks:
  mas-network:
    driver: bridge
```

### Step 3: Create mosquitto.conf

Create `mosquitto.conf` in root:

```conf
listener 1883
allow_anonymous true
```

### Step 4: Create Backend requirements.txt

Create `Backend/requirements.txt`:

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
paho-mqtt==1.6.1
httpx==0.25.0
pydantic==2.5.0
python-dotenv==1.0.0
numpy==1.24.3
pandas==2.0.3
scikit-learn==1.3.0
```

### Step 5: Run Everything with One Command!

```bash
# Start all services
docker-compose up

# Or in detached mode (background)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop everything
docker-compose down

# Rebuild after code changes
docker-compose up --build

# Run frontend separately (recommended)
cd Frontend
pnpm dev
```

---

## Part 2: Production Deployment

### A. Backend on Railway

#### Option 1: Monolith Deployment (Recommended for Railway)

Railway charges per service, so combine everything into one deployment.

**Step 1: Create Railway Monolith**

Create `Backend/railway_main.py`:

```python
"""
Railway Monolith - Runs all services in one process
"""
import asyncio
import uvicorn
from multiprocessing import Process
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_orchestrator():
    from agents.orchestrator.main import app
    uvicorn.run(app, host="0.0.0.0", port=8000)

def run_planner():
    from agents.planner.main import app
    uvicorn.run(app, host="0.0.0.0", port=8011)

def run_pm_agent():
    import asyncio
    from agents.maint.main import main
    asyncio.run(main())

def run_energy_agent():
    import asyncio
    from agents.energy.main import main
    asyncio.run(main())

def run_cyber_agent():
    import asyncio
    from agents.cyber.main import main
    asyncio.run(main())

def run_safety_agent():
    import asyncio
    from agents.safety.main import main
    asyncio.run(main())

def run_ppe_agent():
    import asyncio
    from agents.ppe.main import main
    asyncio.run(main())

def run_publisher():
    import asyncio
    from publisher.main import main
    asyncio.run(main())

if __name__ == "__main__":
    processes = []
    
    # Start all services as separate processes
    services = [
        ("Orchestrator", run_orchestrator),
        ("Planner", run_planner),
        ("PM Agent", run_pm_agent),
        ("Energy Agent", run_energy_agent),
        ("Cyber Agent", run_cyber_agent),
        ("Safety Agent", run_safety_agent),
        ("PPE Agent", run_ppe_agent),
        ("Publisher", run_publisher),
    ]
    
    for name, func in services:
        p = Process(target=func, name=name)
        p.start()
        processes.append(p)
        print(f"✓ Started {name}")
    
    # Wait for all processes
    try:
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        print("Shutting down...")
        for p in processes:
            p.terminate()
```

**Step 2: Create Procfile for Railway**

Create `Backend/Procfile`:

```
web: python railway_main.py
```

**Step 3: Create railway.json**

Create `Backend/railway.json`:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python railway_main.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

**Step 4: Deploy to Railway**

1. Install Railway CLI:
```bash
npm install -g @railway/cli
```

2. Login and deploy:
```bash
cd Backend
railway login
railway init
railway up
```

3. Set Environment Variables in Railway Dashboard:
   - `CORS_ORIGINS=https://your-frontend.vercel.app,http://localhost:3000`
   - `MQTT_BROKER=localhost` (or use CloudAMQP for external MQTT)

4. Get your Railway URL (e.g., `https://your-app.railway.app`)

#### Railway Alternative: Use External MQTT

Since Railway doesn't easily support MQTT brokers, use **CloudAMQP** or **HiveMQ Cloud**:

```bash
# In Railway environment variables:
MQTT_BROKER=your-cloudamqp-broker.mq.cloudamqp.com
MQTT_PORT=1883
MQTT_USERNAME=your-username
MQTT_PASSWORD=your-password
```

### B. Frontend on Vercel

**Step 1: Prepare Frontend for Production**

Update `Frontend/.env.production`:

```env
ORCHESTRATOR_URL=https://your-backend.railway.app
PM_AGENT_URL=https://your-backend.railway.app
ENERGY_AGENT_URL=https://your-backend.railway.app
CYBER_AGENT_URL=https://your-backend.railway.app
SAFETY_AGENT_URL=https://your-backend.railway.app
PPE_AGENT_URL=https://your-backend.railway.app
```

**Note**: Since all agents run on Railway, they'll be on different internal ports but same domain. You'll need to update server actions to use path-based routing or update Railway to expose multiple ports.

**Step 2: Update Server Actions for Production**

Modify agent URLs to use Railway's path-based routing:

```typescript
// Update agents.ts to use environment variables
const BASE_URL = process.env.ORCHESTRATOR_URL || "http://localhost:8000";

export async function fetchPMStatus() {
  // Railway will route internally
  const response = await fetch(`${BASE_URL}/agents/pm/status`);
  // ...
}
```

**Step 3: Deploy to Vercel**

```bash
cd Frontend

# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
vercel

# Set for production
vercel --prod
```

**Step 4: Configure Vercel Environment Variables**

In Vercel Dashboard:
- Go to Settings > Environment Variables
- Add:
  - `ORCHESTRATOR_URL` = `https://your-backend.railway.app`
  - (Same for other agent URLs)

---

## Part 3: Improved Architecture for Production

### Recommended: API Gateway Pattern

Instead of exposing all agents separately, use the **Orchestrator as an API Gateway**:

```python
# In Backend/agents/orchestrator/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI()

# ... existing code ...

# Add proxy routes for agents
@app.get("/api/agents/pm/status")
async def proxy_pm_status():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8001/status")
        return response.json()

@app.get("/api/agents/energy/status")
async def proxy_energy_status():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8002/status")
        return response.json()

# ... add for all agents ...
```

Then frontend only needs ONE URL:
```env
API_BASE_URL=https://your-backend.railway.app
```

---

## Summary

### Local Development:
```bash
# Option 1: Docker Compose (Recommended)
docker-compose up

# Option 2: PowerShell Script (Windows)
./start-backend.ps1
```

### Production:
- **Backend**: Railway (monolith deployment)
- **Frontend**: Vercel (automatic Next.js deployment)
- **MQTT**: CloudAMQP or HiveMQ Cloud

### Next Steps:
1. Create the Docker setup files
2. Test locally with `docker-compose up`
3. Deploy backend to Railway
4. Deploy frontend to Vercel
5. Configure environment variables
