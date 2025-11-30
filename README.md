# 6G-MAS-Factory: Multi-Agent System for Industrial IIoT

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
- [Architecture](#architecture)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Documentation](#documentation)
- [Project Structure](#project-structure)
- [Deployment](#deployment)
- [Contributing](#contributing)

---

## 🎯 Overview

The **6G-MAS-Factory** is an advanced Industrial Internet of Things (IIoT) monitoring system that uses AI-powered agents to:

- 🔧 **Predict machine failures** before they occur (Predictive Maintenance)
- ⚡ **Optimize energy consumption** and detect anomalies
- 🛡️ **Detect cybersecurity threats** in real-time
- 🏭 **Monitor workplace safety** hazards
- 👷 **Ensure PPE compliance** using computer vision

The system processes sensor data via MQTT, runs ML/DL models for predictions, and provides a beautiful Next.js dashboard for monitoring and alerts.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Next.js)                      │
│                    Port 3000 - Dashboard                      │
└────────────────────┬────────────────────────────────────────┘
                     │ Server Actions (HTTP)
                     │
┌────────────────────▼────────────────────────────────────────┐
│                  Orchestrator (FastAPI)                      │
│              Port 8000 - API Gateway                         │
└────────────────────┬────────────────────────────────────────┘
                     │
         ┌───────────┴──────────┬──────────────┐
         │                      │              │
┌────────▼─────────┐  ┌────────▼─────────┐   │
│   Planner Agent  │  │   MQTT Broker    │   │
│   Port 8011      │  │   Port 1883      │   │
└──────────────────┘  └──────────────────┘   │
                                              │
                      ┌───────────────────────┴─────────────┐
                      │        AI Agents (Ports 8001-8005)   │
                      ├──────────────────────────────────────┤
                      │ • PM Agent (Predictive Maintenance)  │
                      │ • Energy Agent                       │
                      │ • Cyber Security Agent               │
                      │ • Safety Agent                       │
                      │ • PPE Agent                          │
                      └──────────────────────────────────────┘
                                    ▲
                                    │ MQTT
                      ┌─────────────┴──────────────┐
                      │  Publisher (Data Simulator) │
                      │  manufacturing_6G_dataset   │
                      └────────────────────────────┘
```

### Components

#### Frontend
- **Framework**: Next.js 15 with TypeScript
- **UI**: Radix UI + Tailwind CSS
- **Charts**: VChart for data visualization
- **Integration**: Server Actions for backend communication

#### Backend
- **5 AI Agents**: Each with ML/DL models for specific tasks
- **Orchestrator**: Central coordinator and API gateway
- **Planner**: High-level decision-making service
- **MQTT**: Message broker for sensor data
- **Publisher**: Simulates real-time factory telemetry

---

## ✨ Features

### Dashboard Features
- 📊 **Real-time Monitoring**: Live data from all agents
- 📈 **Interactive Charts**: VChart-powered visualizations
- 🔔 **Alert System**: Critical alerts and notifications
- 🌓 **Dark Mode**: Full dark/light theme support
- 📱 **Responsive Design**: Works on all devices

### AI Agent Capabilities
- 🤖 **PM Agent**: LSTM-based RUL prediction, health scoring
- ⚡ **Energy Agent**: Anomaly detection, efficiency optimization
- 🔒 **Cyber Agent**: Threat detection, network monitoring
- ⚠️ **Safety Agent**: Hazard detection, risk assessment
- 👷 **PPE Agent**: Computer vision-based compliance checking

### System Features
- 🔄 **Microservices Architecture**: Scalable and maintainable
- 🐳 **Docker Support**: Easy deployment with Docker Compose
- 🔌 **MQTT Protocol**: Efficient real-time data streaming
- 🌐 **REST APIs**: FastAPI for high-performance endpoints
- 🔗 **WebSockets**: Real-time predictions streaming

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

### Backend
- **Language**: Python 3.11+
- **API Framework**: FastAPI
- **Server**: Uvicorn (ASGI)
- **Messaging**: Paho MQTT
- **ML/DL**: TensorFlow, scikit-learn, NumPy, Pandas
- **HTTP Client**: httpx

### Infrastructure
- **Containerization**: Docker, Docker Compose
- **Message Broker**: Eclipse Mosquitto
- **Deployment**: Railway (Backend), Vercel (Frontend)

---

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

**Prerequisites**: Docker and Docker Compose installed

```bash
# Clone the repository
cd "c:/Users/sraye/OneDrive/Desktop/IAS technical Chalenge/ias_tech_challenge"

# Start all backend services with ONE command!
docker-compose up

# In a new terminal, start the frontend
cd Frontend
pnpm install
pnpm dev
```

✅ **Done!** Access the dashboard at [http://localhost:3000](http://localhost:3000)

See **[DOCKER_QUICKSTART.md](./DOCKER_QUICKSTART.md)** for more details.

---

### Option 2: Manual Setup

**Prerequisites**: Python 3.11+, Node.js 18+, MQTT Broker (Mosquitto)

#### Backend Setup
```bash
cd Backend

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
# source venv/bin/activate    # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Start services (in separate terminals)
cd agents/orchestrator && uvicorn main:app --port 8000 --reload
cd agents/planner && uvicorn main:app --port 8011 --reload
cd agents/maint && python main.py
cd agents/energy && python main.py
cd agents/cyber && python main.py
cd agents/safety && python main.py
cd agents/ppe && python main.py
cd publisher && python main.py
```

#### Frontend Setup
```bash
cd Frontend

# Install dependencies
pnpm install

# Create environment file
cp .env.local.example .env.local

# Start development server
pnpm dev
```

See **[SETUP_GUIDE.md](./SETUP_GUIDE.md)** for detailed step-by-step instructions.

---

## 📚 Documentation

### Core Documentation
- **[SETUP_GUIDE.md](./SETUP_GUIDE.md)** - Complete setup guide (manual installation)
- **[DOCKER_QUICKSTART.md](./DOCKER_QUICKSTART.md)** - Quick start with Docker Compose
- **[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)** - Production deployment (Railway + Vercel)

### Frontend Documentation
- **[Frontend/README.md](./Frontend/README.md)** - Frontend-specific documentation
- **[Frontend/.env.local.example](./Frontend/.env.local.example)** - Environment variables template

### Backend Documentation
- **[Backend/README.md](./Backend/README.md)** - Backend architecture and agents

### API Documentation
Once running, visit:
- **Orchestrator API**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Planner API**: [http://localhost:8011/docs](http://localhost:8011/docs)
- **PM Agent API**: [http://localhost:8001/docs](http://localhost:8001/docs)
- *(And so on for ports 8002-8005)*

---

## 📁 Project Structure

```
ias_tech_challenge/
├── Backend/
│   ├── agents/
│   │   ├── orchestrator/      # Central API Gateway (Port 8000)
│   │   ├── planner/           # Decision-making service (Port 8011)
│   │   ├── maint/             # Predictive Maintenance (Port 8001)
│   │   ├── energy/            # Energy Optimization (Port 8002)
│   │   ├── cyber/             # Cybersecurity (Port 8003)
│   │   ├── safety/            # Safety Monitoring (Port 8004)
│   │   ├── ppe/               # PPE Compliance (Port 8005)
│   │   ├── base_agent.py      # Base agent class
│   │   ├── config/            # Agent configurations
│   │   └── utils/             # Shared utilities
│   ├── publisher/             # Data simulator
│   ├── scada_bridge/          # SCADA integration (optional)
│   ├── Dockerfile             # Container definition
│   ├── requirements.txt       # Python dependencies
│   ├── railway_main.py        # Production deployment script
│   └── README.md              # Backend documentation
│
├── Frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── actions/       # Server Actions (Backend API)
│   │   │   ├── (dashboard)/   # Dashboard page
│   │   │   ├── maintenance/   # Maintenance page
│   │   │   ├── machines/      # Machines monitoring
│   │   │   ├── PPE/           # PPE compliance page
│   │   │   └── ...            # Other pages
│   │   ├── components/        # React components
│   │   │   ├── ui/            # shadcn/ui components
│   │   │   ├── chart-blocks/  # Chart components
│   │   │   └── backend-status-example.tsx
│   │   ├── types/             # TypeScript types
│   │   ├── data/              # Static data (fallback)
│   │   └── lib/               # Utilities
│   ├── public/                # Static assets
│   ├── .env.local.example     # Environment template
│   ├── package.json           # Dependencies
│   └── README.md              # Frontend documentation
│
├── docker-compose.yml         # Multi-service orchestration
├── mosquitto.conf             # MQTT broker config
├── SETUP_GUIDE.md             # Manual setup guide
├── DOCKER_QUICKSTART.md       # Docker quick start
├── DEPLOYMENT_GUIDE.md        # Production deployment
└── README.md                  # This file
```

---

## 🌐 Deployment

### Production Deployment (Railway + Vercel)

#### Backend on Railway
```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy backend
cd Backend
railway login
railway init
railway up
```

#### Frontend on Vercel
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy frontend
cd Frontend
vercel login
vercel --prod
```

See **[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)** for complete production deployment instructions.

---

## 🔧 Configuration

### Backend Environment Variables
Set in Railway or `.env`:
```env
CORS_ORIGINS=https://your-frontend.vercel.app,http://localhost:3000
PLANNER_URL=http://planner:8011
MQTT_BROKER=localhost  # Or CloudAMQP URL
MQTT_PORT=1883
```

### Frontend Environment Variables
Create `.env.local`:
```env
ORCHESTRATOR_URL=http://localhost:8000
PM_AGENT_URL=http://localhost:8001
ENERGY_AGENT_URL=http://localhost:8002
CYBER_AGENT_URL=http://localhost:8003
SAFETY_AGENT_URL=http://localhost:8004
PPE_AGENT_URL=http://localhost:8005
```

For production, these should point to your Railway deployment.

---

## 🧪 Testing

### Verify Backend Services
```bash
# Check all agents
curl http://localhost:8000/system-state
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
curl http://localhost:8004/health
curl http://localhost:8005/health
```

### Verify Frontend Integration
1. Open browser to [http://localhost:3000](http://localhost:3000)
2. Check browser console (F12) for API calls
3. Verify data is loading from backend (not static)

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

---

## 📞 Support

For issues and questions:
1. Check the [SETUP_GUIDE.md](./SETUP_GUIDE.md) troubleshooting section
2. Review [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for production issues
3. Open an issue on GitHub

---

## 🗺️ Roadmap

- [ ] WebSocket integration for real-time updates
- [ ] Advanced ML model improvements
- [ ] Historical data analytics
- [ ] Mobile app (React Native)
- [ ] Advanced alert routing (Twilio, Email)
- [ ] Multi-tenant support

---

**Built with ❤️ for Industrial IIoT**

*Powered by AI Agents • Real-time MQTT • Modern Web Technologies*
