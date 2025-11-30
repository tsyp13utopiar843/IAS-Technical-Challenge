# 6G-MAS-Factory Backend

This repository contains the backend infrastructure for the **6G-MAS-Factory** (Multi-Agent System) project. It is designed as a distributed system of autonomous AI agents, orchestrators, and protocol bridges, communicating via MQTT and HTTP/WebSockets.

## 🏗️ Architecture Overview

The backend is built on a **Microservices Architecture** where each AI agent runs as an independent service.

### Core Components

1.  **AI Agents**: Autonomous agents responsible for specific domains.
    *   **Predictive Maintenance (PM) Agent**: Predicts machine failures and RUL.
    *   **Energy Optimization Agent**: Monitors consumption and suggests efficiency improvements.
    *   **Cyber Security Agent**: Detects network threats and anomalies.
    *   **Workplace Safety Agent**: Monitors hazards using computer vision (simulated).
    *   **PPE Compliance Agent**: Ensures personal protective equipment compliance.
2.  **Orchestrator**: A central coordinator that aggregates alerts from all agents and queries the Planner for high-level decisions.
3.  **Planner**: An AI service that generates action plans based on aggregated alerts.
4.  **SCADA Bridge**: A protocol gateway that translates MQTT data into industrial protocols (OPC UA, Modbus TCP, DNP3) for integration with legacy systems.
5.  **Protocol Gateway**: A lightweight bridge for routing MQTT telemetry to agent REST APIs (optional/legacy path).
6.  **Publisher**: A simulation tool that replays the `manufacturing_6G_dataset.csv` to MQTT, mimicking real-time factory telemetry.

### Communication Flow

*   **Telemetry**: Factory sensors (simulated by `Publisher`) publish data to MQTT topics (`factory/#`).
*   **Ingestion**: Agents subscribe to relevant MQTT topics OR receive data via HTTP from the Protocol Gateway.
*   **Processing**: Agents process data using local ML/DL models (LSTMs, Isolation Forests, etc.).
*   **Output**: Agents publish predictions/alerts to MQTT (`predictions/#`) and expose them via REST APIs and WebSockets.
*   **Coordination**: The Orchestrator polls or receives alerts from agents and maintains a system-wide state.

---

## 🚀 Getting Started

### Prerequisites

*   **Python 3.11+**
*   **MQTT Broker**: [Mosquitto](https://mosquitto.org/download/) (running on `localhost:1883`)
*   **Virtual Environment** (recommended)

### Installation

It is recommended to set up a virtual environment for the entire backend or separate ones for each component.

```bash
# Example: Setting up a shared environment (simplest for dev)
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies for all components
pip install -r scada_bridge/requirements.txt
pip install -r agents/energy/requirements.txt
# ... repeat for other agents if they have unique requirements
# Common requirements: fastapi, uvicorn, paho-mqtt, numpy, pandas, tensorflow/torch
```

---

## 🏃‍♂️ Step-by-Step Run Guide

To run the full system, you need to start multiple processes. It's best to use separate terminal tabs.

### 1. Start MQTT Broker
Ensure Mosquitto is running.
```bash
mosquitto -v
```

### 2. Start the Orchestrator
The central API for the dashboard.
```bash
cd agents/orchestrator
uvicorn main:app --port 8000 --reload
```
*   **URL**: `http://localhost:8000`

### 3. Start the Planner
Required by the Orchestrator.
```bash
cd agents/planner
uvicorn main:app --port 8011 --reload
```

### 4. Start AI Agents
Start each agent in a separate terminal.

**Predictive Maintenance (Maint) Agent:**
```bash
cd agents/maint
python main.py
```
*   **API**: `http://localhost:8001`
*   **WebSocket**: `ws://localhost:8001/ws`

**Energy Agent:**
```bash
cd agents/energy
python main.py
```
*   **API**: `http://localhost:8002`
*   **WebSocket**: `ws://localhost:8002/ws`

**Cyber Security Agent:**
```bash
cd agents/cyber
python main.py
```
*   **API**: `http://localhost:8003`
*   **WebSocket**: `ws://localhost:8003/ws`

**Safety & PPE Agents:**
```bash
cd agents/safety
python main.py
# and
cd agents/ppe
python main.py
```
*   **Safety API**: `http://localhost:8004`
*   **PPE API**: `http://localhost:8005`

### 5. Start SCADA Bridge (Optional)
If you need OPC UA / Modbus integration.
```bash
cd scada_bridge
python main.py
```

### 6. Start Data Simulation (Publisher)
This will start feeding data into the system.
```bash
cd publisher
python main.py
```

---

## 🔌 Connecting to the Frontend

The frontend (e.g., Next.js Dashboard) can connect to the backend using three primary methods:

### Method 1: Orchestrator API (Recommended for State)
Use the Orchestrator's REST API to get a high-level view of the system.

*   **Endpoint**: `GET http://localhost:8000/system-state`
*   **Response**:
    ```json
    {
      "alerts": [...],
      "decisions": [...],
      "last_update": "2023-10-27T10:00:00Z"
    }
    ```
*   **Usage**: Polling every 1-5 seconds to update the dashboard's main status view.

### Method 2: Agent WebSockets (Recommended for Real-time Charts)
Connect directly to each agent's WebSocket for real-time streaming of predictions and telemetry.

*   **PM Agent**: `ws://localhost:8001/ws`
*   **Energy Agent**: `ws://localhost:8002/ws`
*   **Cyber Agent**: `ws://localhost:8003/ws`
*   **Safety Agent**: `ws://localhost:8004/ws`
*   **Protocol**: The WebSocket sends JSON messages whenever a new prediction is made (typically every few seconds).
    ```json
    {
      "agent_id": "energy_agent",
      "timestamp": "...",
      "prediction": {
        "consumption_kwh": 45.2,
        "efficiency_score": 92.1,
        "alert_level": "normal"
      }
    }
    ```

### Method 3: MQTT over WebSockets (Advanced)
If your frontend supports MQTT (e.g., using `mqtt.js`), you can subscribe directly to the broker.
*   **Broker**: `ws://localhost:9001` (Ensure Mosquitto is configured for WebSockets)
*   **Topics**:
    *   `predictions/#`: All agent predictions.
    *   `factory/#`: Raw telemetry data.

### Method 4: SCADA Integration
For industrial HMIs (like Ignition or node-red):
*   **OPC UA**: `opc.tcp://localhost:4840`
*   **Modbus TCP**: `localhost:502`

## 🛠️ Troubleshooting

*   **Ports in Use**: If a port is taken, check `config` folders in each agent directory or `.env` files to change the port.
*   **No Data**: Ensure the `publisher` is running and the MQTT broker is accessible.
*   **Missing Models**: If agents fail to start due to missing models, run `python create_dummy_models.py` in the `Backend` root to generate placeholder models.
