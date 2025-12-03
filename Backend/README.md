# 6G-MAS Factory Backend

A comprehensive Multi-Agent System (MAS) backend for intelligent factory monitoring, predictive maintenance, and safety compliance. This backend orchestrates multiple AI agents that work together to monitor equipment health, optimize energy consumption, detect cyber threats, ensure workplace safety, and maintain PPE compliance.

## 🏗️ Architecture Overview

The backend is built on a **Microservices Architecture** where each AI agent runs as an independent service, all unified behind a **single API Gateway** for production deployment. The system uses MQTT for inter-agent communication, FastAPI for REST APIs, and WebSockets for real-time data streaming.

### Core Components

#### 1. **AI Agents** (Autonomous Domain-Specific Services)

- **Predictive Maintenance (PM) Agent** (`agents/maint/`)
  - **Purpose**: Predicts machine failures and calculates Remaining Useful Life (RUL)
  - **Model**: Random Forest Classifier (`PM/rf_smote_pipeline_model.pkl`)
  - **Port**: 8001
  - **Features**: 
    - Real-time equipment health monitoring
    - RUL prediction with failure probability scoring
    - Maintenance scheduling recommendations
    - Historical prediction tracking

- **Energy Optimization Agent** (`agents/energy/`)
  - **Purpose**: Monitors energy consumption and detects anomalies
  - **Model**: LSTM Neural Network (`energy.keras`) + Isolation Forest for anomaly detection
  - **Port**: 8002
  - **Features**:
    - Energy consumption pattern analysis
    - Anomaly detection in power usage
    - Optimization recommendations
    - Time-series forecasting

- **Cyber Security Agent** (`agents/cyber/`)
  - **Purpose**: Detects network threats and security anomalies
  - **Model**: Isolation Forest (`cyber.pkl`)
  - **Port**: 8003
  - **Features**:
    - Real-time threat detection
    - Network traffic anomaly identification
    - Security event classification
    - Alert generation for suspicious activities

- **Workplace Safety (Hazard) Agent** (`agents/safety/`)
  - **Purpose**: Monitors workplace hazards and safety violations
  - **Model**: Random Forest Classifier (`safety_artifacts/rf_hazard_predictor_model.pkl`)
  - **Port**: 8004
  - **Features**:
    - Hazard detection and classification
    - Safety violation tracking
    - Risk assessment scoring
    - Compliance monitoring

- **PPE Compliance Agent** (`agents/ppe/`)
  - **Purpose**: Ensures Personal Protective Equipment compliance using computer vision
  - **Model**: CNN (Keras) (`PPE_artifacts/ppe_classifier.keras`)
  - **Port**: 8005
  - **Features**:
    - Real-time PPE detection (helmet, boots, pants, shirt)
    - Compliance violation alerts
    - Image-based classification
    - Smoothing buffer for stable predictions

- **Backlog Agent** (`agents/backlog/`)
  - **Purpose**: Generates shift-based backlogs summarizing violations and anomalies
  - **Model**: Google Gemini API via LangChain
  - **Port**: N/A (runs as background service)
  - **Features**:
    - Automatic backlog generation every 8 hours
    - Aggregates events from all agents
    - Natural language summaries
    - Actionable recommendations

#### 2. **Orchestrator** (`agents/orchestrator/`)
- **Purpose**: Central coordinator that aggregates alerts from all agents
- **Port**: 8000
- **Features**:
  - Alert aggregation and routing
  - Integration with Planner service for decision-making
  - Twilio SMS notifications for critical alerts
  - System state management for dashboard
  - CORS-enabled API for frontend integration

#### 3. **Planner** (`agents/planner/`)
- **Purpose**: AI service that generates action plans based on aggregated alerts
- **Port**: 8011
- **Features**:
  - Decision-making based on alert context
  - Action plan generation
  - Priority-based recommendations

#### 4. **SCADA Bridge** (`scada_bridge/`)
- **Purpose**: Protocol gateway that translates MQTT data into industrial protocols
- **Features**:
  - OPC UA server (port 4840)
  - Modbus TCP server (port 502)
  - DNP3 server (port 20000)
  - Bidirectional data translation
  - Legacy system integration

#### 5. **Publisher** (`publisher/`)
- **Purpose**: Simulation tool that replays manufacturing data to MQTT
- **Features**:
  - Replays `manufacturing_6G_dataset.csv` data
  - Mimics real-time factory telemetry
  - Configurable publishing intervals

### Agent Architecture

Each AI agent follows a standardized modular architecture with five core components:

1. **Model** (`model.py`): Handles ML model loading, preprocessing, and inference
2. **Logic** (`logic.py`): Implements business rules and decision-making
3. **State** (`state.py`): Manages agent state, history, and persistence
4. **Communication** (`communication.py`): Handles MQTT, REST API, and WebSocket interfaces
5. **Alerts** (`alerts.py`): Routes alerts to appropriate channels based on severity

All agents inherit from `BaseAgent` (`agents/base_agent.py`), which provides:
- Standardized lifecycle management (start, stop, restart)
- Health check endpoints
- State checkpointing and recovery
- Graceful shutdown handling

## 📋 Prerequisites

- **Python**: 3.11 or higher
- **MQTT Broker**: Mosquitto or any MQTT broker (default: localhost:1883)
- **Operating System**: Windows, Linux, or macOS
- **Memory**: Minimum 4GB RAM (8GB recommended for all agents)
- **Disk Space**: ~2GB for models and dependencies

### Optional Dependencies

- **Twilio Account**: For SMS notifications (required for critical alerts)
- **Google Gemini API Key**: For Backlog Agent (required for backlog generation)
- **Docker**: For containerized deployment
- **Railway Account**: For cloud deployment

## 🚀 Installation & Setup

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd Backend
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
# Install main requirements
pip install -r requirements.txt

# Install agent-specific requirements (if needed)
pip install -r agents/maint/requirements.txt
pip install -r agents/energy/requirements.txt
pip install -r agents/cyber/requirements.txt
pip install -r agents/safety/requirements.txt
pip install -r agents/ppe/requirements.txt
pip install -r agents/backlog/requirements.txt
```

### Step 4: Configure Environment Variables

1. Copy the environment template:
```bash
cp env.template .env
```

2. Edit `.env` and configure the following:

```env
# MQTT Broker Configuration
MQTT_BROKER=localhost
MQTT_PORT=1883

# Orchestrator & Planner
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
PLANNER_URL=http://localhost:8011

# Twilio (for SMS notifications)
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_FROM_NUMBER=+1234567890
TWILIO_TO_NUMBER=+0987654321

# Google Gemini (for Backlog Agent)
GEMINI_API_KEY=your_gemini_api_key

# Logging
LOG_LEVEL=INFO
```

### Step 5: Verify Model Files

Ensure all model files are in place:

```bash
# Check model files exist
ls PM/rf_smote_pipeline_model.pkl
ls PM/scaler.pkl
ls PM/label_encoder.pkl
ls energy.keras
ls cyber.pkl
ls safety_artifacts/rf_hazard_predictor_model.pkl
ls safety_artifacts/standard_scaler.pkl
ls safety_artifacts/label_encoders.pkl
ls PPE_artifacts/ppe_classifier.keras
ls PPE_artifacts/scaler.pkl
ls PPE_artifacts/class_weights.pkl
```

### Step 6: Start MQTT Broker

```bash
# Using Mosquitto (if installed)
mosquitto -p 1883

# Or using Docker
docker run -it -p 1883:1883 eclipse-mosquitto
```

## 🏃 Running the Backend

### Option 1: Run All Services (Monolith Mode - Recommended for Railway)

This runs all services in a single process, ideal for deployment:

```bash
python railway_main.py
```

This will start:
- Orchestrator (port 8000)
- Planner (port 8011)
- PM Agent (port 8001)
- Energy Agent (port 8002)
- Cyber Agent (port 8003)
- Safety Agent (port 8004)
- PPE Agent (port 8005)
- Publisher (data simulator)

### Option 2: Run Services Individually

For development and testing, you can run each service separately:

#### Start Orchestrator
```bash
python -m uvicorn agents.orchestrator.main:app --host 0.0.0.0 --port 8000
```

#### Start Planner
```bash
python -m uvicorn agents.planner.main:app --host 0.0.0.0 --port 8011
```

#### Start PM Agent
```bash
python -m agents.maint.main
```

#### Start Energy Agent
```bash
python -m agents.energy.main
```

#### Start Cyber Agent
```bash
python -m agents.cyber.main
```

#### Start Safety Agent
```bash
python -m agents.safety.main
```

#### Start PPE Agent
```bash
python -m agents.ppe.main
```

#### Start Publisher (Data Simulator)
```bash
python -m publisher.main
```

### Option 3: Using Docker Compose (If Available)

```bash
docker-compose up -d
```

## 🔌 Connecting to the Frontend

### API Gateway Configuration

The backend exposes a unified API through the Orchestrator service. For production, you can use Nginx as a reverse proxy (see `nginx/nginx.conf`), but for development, you can connect directly to individual services.

### Frontend Integration Guide

#### 1. **Base URLs Configuration**

In your frontend configuration, set the following base URLs:

```javascript
// Development (individual services)
const API_BASE_URLS = {
  orchestrator: 'http://localhost:8000',
  pm: 'http://localhost:8001',
  energy: 'http://localhost:8002',
  cyber: 'http://localhost:8003',
  safety: 'http://localhost:8004',
  ppe: 'http://localhost:8005',
  planner: 'http://localhost:8011'
};

// Production (with Nginx reverse proxy)
const API_BASE_URLS = {
  orchestrator: 'https://your-domain.com/api/orchestrator',
  pm: 'https://your-domain.com/api/pm',
  energy: 'https://your-domain.com/api/energy',
  cyber: 'https://your-domain.com/api/cyber',
  safety: 'https://your-domain.com/api/safety',
  ppe: 'https://your-domain.com/api/ppe'
};
```

#### 2. **CORS Configuration**

The backend has CORS enabled by default. Configure allowed origins in `.env`:

```env
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,https://your-frontend-domain.com
```

#### 3. **Key API Endpoints for Frontend**

##### Orchestrator Endpoints

```javascript
// Get system-wide state (alerts, decisions)
GET /api/orchestrator/system-state
Response: {
  "alerts": [...],
  "decisions": [...],
  "last_update": "2024-01-01T12:00:00Z"
}

// Submit alert (if needed)
POST /api/orchestrator/alert
Body: {
  "level": "CRITICAL",
  "type": "maintenance",
  "source": "pm_agent",
  "details": "Machine failure predicted"
}
```

##### Agent Endpoints (Same pattern for all agents)

```javascript
// Health check
GET /api/pm/health
Response: {
  "status": "healthy",
  "agent_id": "pm_agent",
  "mqtt_connected": true
}

// Agent status and state
GET /api/pm/status
Response: {
  "status": "running",
  "agent_id": "pm_agent",
  "last_prediction": {...},
  "metrics": {...}
}

// Prediction history
GET /api/pm/history?limit=50
Response: {
  "history": [...],
  "total": 100
}

// Manual prediction trigger
POST /api/pm/predict
Body: {
  "temperature": 75.5,
  "pressure": 120.3,
  "vibration": 0.8,
  ...
}
```

#### 4. **WebSocket Connections for Real-Time Data**

Each agent exposes a WebSocket endpoint for real-time prediction streaming:

```javascript
// Connect to PM Agent WebSocket
const ws = new WebSocket('ws://localhost:8001/ws');

ws.onmessage = (event) => {
  const prediction = JSON.parse(event.data);
  console.log('New prediction:', prediction);
  // Update your UI with real-time data
};

// Connect to Energy Agent WebSocket
const energyWs = new WebSocket('ws://localhost:8002/ws');

// Similar pattern for other agents
```

#### 5. **Example Frontend Integration (React/Next.js)**

```typescript
// hooks/useSystemState.ts
import { useEffect, useState } from 'react';

export function useSystemState() {
  const [state, setState] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchState = async () => {
      try {
        const response = await fetch('http://localhost:8000/system-state');
        const data = await response.json();
        setState(data);
      } catch (error) {
        console.error('Failed to fetch system state:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchState();
    const interval = setInterval(fetchState, 5000); // Poll every 5 seconds

    return () => clearInterval(interval);
  }, []);

  return { state, loading };
}

// hooks/useAgentWebSocket.ts
import { useEffect, useState } from 'react';

export function useAgentWebSocket(agentPort: number) {
  const [predictions, setPredictions] = useState([]);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:${agentPort}/ws`);

    ws.onopen = () => {
      setConnected(true);
      console.log(`Connected to agent on port ${agentPort}`);
    };

    ws.onmessage = (event) => {
      const prediction = JSON.parse(event.data);
      setPredictions(prev => [prediction, ...prev].slice(0, 100)); // Keep last 100
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setConnected(false);
    };

    ws.onclose = () => {
      setConnected(false);
      // Attempt reconnection after 5 seconds
      setTimeout(() => {
        // Reconnect logic here
      }, 5000);
    };

    return () => {
      ws.close();
    };
  }, [agentPort]);

  return { predictions, connected };
}

// Usage in component
function Dashboard() {
  const { state, loading } = useSystemState();
  const { predictions: pmPredictions } = useAgentWebSocket(8001);
  const { predictions: energyPredictions } = useAgentWebSocket(8002);

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <h1>System State</h1>
      <p>Alerts: {state?.alerts?.length || 0}</p>
      <p>Decisions: {state?.decisions?.length || 0}</p>
      
      <h2>PM Agent Predictions</h2>
      <ul>
        {pmPredictions.map((pred, i) => (
          <li key={i}>{JSON.stringify(pred)}</li>
        ))}
      </ul>
    </div>
  );
}
```

#### 6. **Error Handling**

```typescript
// utils/apiClient.ts
class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  async getSystemState() {
    return this.request('/system-state');
  }

  async getAgentStatus(agent: string) {
    return this.request(`/api/${agent}/status`);
  }

  async getAgentHistory(agent: string, limit = 50) {
    return this.request(`/api/${agent}/history?limit=${limit}`);
  }
}

// Usage
const apiClient = new ApiClient('http://localhost:8000');
const systemState = await apiClient.getSystemState();
```

#### 7. **Production Deployment Considerations**

- **HTTPS**: Ensure all API calls use HTTPS in production
- **Authentication**: Add API key or JWT authentication (not currently implemented)
- **Rate Limiting**: Implement rate limiting on the backend
- **WebSocket Reconnection**: Implement exponential backoff for WebSocket reconnections
- **Error Boundaries**: Use React error boundaries to handle API failures gracefully
- **Environment Variables**: Use environment variables for API URLs in frontend

```typescript
// config.ts
export const config = {
  apiBaseUrl: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000',
  wsBaseUrl: process.env.NEXT_PUBLIC_WS_BASE_URL || 'ws://localhost:8001',
  // ... other config
};
```

## 📡 MQTT Topics

The system uses MQTT for inter-agent communication. Key topics:

- `sensors/factory/data` - Raw sensor data (published by Publisher)
- `predictions/pm_agent` - PM Agent predictions
- `predictions/energy_agent` - Energy Agent predictions
- `predictions/cyber_agent` - Cyber Agent predictions
- `predictions/safety_agent` - Safety Agent predictions
- `predictions/ppe_agent` - PPE Agent predictions
- `alerts/pm_agent` - PM Agent alerts
- `alerts/energy_agent` - Energy Agent alerts
- `alerts/cyber_agent` - Cyber Agent alerts
- `alerts/safety_agent` - Safety Agent alerts
- `alerts/ppe_agent` - PPE Agent alerts
- `backlog/shift_summary` - Backlog Agent summaries

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_pm_agent.py

# Run with coverage
pytest --cov=agents --cov-report=html
```

## 📁 Project Structure

```
Backend/
├── agents/
│   ├── orchestrator/          # Central coordinator (Port 8000)
│   ├── planner/               # Decision-making service (Port 8011)
│   ├── maint/                 # PM Agent (Port 8001)
│   │   ├── model.py           # ML model handling
│   │   ├── logic.py           # Business rules
│   │   ├── state.py           # State management
│   │   ├── communication.py   # API & MQTT
│   │   ├── alerts.py          # Alert routing
│   │   └── main.py            # Agent orchestrator
│   ├── energy/                # Energy Agent (Port 8002)
│   ├── cyber/                 # Cyber Agent (Port 8003)
│   ├── safety/                # Safety Agent (Port 8004)
│   ├── ppe/                   # PPE Agent (Port 8005)
│   ├── backlog/               # Backlog Agent
│   ├── base_agent.py          # Base agent class
│   ├── config/                # Agent configurations (YAML)
│   └── utils/                 # Shared utilities
│       ├── notifications.py   # Twilio notification manager
│       ├── mqtt_client.py     # MQTT client wrapper
│       ├── state_manager.py   # State persistence
│       └── config_loader.py   # Configuration loader
├── scada_bridge/              # SCADA integration
├── publisher/                 # Data simulator
├── nginx/                     # Nginx reverse proxy config
├── PM/                        # PM Agent model files
├── PPE_artifacts/             # PPE Agent model files
├── safety_artifacts/          # Safety Agent model files
├── railway_main.py            # Monolith deployment script
├── requirements.txt           # Python dependencies
├── env.template               # Environment variables template
├── Dockerfile                 # Docker container definition
└── README.md                  # This file
```

## 🔧 Configuration

### Agent Configuration Files

Each agent has a YAML configuration file in `agents/config/`:

- `common_config.yaml` - Shared configuration
- `pm_agent_config.yaml` - PM Agent specific config
- `energy_agent_config.yaml` - Energy Agent specific config
- `cyber_agent_config.yaml` - Cyber Agent specific config
- `hazard_agent_config.yaml` - Safety Agent specific config
- `ppe_agent_config.yaml` - PPE Agent specific config
- `backlog_agent_config.yaml` - Backlog Agent specific config

### Model Paths

Model paths are configured in each agent's config file. The system supports:
- Relative paths from agent directory
- Relative paths from Backend root
- Absolute paths

Example (`pm_agent_config.yaml`):
```yaml
model:
  path: "../PM/rf_smote_pipeline_model.pkl"
  scaler_path: "../PM/scaler.pkl"
  label_encoder_path: "../PM/label_encoder.pkl"
```

## 🚢 Deployment

### Railway Deployment

The backend is optimized for Railway deployment using a monolith architecture. The `Dockerfile` and `railway_main.py` are configured to run all services in a single container.

#### Step-by-Step Railway Deployment:

1. **Create a Railway Account**
   - Go to [railway.app](https://railway.app)
   - Sign up or log in

2. **Create a New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo" (or use Railway CLI)
   - Connect your repository

3. **Configure Environment Variables**
   In Railway dashboard, go to Variables tab and add:
   ```env
   # MQTT Broker (use Railway's public MQTT or external service)
   MQTT_BROKER=your-mqtt-broker-url
   MQTT_PORT=1883
   
   # CORS (your frontend URL)
   CORS_ORIGINS=https://your-frontend-domain.com
   
   # Planner URL (internal, Railway handles this)
   PLANNER_URL=http://localhost:8011
   
   # Twilio (for SMS notifications)
   TWILIO_ACCOUNT_SID=your_account_sid
   TWILIO_AUTH_TOKEN=your_auth_token
   TWILIO_FROM_NUMBER=+1234567890
   TWILIO_TO_NUMBER=+0987654321
   
   # Google Gemini (for Backlog Agent)
   GEMINI_API_KEY=your_gemini_api_key
   
   # Logging
   LOG_LEVEL=INFO
   ```

4. **Deploy**
   - Railway will automatically detect the `Dockerfile`
   - Build and deploy will start automatically
   - The `PORT` environment variable is automatically set by Railway
   - All services will run on the assigned port

5. **Access Your Backend**
   - Railway provides a public URL (e.g., `https://your-app.railway.app`)
   - The orchestrator will be available at the root URL
   - Update your frontend to use this URL

#### Railway-Specific Notes:

- **Port Configuration**: Railway automatically sets the `PORT` environment variable. The `railway_main.py` script uses this port for the orchestrator.
- **Internal Services**: All agents run on internal ports (8001-8005, 8011) and are accessible via the orchestrator API.
- **MQTT Broker**: You'll need to use an external MQTT broker (e.g., CloudMQTT, HiveMQ) or set up a separate Railway service for MQTT.
- **Health Checks**: The Dockerfile includes a health check that monitors the orchestrator endpoint.
- **Logs**: View logs in Railway dashboard under the "Deployments" tab.

#### Recommended Railway Setup:

1. **Main Backend Service** (this repository)
   - Deploys all agents and orchestrator
   - Exposes single public URL

2. **MQTT Broker Service** (optional, separate)
   - Use Railway's MQTT service or external provider
   - Update `MQTT_BROKER` environment variable

3. **Database Service** (optional, for state persistence)
   - Use Railway's PostgreSQL or MongoDB
   - Update agent configs to use database instead of file-based state

### Docker Deployment (Local/Other Platforms)

```bash
# Build image
docker build -t 6g-mas-backend .

# Run container
docker run -p 8000:8000 --env-file .env 6g-mas-backend

# Or with custom port
docker run -p 3000:8000 -e PORT=8000 --env-file .env 6g-mas-backend
```

### Docker Compose (Local Development)

Create a `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - ./agents:/app/agents
      - ./PM:/app/PM
      - ./PPE_artifacts:/app/PPE_artifacts
      - ./safety_artifacts:/app/safety_artifacts
    healthcheck:
      test: ["CMD", "python", "-c", "import httpx; httpx.get('http://localhost:8000/status', timeout=5)"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  mqtt:
    image: eclipse-mosquitto:latest
    ports:
      - "1883:1883"
    volumes:
      - ./mosquitto.conf:/mosquitto/config/mosquitto.conf
```

## 📊 Monitoring & Logging

- **Logs**: All agents log to console with structured logging
- **Health Checks**: Each agent exposes `/health` endpoint
- **Metrics**: Agent state includes prediction metrics and history
- **Alerting**: Critical alerts trigger Twilio SMS notifications

## 🔐 Security Considerations

- **MQTT**: Consider using TLS/SSL for MQTT connections in production
- **API**: Add authentication middleware (not currently implemented)
- **Environment Variables**: Never commit `.env` files to version control
- **CORS**: Configure `CORS_ORIGINS` appropriately for production

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

[Your License Here]

## 🆘 Troubleshooting

### Common Issues

1. **ModuleNotFoundError**: Ensure you're running from the Backend directory and using `python -m` for module execution
2. **MQTT Connection Failed**: Verify MQTT broker is running and accessible
3. **Model File Not Found**: Check model paths in agent config files
4. **Port Already in Use**: Change port numbers in agent config files or stop conflicting services

### Getting Help

- Check agent logs for detailed error messages
- Verify environment variables are set correctly
- Ensure all dependencies are installed
- Check MQTT broker connectivity

---

**Built with ❤️ for intelligent factory automation**

