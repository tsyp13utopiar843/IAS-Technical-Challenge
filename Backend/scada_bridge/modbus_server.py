"""
Modbus TCP Server Module
Exposes AI agent predictions via Modbus holding registers.
Maps float values to Int16 with scaling and enum conversions.
"""
import logging
import threading
from typing import Dict, Any
from pymodbus.server import StartTcpServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.transaction import ModbusSocketFramer

import config
from data_transformer import DataTransformer

logger = logging.getLogger(__name__)


class ModbusBridgeServer:
    """Modbus TCP server for SCADA Bridge."""
    
    def __init__(self):
        self.transformer = DataTransformer()
        self.server_thread = None
        self.running = False
        
        # Initialize datastore with 1000 registers (all zeros)
        # Register types: hr = holding registers
        self.datablock = ModbusSequentialDataBlock(0, [0] * 1000)
        
        # Create slave context
        self.slave_context = ModbusSlaveContext(
            di=None,  # Discrete inputs
            co=None,  # Coils
            hr=self.datablock,  # Holding registers
            ir=None   # Input registers
        )
        
        # Create server context with single slave
        self.context = ModbusServerContext(
            slaves={config.MODBUS_UNIT_ID: self.slave_context},
            single=True
        )
        
        # Device identification
        self.identity = ModbusDeviceIdentification()
        self.identity.VendorName = '6G-MAS-Factory'
        self.identity.ProductCode = 'SCADA-BRIDGE'
        self.identity.VendorUrl = 'http://6g-mas-factory.com'
        self.identity.ProductName = 'Multi-Agent SCADA Bridge'
        self.identity.ModelName = 'Modbus TCP Server'
        self.identity.MajorMinorRevision = '1.0.0'
    
    def update_from_mqtt(self, agent_id: str, prediction_data: Dict[str, Any]):
        """
        Update Modbus registers from MQTT prediction.
        Called by MQTT client callback.
        Thread-safe operation.
        """
        try:
            # Transform to Modbus format
            modbus_values = self.transformer.to_modbus(agent_id, prediction_data)
            
            # Update registers atomically
            for address, value in modbus_values.items():
                # Ensure value fits in Int16 range (-32768 to 32767)
                if value > 32767:
                    value = 32767
                    logger.warning(f"Register {address} value clamped to 32767")
                elif value < -32768:
                    value = -32768
                    logger.warning(f"Register {address} value clamped to -32768")
                
                self.datablock.setValues(address, [value])
                logger.debug(f"Updated register {address} = {value}")
            
            # Update system status registers
            self._update_system_status()
            
        except Exception as e:
            logger.error(f"Error updating Modbus registers from {agent_id}: {e}", exc_info=True)
    
    def _update_system_status(self):
        """Update system-level status registers (500-599)."""
        try:
            # Register 500: Overall Health (simplified - average of PM and Safety health)
            pm_health = self.datablock.getValues(1, 1)[0]  # PM HealthScore at register 1
            safety_score = self.datablock.getValues(302, 1)[0]  # Safety score at register 302
            
            if pm_health > 0 or safety_score > 0:
                overall_health = (pm_health + safety_score) // 2
                self.datablock.setValues(500, [overall_health])
            
            # Register 501: Active Agents (hardcoded to 5 for now)
            self.datablock.setValues(501, [5])
            
            # Register 503: System Status (0=operational, 1=degraded, 2=error)
            # Simple logic: if overall health < 50, degraded; if < 25, error
            overall_health = self.datablock.getValues(500, 1)[0]
            if overall_health >= 50:
                system_status = 0  # Operational
            elif overall_health >= 25:
                system_status = 1  # Degraded
            else:
                system_status = 2  # Error
            
            self.datablock.setValues(503, [system_status])
            
        except Exception as e:
            logger.error(f"Error updating system status registers: {e}")
    
    def start(self):
        """Start Modbus TCP server in background thread."""
        def run_server():
            try:
                logger.info(f"Starting Modbus TCP server on {config.MODBUS_HOST}:{config.MODBUS_PORT}")
                self.running = True
                
                # Start server (blocking call)
                StartTcpServer(
                    context=self.context,
                    identity=self.identity,
                    address=(config.MODBUS_HOST, config.MODBUS_PORT),
                    framer=ModbusSocketFramer
                )
            except Exception as e:
                logger.error(f"Modbus server error: {e}", exc_info=True)
                self.running = False
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        logger.info("Modbus TCP server thread started")
    
    def stop(self):
        """Stop Modbus TCP server."""
        logger.info("Stopping Modbus TCP server...")
        self.running = False
        # Note: pymodbus doesn't have a clean shutdown method for sync server
        # The daemon thread will terminate when main process exits
        logger.info("Modbus TCP server stopped")
