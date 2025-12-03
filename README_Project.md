# 6G-MAS Factory: Multi-Agent System for Industrial IIoT

[![Next.js](https://img.shields.io/badge/Next.js-15-black)](https://nextjs.org/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue)](https://www.docker.com/)

A comprehensive **Multi-Agent System (MAS)** for industrial IIoT factory monitoring and predictive maintenance, featuring real-time data processing, AI-powered decision-making, and a modern web dashboard.

![Architecture](https://img.shields.io/badge/Architecture-Microservices-orange)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Deployment](#deployment)
- [Testing](#testing)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [Documentation](#documentation)

---

## 🎯 Overview

The **6G-MAS Factory** is an advanced Industrial Internet of Things (IIoT) monitoring system that uses AI-powered agents to:

- 🔧 **Predict machine failures** before they occur (Predictive Maintenance)
- ⚡ **Optimize energy consumption** and detect anomalies
- 🛡️ **Detect cybersecurity threats** in real-time
- 🏭 **Monitor workplace safety** hazards
- 👷 **Ensure PPE compliance** using computer vision
- 📊 **Generate shift backlogs** using AI-powered analysis

The system processes sensor data via MQTT, runs ML/DL models for predictions, and provides a beautiful Next.js dashboard for monitoring and alerts. All backend services are unified behind a single API gateway (Nginx) for production-ready deployment.

---

## ✨ Key Features

### 🤖 AI-Powered Agents

- **Predictive Maintenance Agent**: LSTM-based RUL (Remaining Useful Life) prediction, health scoring, and maintenance scheduling
- **Energy Optimization Agent**: Anomaly detection using Isolation Forest, efficiency scoring, and consumption optimization
- **Cyber Security Agent**: Real-time threat detection, network anomaly identification, and security monitoring
- **Safety Agent**: Workplace hazard detection, risk assessment, and safety scoring
- **PPE Compliance Agent**: Computer vision-based personal protective equipment compliance checking
- **Backlog Agent**: AI-powered shift backlog generation using Google Gemini API

### 📊 Dashboard Features

- **Real-time Monitoring**: Live data from all agents with automatic refresh
- **Interactive Charts**: VChart-powered visualizations for trends and analytics
- **Alert System**: Critical alerts with Twilio SMS notifications
- **Dark Mode**: Full dark/light theme support
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Multi-page Navigation**: Dedicated pages for maintenance, machines, PPE, backlog, and sensitization

### 🏗️ System Architecture

- **Microservices Architecture**: Scalable and maintainable agent-based design
- **Single API Gateway**: Nginx reverse proxy consolidates all backend services
- **MQTT Protocol**: Efficient real-time data streaming
- **REST APIs**: FastAPI for high-performance endpoints
- **WebSocket Support**: Real-time predictions streaming (ready for implementation)
- **Docker Support**: Easy deployment with Docker Compose
- **Production-Ready**: Configured for Netlify (Frontend) and Railway/VPS (Backend)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                        │
│              Deployed on Netlify / Port 3000                  │
│              Single API Gateway URL                           │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP/HTTPS
                     │ NEXT_PUBLIC_API_GATEWAY
                     │
┌────────────────────▼────────────────────────────────────────┐
│              Nginx API Gateway (Port 8080)                    │
│              Single Entry Point for All Services              │
└────────────────────┬────────────────────────────────────────┘
                     │
         ┌───────────┴──────────┬──────────────┐
         │                      │              │
┌────────▼─────────┐  ┌────────▼─────────┐   │
│   Orchestrator  │  │   Planner Agent  │   │
│   Port 8000     │  │   Port 8011      │   │
│   /api/orch...  │  └──────────────────┘   │
└──────────────────┘                         │
                                              │
                      ┌───────────────────────┴─────────────┐
                      │        AI Agents (Ports 8001-8005)   │
                      ├──────────────────────────────────────┤
                      │ • PM Agent      /api/pm              │
                      │ • Energy Agent  /api/energy           │
                      │ • Cyber Agent   /api/cyber            │
                      │ • Safety Agent  /api/safety           │
                      │ • PPE Agent     /api/ppe              │
                      └──────────────────────────────────────┘
                                    ▲
                                    │ MQTT
                      ┌─────────────┴──────────────┐
                      │  MQTT Broker (Mosquitto)   │
                      │  Port 1883                 │
                      └─────────────┬──────────────┘
                                    │
                      ┌─────────────▼──────────────┐
                      │  Publisher (Data Simulator) │
                      │  manufacturing_6G_dataset  │
                      └────────────────────────────┘
```

### Key Architectural Decisions

1. **Single API Gateway**: All backend services are exposed through one Nginx reverse proxy, eliminating the need for multiple port configurations
2. **Environment-Based Configuration**: Frontend uses `NEXT_PUBLIC_API_GATEWAY` to point to the backend gateway URL
3. **Twilio Integration**: Critical alerts are sent via SMS/WhatsApp using Twilio
4. **Docker Compose**: All services run in containers for easy deployment and scaling

---

## 🛠️ Tech Stack

### Frontend
- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **UI Components**: Radix UI, shadcn/ui
- **Styling**: Tailwind CSS
- **Charts**: @visactor/vchart
- **State**: Jotai
- **Package Manager**: pnpm
- **Deployment**: Netlify

### Backend
- **Language**: Python 3.11+
- **API Framework**: FastAPI
- **Server**: Uvicorn (ASGI)
- **Messaging**: Paho MQTT
- **ML/DL**: TensorFlow, scikit-learn, NumPy, Pandas
- **HTTP Client**: httpx
- **Notifications**: Twilio (SMS/WhatsApp)
- **Reverse Proxy**: Nginx
- **Deployment**: Railway, Render, or VPS

### Infrastructure
- **Containerization**: Docker, Docker Compose
- **Message Broker**: Eclipse Mosquitto
- **Testing**: pytest, pytest-asyncio

---

## 🚀 Quick Start

### Prerequisites

- **Docker & Docker Compose** (for easiest setup)
- OR **Python 3.11+** and **Node.js 18+** (for manual setup)
- **MQTT Broker** (Mosquitto) - included in Docker Compose

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd ias_tech_challenge

# Start all backend services
docker-compose up -d

# Start frontend (in a new terminal)
cd Frontend
pnpm install
pnpm dev
```

✅ **Done!** Access the dashboard at [http://localhost:3000](http://localhost:3000)

The backend API gateway is available at [http://localhost:8080](http://localhost:8080)

### Option 2: Manual Setup

#### Backend Setup

```bash
cd Backend

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
# source venv/bin/activate    # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp env.template .env
# Edit .env with your API keys (Twilio, Gemini, etc.)

# Start services (see Backend/README.md for details)
```

#### Frontend Setup

```bash
cd Frontend

# Install dependencies
pnpm install

# Create environment file
echo "NEXT_PUBLIC_API_GATEWAY=http://localhost:8080" > .env.local

# Start development server
pnpm dev
```

See **[Backend/README.md](./Backend/README.md)** and **[Frontend/README.md](./Frontend/README.md)** for detailed setup instructions.

---

## 🌐 Deployment

### Production Architecture

- **Frontend**: Deployed on **Netlify** (or Vercel)
- **Backend**: Deployed on **Railway**, **Render**, or a **VPS** (DigitalOcean, AWS, etc.)
- **API Gateway**: Nginx reverse proxy (included in Docker Compose)

### Backend Deployment (Railway/Render/VPS)

1. **Push code to GitHub**
2. **Deploy using Docker Compose** on your platform
3. **Set environment variables**:
   - `TWILIO_ACCOUNT_SID`
   - `TWILIO_AUTH_TOKEN`
   - `TWILIO_FROM_NUMBER`
   - `TWILIO_TO_NUMBER`
   - `GEMINI_API_KEY` (for Backlog Agent)
   - `HF_MODEL_REPO` (optional, for Hugging Face models)
4. **Get your backend URL** (e.g., `https://mas-backend-production.up.railway.app`)

### Frontend Deployment (Netlify)

1. **Connect GitHub repository** to Netlify
2. **Set build settings**:
   - **Base directory**: `Frontend`
   - **Build command**: `pnpm build` (or `npm run build`)
   - **Publish directory**: `.next`
3. **Set environment variable**:
   - `NEXT_PUBLIC_API_GATEWAY`: Your backend gateway URL (from step above)
4. **Deploy!**

See **[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)** for complete deployment instructions.

---

## 🧪 Testing

### Backend Tests

```bash
cd Backend

# Install test dependencies
venv\Scripts\python -m pip install pytest pytest-asyncio

# Run all tests
venv\Scripts\python -m pytest

# Run specific test file
venv\Scripts\python -m pytest tests/test_orchestrator.py
```

**Test Coverage**:
- ✅ Unit tests for all agents (PM, Energy, Cyber, Safety, PPE, Backlog)
- ✅ Integration tests for Orchestrator API
- ✅ Twilio notification tests
- ✅ Alert handling and state management tests

### Frontend Tests

Frontend testing can be added using Jest/Vitest and React Testing Library (not yet implemented).

---

## ⚙️ Configuration

### Backend Environment Variables

Copy `Backend/env.template` to `Backend/.env` and fill in your values:

```env
# Twilio SMS Notifications
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_FROM_NUMBER=+1234567890
TWILIO_TO_NUMBER=+0987654321

# Google Gemini API (for Backlog Agent)
GEMINI_API_KEY=your_gemini_api_key

# Hugging Face (optional)
HF_MODEL_REPO=your-org/your-model-repo

# MQTT Configuration
MQTT_BROKER=localhost
MQTT_PORT=1883

# Orchestrator
CORS_ORIGINS=*
PLANNER_URL=http://planner:8011
```

### Frontend Environment Variables

Create `Frontend/.env.local`:

```env
# Backend API Gateway URL
NEXT_PUBLIC_API_GATEWAY=http://localhost:8080

# For production, use your deployed backend URL:
# NEXT_PUBLIC_API_GATEWAY=https://mas-backend-production.up.railway.app
```

---

## 📁 Project Structure

```
ias_tech_challenge/
├── Backend/
│   ├── agents/
│   │   ├── orchestrator/      # Central API Gateway (Port 8000)
│   │   ├── planner/           # Decision-making service (Port 8011)
│   │   ├── maint/            # Predictive Maintenance (Port 8001)
│   │   ├── energy/            # Energy Optimization (Port 8002)
│   │   ├── cyber/             # Cybersecurity (Port 8003)
│   │   ├── safety/            # Safety Monitoring (Port 8004)
│   │   ├── ppe/               # PPE Compliance (Port 8005)
│   │   ├── backlog/           # Backlog Generation Agent
│   │   ├── base_agent.py      # Base agent class
│   │   ├── config/             # Agent configurations
│   │   └── utils/              # Shared utilities (Twilio, etc.)
│   ├── nginx/                  # Nginx reverse proxy config
│   ├── tests/                  # Test suite
│   ├── publisher/              # Data simulator
│   ├── scada_bridge/           # SCADA integration (optional)
│   ├── Dockerfile              # Container definition
│   ├── requirements.txt        # Python dependencies
│   ├── env.template            # Environment variables template
│   └── README.md               # Backend documentation
│
├── Frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── actions/        # Server Actions (Backend API)
│   │   │   ├── (dashboard)/   # Dashboard page
│   │   │   ├── maintenance/   # Maintenance page
│   │   │   ├── machines/       # Machines monitoring
│   │   │   ├── PPE/            # PPE compliance page
│   │   │   └── ...             # Other pages
│   │   ├── components/         # React components
│   │   ├── types/              # TypeScript types
│   │   └── lib/                # Utilities
│   ├── public/                 # Static assets
│   ├── netlify.toml            # Netlify configuration
│   └── README.md               # Frontend documentation
│
├── docker-compose.yml          # Multi-service orchestration
├── mosquitto.conf              # MQTT broker config
├── SETUP_GUIDE.md              # Manual setup guide
├── DOCKER_QUICKSTART.md        # Docker quick start
├── DEPLOYMENT_GUIDE.md         # Production deployment
└── README.md                   # This file
```

---

## 📚 Documentation

### Core Documentation
- **[Backend/README.md](./Backend/README.md)** - Backend architecture, agents, and API documentation
- **[Frontend/README.md](./Frontend/README.md)** - Frontend setup, components, and integration guide
- **[SETUP_GUIDE.md](./SETUP_GUIDE.md)** - Complete manual setup guide
- **[DOCKER_QUICKSTART.md](./DOCKER_QUICKSTART.md)** - Quick start with Docker Compose
- **[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)** - Production deployment guide

### API Documentation
Once running, visit:
- **API Gateway**: [http://localhost:8080/api/orchestrator/docs](http://localhost:8080/api/orchestrator/docs)
- **PM Agent**: [http://localhost:8080/api/pm/docs](http://localhost:8080/api/pm/docs)
- **Energy Agent**: [http://localhost:8080/api/energy/docs](http://localhost:8080/api/energy/docs)
- *(And so on for other agents)*

---

## 🔧 Key Features Explained

### 1. Single API Gateway Architecture

Instead of exposing multiple ports (8000-8005), all backend services are unified behind a single Nginx reverse proxy on port 8080. This provides:

- **Security**: Only one port exposed to the internet
- **CORS Management**: Centralized CORS configuration
- **Load Balancing**: Ready for horizontal scaling
- **SSL/TLS**: Easy to add HTTPS termination

### 2. Twilio SMS Integration

Critical alerts from any agent trigger SMS notifications via Twilio:

- **Automatic**: No manual configuration needed
- **Reliable**: Handles failures gracefully
- **Configurable**: Environment variables for credentials

### 3. AI-Powered Backlog Generation

The Backlog Agent collects violations and anomalies during 8-hour shifts and generates comprehensive reports using Google Gemini API.

### 4. Production-Ready Deployment

- **Frontend**: Optimized for Netlify with Next.js plugin
- **Backend**: Docker Compose ready for Railway/Render/VPS
- **Environment Variables**: Template files for easy configuration

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgments

- **Next.js** - React framework
- **FastAPI** - Python web framework
- **Eclipse Mosquitto** - MQTT broker
- **Radix UI** - Component primitives
- **VChart** - Visualization library
- **Twilio** - SMS/WhatsApp notifications
- **Google Gemini** - AI-powered backlog generation

---

## 📞 Support

For issues and questions:
1. Check the documentation in `Backend/README.md` and `Frontend/README.md`
2. Review [SETUP_GUIDE.md](./SETUP_GUIDE.md) troubleshooting section
3. Review [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for production issues
4. Open an issue on GitHub

---

## 🗺️ Roadmap

- [x] Single API Gateway (Nginx)
- [x] Twilio SMS integration
- [x] Comprehensive test suite
- [x] Production deployment configuration
- [ ] WebSocket integration for real-time updates
- [ ] Advanced ML model improvements
- [ ] Historical data analytics
- [ ] Mobile app (React Native)
- [ ] Multi-tenant support

---

**Built with ❤️ for Industrial IIoT**

*Powered by AI Agents • Real-time MQTT • Modern Web Technologies • Production-Ready Architecture*

