# SCADA Bridge - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Prerequisites
- Python 3.11+
- MQTT broker running (mosquitto)
- Ports 4840 and 502 available

### Step 1: Install Dependencies
```bash
cd Backend/scada_bridge
pip install -r requirements.txt
```

### Step 2: Start MQTT Broker
```bash
# Windows
mosquitto

# Linux/Mac
sudo mosquitto
```

### Step 3: Run the Bridge
```bash
python main.py
```

You should see:
```
=========================================================
6G-MAS-Factory SCADA Protocol Bridge
===========================================================
OPC UA server initialized with namespace index: 2
Starting SCADA Bridge services...
SCADA Bridge is now running
  - OPC UA:     opc.tcp://0.0.0.0:4840/freeopcua/server/
  - Modbus TCP: 0.0.0.0:502
  - MQTT:       localhost:1883
===========================================================
```

### Step 4: Test with Simulator (New Terminal)
```bash
python tests/mqtt_simulator.py --interval 3 --count 5
```

### Step 5: Verify OPC UA (New Terminal)
```bash
python tests/test_opcua_client.py
```

### Step 6: Verify Modbus (New Terminal)
```bash
python tests/test_modbus_client.py
```

## ✅ Success Indicators

**Bridge Running:**
- No errors in main.py output
- All three servers started successfully
- Connected to MQTT broker

**Simulator Working:**
- ✓ symbols for each published prediction
- 5 predictions per iteration (all agents)

**OPC UA Test:**
- Connected successfully
- Reads node values (should match simulator values)

**Modbus Test:**
- Connected successfully
- Register values displayed correctly

## 🐛 Troubleshooting

### Port 502 Permission Denied
```bash
# Option 1: Run as admin (Windows PowerShell)
# Right-click PowerShell → Run as Administrator

# Option 2: Change port
# Edit .env file:
MODBUS_PORT=5020
```

### MQTT Connection Failed
```bash
# Check if mosquitto is running
netstat -an | findstr 1883

# Start mosquitto if not running
mosquitto
```

### OPC UA Connection Failed
```bash
# Check port availability
netstat -an | findstr 4840

# Verify no firewall blocking
```

## 📚 Next Steps

1. **Connect Real Agents:** Configure your AI agents to publish to `predictions/{agent_id}`
2. **SCADA Integration:** Connect your SCADA system to OPC UA or Modbus
3. **Railway Deploy:** Push to GitHub and deploy on Railway platform

### Railway Deployment

1. Connect GitHub repository to Railway
2. Railway will auto-detect `requirements.txt`
3. Set environment variables in Railway dashboard:
   - `MQTT_BROKER` - Your MQTT broker hostname
   - `MQTT_PORT` - 1883
   - `OPCUA_PORT` - 4840
   - `MODBUS_PORT` - 502
4. Deploy automatically

See [README.md](README.md) for full documentation.
