"""
Main Entry Point for SCADA Bridge
Coordinates MQTT client and all protocol servers (OPC UA, Modbus, DNP3).
"""
import logging
import asyncio
import signal
import sys
from threading import Event

import config
from mqtt_client import MQTTBridgeClient
from opcua_server import OPCUABridgeServer
from modbus_server import ModbusBridgeServer
from dnp3_server import DNP3BridgeServer

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT
)

logger = logging.getLogger(__name__)

# Global shutdown event
shutdown_event = Event()


class SCADABridge:
    """Main SCADA Bridge coordinating all components."""
    
    def __init__(self):
        self.mqtt_client = None
        self.opcua_server = None
        self.modbus_server = None
        self.dnp3_server = None
        self.opcua_task = None
    
    async def initialize(self):
        """Initialize all servers and MQTT client."""
        logger.info("="*60)
        logger.info("6G-MAS-Factory SCADA Protocol Bridge")
        logger.info("="*60)
        
        # Initialize MQTT client
        self.mqtt_client = MQTTBridgeClient()
        
        # Initialize OPC UA server
        logger.info("Initializing OPC UA server...")
        self.opcua_server = OPCUABridgeServer(mqtt_client=self.mqtt_client)
        await self.opcua_server.init()
        
        # Initialize Modbus server
        logger.info("Initializing Modbus TCP server...")
        self.modbus_server = ModbusBridgeServer()
        
        # Initialize DNP3 server (optional)
        if config.DNP3_ENABLED:
            logger.info("Initializing DNP3 outstation...")
            self.dnp3_server = DNP3BridgeServer()
        else:
            logger.info("DNP3 server disabled")
            self.dnp3_server = None
        
        # Register MQTT callbacks
        self._register_mqtt_callbacks()
        
        logger.info("All servers initialized successfully")
    
    def _register_mqtt_callbacks(self):
        """Register callbacks to update protocol servers from MQTT."""
        
        def on_prediction(agent_id: str, prediction_data: dict):
            """Handle prediction from MQTT."""
            logger.info(f"Received prediction from {agent_id}")
            
            # Update OPC UA (async)
            if self.opcua_server:
                asyncio.create_task(
                    self.opcua_server.update_from_mqtt(agent_id, prediction_data)
                )
            
            # Update Modbus (sync)
            if self.modbus_server:
                self.modbus_server.update_from_mqtt(agent_id, prediction_data)
            
            # Update DNP3 (sync)
            if self.dnp3_server:
                self.dnp3_server.update_from_mqtt(agent_id, prediction_data)
        
        self.mqtt_client.add_message_callback(on_prediction)
        logger.info("MQTT callbacks registered")
    
    async def start(self):
        """Start all servers."""
        logger.info("Starting SCADA Bridge services...")
        
        # Start Modbus server (threaded)
        self.modbus_server.start()
        
        # Start DNP3 server (if enabled)
        if self.dnp3_server:
            self.dnp3_server.start()
        
        # Start MQTT client (threaded)
        self.mqtt_client.start()
        
        # Start OPC UA server (async - will block here)
        logger.info("Starting OPC UA server (async)...")
        self.opcua_task = asyncio.create_task(self.opcua_server.start())
        
        logger.info("="*60)
        logger.info("SCADA Bridge is now running")
        logger.info(f"  - OPC UA:     {config.OPCUA_ENDPOINT}")
        logger.info(f"  - Modbus TCP: {config.MODBUS_HOST}:{config.MODBUS_PORT}")
        if config.DNP3_ENABLED:
            logger.info(f"  - DNP3:       {config.DNP3_HOST}:{config.DNP3_PORT}")
        logger.info(f"  - MQTT:       {config.MQTT_BROKER}:{config.MQTT_PORT}")
        logger.info("="*60)
        
        # Wait for shutdown signal
        await self._wait_for_shutdown()
    
    async def _wait_for_shutdown(self):
        """Wait for shutdown event."""
        while not shutdown_event.is_set():
            await asyncio.sleep(1)
    
    async def shutdown(self):
        """Gracefully shutdown all servers."""
        logger.info("="*60)
        logger.info("Shutting down SCADA Bridge...")
        logger.info("="*60)
        
        # Stop MQTT client
        if self.mqtt_client:
            self.mqtt_client.stop()
        
        # Stop Modbus server
        if self.modbus_server:
            self.modbus_server.stop()
        
        # Stop DNP3 server
        if self.dnp3_server:
            self.dnp3_server.stop()
        
        # Stop OPC UA server
        if self.opcua_server:
            await self.opcua_server.stop()
        
        # Cancel OPC UA task
        if self.opcua_task:
            self.opcua_task.cancel()
            try:
                await self.opcua_task
            except asyncio.CancelledError:
                pass
        
        logger.info("SCADA Bridge shutdown complete")


def signal_handler(signum, frame):
    """Handle shutdown signals."""
    logger.info(f"Received signal {signum}, initiating shutdown...")
    shutdown_event.set()


async def main():
    """Main entry point."""
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    bridge = SCADABridge()
    
    try:
        await bridge.initialize()
        await bridge.start()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
    finally:
        await bridge.shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)
