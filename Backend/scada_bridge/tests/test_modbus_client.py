"""
Modbus Client Test
Connects to the SCADA bridge Modbus TCP server and reads registers.
"""
import sys
import os
from pymodbus.client import ModbusTcpClient

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config as bridge_config


def test_modbus_client():
    """Test Modbus TCP client connection and register reading."""
    print("="*60)
    print("Modbus TCP Client Test")
    print("="*60)
    print(f"Connecting to: {bridge_config.MODBUS_HOST}:{bridge_config.MODBUS_PORT}")
    
    client = ModbusTcpClient(
        host=bridge_config.MODBUS_HOST,
        port=bridge_config.MODBUS_PORT
    )
    
    try:
        if client.connect():
            print("✓ Connected successfully\n")
            
            # Read Predictive Maintenance registers (0-10)
            print("Predictive Maintenance (Registers 0-10):")
            print("-" * 40)
            
            result = client.read_holding_registers(address=0, count=10, unit=bridge_config.MODBUS_UNIT_ID)
            
            if not result.isError():
                print(f"  Reg 0 (RUL hours): {result.registers[0]}")
                print(f"  Reg 1 (Health Score): {result.registers[1]}")
                print(f"  Reg 2 (Alert Level): {result.registers[2]} (0=normal, 1=warning, 2=critical)")
                print(f"  Reg 3 (Failure Prob %): {result.registers[3]}")
            else:
                print(f"  Error reading registers: {result}")
            
            print()
            
            # Read Energy Optimization registers (100-105)
            print("Energy Optimization (Registers 100-105):")
            print("-" * 40)
            
            result = client.read_holding_registers(address=100, count=5, unit=bridge_config.MODBUS_UNIT_ID)
            
            if not result.isError():
                print(f"  Reg 100 (Consumption kWh*10): {result.registers[0]}")
                print(f"  Reg 101 (Efficiency Score): {result.registers[1]}")
                print(f"  Reg 102 (Predicted kWh*10): {result.registers[2]}")
                print(f"  Reg 103 (Is Anomaly): {result.registers[3]} (0=false, 1=true)")
                print(f"  Reg 104 (Anomaly Score): {result.registers[4]}")
            else:
                print(f"  Error reading registers: {result}")
            
            print()
            
            # Read Cyber Security registers (200-204)
            print("Cyber Security (Registers 200-204):")
            print("-" * 40)
            
            result = client.read_holding_registers(address=200, count=4, unit=bridge_config.MODBUS_UNIT_ID)
            
            if not result.isError():
                print(f"  Reg 200 (Threat Level): {result.registers[0]} (0=low, 1=med, 2=high, 3=crit)")
                print(f"  Reg 201 (Anomaly Score): {result.registers[1]}")
                print(f"  Reg 202 (Active Threats): {result.registers[2]}")
                print(f"  Reg 203 (Network Health): {result.registers[3]}")
            else:
                print(f"  Error reading registers: {result}")
            
            print()
            
            # Read System Status registers (500-504)
            print("System Status (Registers 500-504):")
            print("-" * 40)
            
            result = client.read_holding_registers(address=500, count=4, unit=bridge_config.MODBUS_UNIT_ID)
            
            if not result.isError():
                print(f"  Reg 500 (Overall Health): {result.registers[0]}")
                print(f"  Reg 501 (Active Agents): {result.registers[1]}")
                print(f"  Reg 503 (System Status): {result.registers[3]} (0=ok, 1=degraded, 2=error)")
            else:
                print(f"  Error reading registers: {result}")
            
            print("\n✓ Test completed successfully")
        
        else:
            print("✗ Failed to connect")
    
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        client.close()
        print("\nDisconnected from Modbus server")


if __name__ == "__main__":
    test_modbus_client()
