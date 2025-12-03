# 6G-MAS Factory Backend

This repository contains the backend infrastructure for the **6G-MAS-Factory** (Multi-Agent System) project. It is designed as a distributed system of autonomous AI agents, orchestrators, and protocol bridges, communicating via MQTT and HTTP/WebSockets.

## 🏗️ Architecture Overview

The backend is built on a **Microservices Architecture** where each AI agent runs as an independent service, all unified behind a **single Nginx API Gateway** for production deployment.

### Core Components

1. **AI Agents**: Autonomous agents responsible for specific domains.
   - **Predictive Maintenance (PM) Agent**: Predicts machine failures and RUL using LSTM models
   - **Energy Optimization Agent**: Monitors consumption and detects anomalies using Isolation Forest
   - **Cyber Security Agent**: Detects network threats and anomalies
   - **Workplace Safety Agent**: Monitors hazards using ML models
   - **PPE Compliance Agent**: Ensures personal protective equipment compliance using computer vision
   - **Backlog Agent**: Generates shift backlogs using Google Gemini API

2. **Orchestrator**: Central coordinator that aggregates alerts from all agents, queries the Planner for decisions, and sends Twilio SMS notifications for critical alerts.

3. **Planner**: AI service that generates action plans based on aggregated alerts.

4. **Nginx API Gateway**: Single entry point (port 8080) that routes requests to all backend services:
   - `/api/orchestrator/` → Orchestrator (port 8000)
   - `/api/pm/` → PM Agent (port 8001)
   - `/api/energy/` → Energy Agent (port 8002)
   - `/api/cyber/` → Cyber Agent (port 8003)
   - `/api/safety/` → Safety Agent (port 8004)
   - `/api/ppe/` → PPE Agent (port 8005)
   - `/ws/*` → WebSocket routes for real-time streaming

5. **SCADA Bridge**: Protocol gateway that translates MQTT data into industrial protocols (OPC UA, Modbus TCP, DNP3) for integration with legacy systems.

6. **Publisher**: Simulation tool that replays the `manufacturing_6G_dataset.csv` to MQTT, mimicking real-time factory telemetry.

### Communication Flow

```
Factory Sensors → MQTT Broker → Agents → Predictions → Orchestrator → Planner → Twilio SMS
                                      ↓
                              REST APIs / WebSockets
                                      ↓
                              Frontend Dashboard
```

- **Telemetry**: Factory sensors (simulated by `Publisher`) publish data to MQTT topics (`factory/#`)
- **Ingestion**: Agents subscribe to relevant MQTT topics
- **Processing**: Agents process data using local ML/DL models (LSTMs, Isolation Forests, etc.)
- **Output**: Agents publish predictions/alerts to MQTT (`predictions/#`) and expose them via REST APIs
- **Coordination**: Orchestrator receives alerts from agents, queries Planner, and sends SMS notifications for critical alerts

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.11+**
- **MQTT Broker**: Eclipse Mosquitto (included in Docker Compose)
- **Docker & Docker Compose** (recommended) OR manual setup

### Quick Start with Docker Compose

```bash
# From project root
docker-compose up -d

# Check services
docker-compose ps

# View logs
docker-compose logs -f orchestrator
```

The API Gateway will be available at `http://localhost:8080`

### Manual Setup

#### 1. Create Virtual Environment

```bash
cd Backend
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
# source venv/bin/activate    # Linux/Mac
```

#### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 3. Configure Environment Variables

```bash
# Copy template
cp env.template .env

# Edit .env with your API keys
# Required: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER, TWILIO_TO_NUMBER
# Optional: GEMINI_API_KEY (for Backlog Agent), HF_MODEL_REPO (for Hugging Face models)
```

#### 4. Start MQTT Broker

```bash
# Using Docker
docker run -it -p 1883:1883 -p 9001:9001 eclipse-mosquitto:2.0

# Or install Mosquitto locally
mosquitto -v
```

#### 5. Start Services

**Option A: Using Docker Compose (Recommended)**

```bash
# From project root
docker-compose up
```

**Option B: Manual Start (for development)**

Start each service in separate terminals:

```bash
# Terminal 1: Orchestrator
cd agents/orchestrator
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Planner
cd agents/planner
uvicorn main:app --host 0.0.0.0 --port 8011 --reload

# Terminal 3: PM Agent
cd agents/maint
python main.py

# Terminal 4: Energy Agent
cd agents/energy
python main.py

# Terminal 5: Cyber Agent
cd agents/cyber
python main.py

# Terminal 6: Safety Agent
cd agents/safety
python main.py

# Terminal 7: PPE Agent
cd agents/ppe
python main.py

# Terminal 8: Publisher (Data Simulator)
cd publisher
python main.py
```

**Option C: Using Nginx Gateway**

After starting all services manually, start Nginx:

```bash
# From project root
docker run -d \
  -p 8080:80 \
  -v $(pwd)/Backend/nginx/nginx.conf:/etc/nginx/nginx.conf:ro \
  --network ias_tech_challenge_mas-network \
  nginx:alpine
```

---

## 🔌 API Endpoints

### Via API Gateway (Production)

All endpoints are accessible through the Nginx gateway at `http://localhost:8080`:

- **Orchestrator**: `GET /api/orchestrator/system-state`
- **PM Agent**: `GET /api/pm/status`, `GET /api/pm/history`
- **Energy Agent**: `GET /api/energy/status`, `GET /api/energy/history`
- **Cyber Agent**: `GET /api/cyber/status`, `GET /api/cyber/history`
- **Safety Agent**: `GET /api/safety/status`, `GET /api/safety/history`
- **PPE Agent**: `GET /api/ppe/status`, `GET /api/ppe/history`

### Direct Access (Development)

- **Orchestrator**: `http://localhost:8000`
- **Planner**: `http://localhost:8011`
- **PM Agent**: `http://localhost:8001`
- **Energy Agent**: `http://localhost:8002`
- **Cyber Agent**: `http://localhost:8003`
- **Safety Agent**: `http://localhost:8004`
- **PPE Agent**: `http://localhost:8005`

### API Documentation

Once services are running, visit:
- **Orchestrator Swagger**: `http://localhost:8000/docs` (or `http://localhost:8080/api/orchestrator/docs` via gateway)
- **Agent Swagger**: Each agent exposes its own `/docs` endpoint

---

## 🔔 Twilio SMS Integration

The Orchestrator automatically sends SMS notifications via Twilio when critical alerts are received.

### Setup

1. **Get Twilio Credentials**:
   - Sign up at [twilio.com](https://www.twilio.com)
   - Get your Account SID and Auth Token
   - Get a phone number (or use WhatsApp-enabled number)

2. **Configure Environment Variables**:
   ```env
   TWILIO_ACCOUNT_SID=your_account_sid
   TWILIO_AUTH_TOKEN=your_auth_token
   TWILIO_FROM_NUMBER=+1234567890
   TWILIO_TO_NUMBER=+0987654321
   ```

3. **Test**:
   Send a critical alert to the Orchestrator:
   ```bash
   curl -X POST http://localhost:8000/alert \
     -H "Content-Type: application/json" \
     -d '{"level": "CRITICAL", "type": "test", "source": "test_agent", "details": "Test alert"}'
   ```

### Alert Format

SMS messages are formatted as:
```
🔴 [6G-MAS ALERT] CRITICAL
Agent: pm_agent
Msg: Machine failure predicted in 24 hours
```

---

## 🧪 Testing

### Run All Tests

```bash
cd Backend
venv\Scripts\python -m pytest
```

### Run Specific Test Suite

```bash
# Test notifications (Twilio)
venv\Scripts\python -m pytest tests/test_notifications.py

# Test orchestrator
venv\Scripts\python -m pytest tests/test_orchestrator.py

# Test specific agent
venv\Scripts\python -m pytest tests/test_pm_agent.py
```

### Test Coverage

- ✅ Unit tests for all agents (PM, Energy, Cyber, Safety, PPE, Backlog)
- ✅ Integration tests for Orchestrator API
- ✅ Twilio notification tests
- ✅ Alert handling and state management tests

---

## 📁 Project Structure

```
Backend/
├── agents/
│   ├── orchestrator/          # Central coordinator (Port 8000)
│   │   ├── main.py            # FastAPI app with Twilio integration
│   │   └── requirements.txt
│   ├── planner/               # Decision-making service (Port 8011)
│   ├── maint/                 # PM Agent (Port 8001)
│   ├── energy/                # Energy Agent (Port 8002)
│   ├── cyber/                 # Cyber Agent (Port 8003)
│   ├── safety/                 # Safety Agent (Port 8004)
│   ├── ppe/                    # PPE Agent (Port 8005)
│   ├── backlog/                # Backlog Agent
│   ├── base_agent.py           # Base agent class
│   ├── config/                 # Agent configurations (YAML)
│   └── utils/
│       ├── notifications.py    # Twilio notification manager
│       ├── mqtt_client.py      # MQTT client wrapper
│       ├── state_manager.py    # State persistence
│       └── config_loader.py    # Configuration loader
├── nginx/
│   └── nginx.conf              # Nginx reverse proxy configuration
├── tests/                      # Test suite
│   ├── test_notifications.py
│   ├── test_orchestrator.py
│   ├── test_pm_agent.py
│   └── ...
├── publisher/                  # Data simulator
├── scada_bridge/               # SCADA integration (optional)
├── Dockerfile                  # Container definition
├── requirements.txt            # Python dependencies
├── env.template                # Environment variables template
├── pytest.ini                  # Pytest configuration
└── README.md                   # This file
```

---

## ⚙️ Configuration

### Environment Variables

See `env.template` for all available environment variables. Key variables:

**Required for Twilio**:
- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_FROM_NUMBER`
- `TWILIO_TO_NUMBER`

**Optional**:
- `GEMINI_API_KEY` - For Backlog Agent AI generation
- `HF_MODEL_REPO` - Hugging Face model repository
- `MQTT_BROKER` - MQTT broker hostname (default: `localhost`)
- `MQTT_PORT` - MQTT broker port (default: `1883`)
- `CORS_ORIGINS` - CORS allowed origins (default: `*`)
- `PLANNER_URL` - Planner service URL (default: `http://planner:8011`)

### Agent Configuration

Each agent has a YAML configuration file in `agents/config/`:
- `pm_agent_config.yaml`
- `energy_agent_config.yaml`
- `cyber_agent_config.yaml`
- `hazard_agent_config.yaml`
- `ppe_agent_config.yaml`
- `backlog_agent_config.yaml`
- `common_config.yaml` - Shared settings

---

## 🐳 Docker Deployment

### Using Docker Compose

The `docker-compose.yml` in the project root includes:
- MQTT Broker (Mosquitto)
- Orchestrator
- Planner
- All 5 AI Agents
- Publisher (Data Simulator)
- Nginx API Gateway

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

### Production Deployment

For production deployment on Railway, Render, or VPS:

1. **Set environment variables** in your platform's dashboard
2. **Deploy using Docker Compose** or individual containers
3. **Expose port 8080** (Nginx gateway) to the internet
4. **Configure SSL/TLS** (using Let's Encrypt or platform-provided certificates)

---

## 🔧 Troubleshooting

### Port Already in Use

If a port is already in use:
- Check running processes: `netstat -ano | findstr :8000` (Windows) or `lsof -i :8000` (Linux/Mac)
- Change port in agent configuration or Docker Compose

### MQTT Connection Failed

- Ensure Mosquitto is running: `docker ps | grep mosquitto`
- Check MQTT broker URL in environment variables
- Verify network connectivity

### Missing Models

If agents fail to start due to missing models:
```bash
python create_dummy_models.py
```

### Twilio Not Working

- Verify environment variables are set correctly
- Check Twilio credentials in Twilio Console
- Ensure phone numbers are in E.164 format (+1234567890)
- Check logs for error messages

### Tests Failing

- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Install test dependencies: `pip install pytest pytest-asyncio`
- Run tests from the `Backend` directory

---

## 📚 Additional Resources

- **[Root README.md](../README.md)** - Project overview and quick start
- **[Frontend/README.md](../Frontend/README.md)** - Frontend integration guide
- **[DEPLOYMENT_GUIDE.md](../DEPLOYMENT_GUIDE.md)** - Production deployment
- **[DOCKER_QUICKSTART.md](../DOCKER_QUICKSTART.md)** - Docker setup guide

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass: `pytest`
5. Submit a pull request

---

**Built with ❤️ for Industrial IIoT**

*Multi-Agent System • Real-time MQTT • AI-Powered Predictions • Production-Ready*

