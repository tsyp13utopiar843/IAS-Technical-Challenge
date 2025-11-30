"""
Configuration module for SCADA Bridge.
Loads settings from environment variables with sensible defaults.
"""
import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

# MQTT Configuration
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_KEEPALIVE = int(os.getenv("MQTT_KEEPALIVE", "60"))
MQTT_RETRY_DELAY = int(os.getenv("MQTT_RETRY_DELAY", "5"))

# OPC UA Configuration
OPCUA_PORT = int(os.getenv("OPCUA_PORT", "4840"))
OPCUA_ENDPOINT = f"opc.tcp://0.0.0.0:{OPCUA_PORT}/freeopcua/server/"
OPCUA_NAMESPACE = "http://6g-mas-factory.com"
OPCUA_SERVER_NAME = "6G-MAS-Factory SCADA Bridge"

# Security
OPCUA_ALLOW_ANONYMOUS = os.getenv("OPCUA_ALLOW_ANONYMOUS", "true").lower() == "true"
OPCUA_USERNAME = os.getenv("OPCUA_USERNAME", "admin")
OPCUA_PASSWORD = os.getenv("OPCUA_PASSWORD", "admin123")

# Modbus Configuration
MODBUS_PORT = int(os.getenv("MODBUS_PORT", "502"))
MODBUS_HOST = os.getenv("MODBUS_HOST", "0.0.0.0")
MODBUS_UNIT_ID = int(os.getenv("MODBUS_UNIT_ID", "1"))

# IP Whitelist for Modbus (comma-separated, empty = allow all)
MODBUS_IP_WHITELIST_STR = os.getenv("MODBUS_IP_WHITELIST", "")
MODBUS_IP_WHITELIST: List[str] = [ip.strip() for ip in MODBUS_IP_WHITELIST_STR.split(",") if ip.strip()]

# DNP3 Configuration
DNP3_ENABLED = os.getenv("DNP3_ENABLED", "false").lower() == "true"
DNP3_PORT = int(os.getenv("DNP3_PORT", "20000"))
DNP3_HOST = os.getenv("DNP3_HOST", "0.0.0.0")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Performance
UPDATE_LATENCY_TARGET_MS = 100  # Target latency from MQTT to protocol update

# Agent IDs
AGENT_IDS = ["pm_agent", "energy_agent", "cyber_agent", "hazard_agent", "ppe_agent"]

# MQTT Topics
MQTT_PREDICTIONS_TOPIC = "predictions/#"
MQTT_CONFIG_TOPIC_PREFIX = "config/"

# Default Values for Missing Fields
DEFAULT_VALUES = {
    "float": 0.0,
    "int": 0,
    "string": "N/A",
    "bool": False
}
