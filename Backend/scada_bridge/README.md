# SCADA Protocol Bridge

## Overview

The **SCADA Protocol Bridge** translates predictions from AI agents (via MQTT) into industrial SCADA protocols (OPC UA, Modbus TCP, and DNP3). This enables legacy SCADA systems to access real-time AI predictions for predictive maintenance, energy optimization, cybersecurity, workplace safety, and PPE compliance.

## Architecture

```
MQTT Broker (predictions/# topics)
         ↓
    SCADA Bridge
    ┌─────────────────────┐
    │  MQTT Client        │
    └──────────┬──────────┘
    │  Data Transformer   │
    └──────────┬──────────┘
         ┏━━━━━┻━━━━━┓
    ┌────▼────┐  ┌────▼────┐
    │ OPC UA  │  │ Modbus  │
    │ :4840   │  │ :502    │
    └─────────┘  └─────────┘
```

### Supported Agents
- **PM Agent** (Predictive Maintenance): RUL, health scores, alert levels
- **Energy Agent**: Consumption, efficiency, anomaly detection
- **Cyber Agent**: Threat levels, network health
- **Hazard Agent**: Workplace safety risks, hazard counts
- **PPE Agent**: Compliance rates, violations

## Installation

### Prerequisites
- Python 3.11 or higher
- MQTT Broker (e.g., Mosquitto) running on localhost:1883
- Ports 4840 (OPC UA) and 502 (Modbus) available

### Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment (optional):**
   Create `.env` file:
   ```bash
   MQTT_BROKER=localhost
   MQTT_PORT=1883
   OPCUA_PORT=4840
   MODBUS_PORT=502
   LOG_LEVEL=INFO
   ```

3. **Start the bridge:**
   ```bash
   python main.py
   ```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MQTT_BROKER` | localhost | MQTT broker hostname |
| `MQTT_PORT` | 1883 | MQTT broker port |
| `OPCUA_PORT` | 4840 | OPC UA server port |
| `MODBUS_PORT` | 502 | Modbus TCP port |
| `DNP3_ENABLED` | false | Enable DNP3 outstation |
| `DNP3_PORT` | 20000 | DNP3 outstation port |
| `LOG_LEVEL` | INFO | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `MODBUS_IP_WHITELIST` | (empty) | Comma-separated IPs allowed for Modbus |

## Protocol Details

### OPC UA Server

**Endpoint:** `opc.tcp://localhost:4840/freeopcua/server/`

**Namespace Structure:**
```
MultiAgentSystem/
  ├── SystemStatus/
  │   ├── OverallHealth (Float)
  │   ├── ActiveAgents (Int32)
  │   └── TotalAlerts (Int32)
  │
  ├── PredictiveMaintenance/
  │   ├── RemainingUsefulLife (Float)
  │   ├── HealthScore (Float)
  │   ├── AlertLevel (String)
  │   ├── FailureProbability (Float)
  │   ├── RecommendedAction (String)
  │   ├── ThresholdCritical (Float, R/W)
  │   └── ThresholdWarning (Float, R/W)
  │
  ├── EnergyOptimization/
  ├── CyberSecurity/
  ├── WorkplaceSafety/
  └── PPECompliance/
```

**Connection Example (UA Expert):**
1. Add Server: `opc.tcp://localhost:4840`
2. Connect anonymously
3. Browse to `MultiAgentSystem` folder

### Modbus TCP Server

**Address:** `localhost:502`  
**Unit ID:** 1

**Register Map:**

| Range | Agent | Description |
|-------|-------|-------------|
| 0-99 | Predictive Maintenance | RUL, health, alerts |
| 100-199 | Energy Optimization | Consumption, efficiency |
| 200-299 | Cyber Security | Threats, network health |
| 300-399 | Workplace Safety | Hazards, risk levels |
| 400-499 | PPE Compliance | Compliance rates |
| 500-599 | System Status | Overall system health |

**Data Conversions:**
- Floats multiplied by 10 (e.g., 48.5 kWh → register value 485)
- String enums mapped to integers (e.g., "critical" → 2)
- Booleans: 0=false, 1=true

**Connection Example (pymodbus console):**
```bash
pymodbus.console tcp --host localhost --port 502
> client.read_holding_registers address=0 count=10 unit=1
```

## Testing

### 1. MQTT Simulation

Publish mock predictions:
```bash
python tests/mqtt_simulator.py --interval 5 --count 10
```

This simulates all 5 agents publishing predictions every 5 seconds.

### 2. OPC UA Client Test

Read OPC UA nodes:
```bash
python tests/test_opcua_client.py
```

Verifies OPC UA server is running and nodes are updated.

### 3. Modbus Client Test

Read Modbus registers:
```bash
python tests/test_modbus_client.py
```

Verifies Modbus register values and conversions.

### 4. Bidirectional Test

Test OPC UA write → MQTT config:
```bash
python tests/test_bidirectional.py
```

Writes to a writable OPC UA node and verifies MQTT config message is published.

### 5. Load Test

Performance test:
```bash
python tests/load_test.py --rate 100 --duration 60
```

Tests bridge with 100 predictions/second for 60 seconds.

## MQTT Topics

### Input (Subscribe)
- `predictions/pm_agent` - Predictive maintenance predictions
- `predictions/energy_agent` - Energy optimization predictions
- `predictions/cyber_agent` - Cybersecurity predictions
- `predictions/hazard_agent` - Workplace safety predictions
- `predictions/ppe_agent` - PPE compliance predictions

**Payload Format:**
```json
{
  "agent_id": "pm_agent",
  "timestamp": "2024-11-30T10:30:00Z",
  "prediction": {
    "rul_hours": 48.5,
    "health_score": 87.3,
    "alert_level": "warning",
    "failure_probability": 0.23,
    "recommended_action": "Schedule maintenance"
  }
}
```

### Output (Publish)
- `config/pm_agent` - Configuration updates from SCADA writes
- `config/energy_agent` - Energy agent config
- etc.

## Troubleshooting

### OPC UA Server won't start
- Check port 4840 is not in use: `netstat -an | findstr 4840`
- Verify asyncua installed: `pip show asyncua`

### Modbus Server won't start
- Port 502 requires admin privileges on some systems
- Change to port 5020 in config if needed
- Check firewall settings

### MQTT Connection fails
- Verify MQTT broker is running: `mosquitto -v`
- Check broker address in config
- Test connection: `mosquitto_pub -h localhost -t test -m "hello"`

### No data updating
- Ensure agents are publishing to `predictions/#` topics
- Check MQTT client logs in bridge output
- Verify JSON payload format matches expected schema

## Integration Examples

### Ignition SCADA (OPC UA)
1. Add new OPC UA connection in Ignition Designer
2. Set endpoint: `opc.tcp://localhost:4840`
3. Browse tags from `MultiAgentSystem` namespace
4. Drag tags to designer to create visualizations

### Python Modbus Client
```python
from pymodbus.client import ModbusTcpClient

client = ModbusTcpClient('localhost', port=502)
client.connect()

# Read PM health score (register 1)
result = client.read_holding_registers(address=1, count=1, unit=1)
health_score = result.registers[0]
print(f"Health Score: {health_score}")

client.close()
```

## Performance

- **Update Latency:** <100ms from MQTT receipt to protocol update
- **Concurrent Clients:** 10+ simultaneous SCADA connections
- **Throughput:** 100+ predictions/second
- **Reliability:** >99% success rate under load

## File Structure

```
scada_bridge/
├── main.py                 # Main entry point
├── config.py               # Configuration
├── mqtt_client.py          # MQTT client
├── opcua_server.py         # OPC UA server
├── modbus_server.py        # Modbus TCP server
├── dnp3_server.py          # DNP3 outstation (stub)
├── data_transformer.py     # Protocol transformations
├── requirements.txt        # Dependencies
└── tests/
    ├── mqtt_simulator.py        # Mock prediction publisher
    ├── test_opcua_client.py     # OPC UA test client
    ├── test_modbus_client.py    # Modbus test client
    ├── test_bidirectional.py    # Bidirectional write test
    └── load_test.py             # Performance test
```

## Deployment on Railway

This bridge is designed to be deployed on Railway:

1. **Connect Repository:** Link your GitHub repository to Railway
2. **Set Environment Variables:** Configure in Railway dashboard:
   - `MQTT_BROKER` - Your MQTT broker hostname
   - `MQTT_PORT` - MQTT port (default: 1883)
   - `OPCUA_PORT` - OPC UA port (default: 4840)
   - `MODBUS_PORT` - Modbus port (default: 502)
   - `LOG_LEVEL` - Logging level (default: INFO)

3. **Deploy:** Railway will automatically detect `requirements.txt` and deploy

4. **Access:** Use Railway's provided URL to connect SCADA clients



## License

MIT License - 6G-MAS-Factory Project
