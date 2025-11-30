"""
OPC UA Client Test
Connects to the SCADA bridge OPC UA server and reads node values.
"""
import sys
import os
import asyncio
from asyncua import Client

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config as bridge_config


async def test_opcua_client():
    """Test OPC UA client connection and node reading."""
    url = bridge_config.OPCUA_ENDPOINT
    
    print("="*60)
    print("OPC UA Client Test")
    print("="*60)
    print(f"Connecting to: {url}")
    
    client = Client(url=url)
    
    try:
        await client.connect()
        print("✓ Connected successfully\n")
        
        # Get namespace index
        nsidx = await client.get_namespace_index(bridge_config.OPCUA_NAMESPACE)
        print(f"Namespace index: {nsidx}\n")
        
        # Read Predictive Maintenance nodes
        print("Predictive Maintenance:")
        print("-" * 40)
        
        pm_nodes = {
            "RemainingUsefulLife": f"ns={nsidx};s=RemainingUsefulLife",
            "HealthScore": f"ns={nsidx};s=HealthScore",
            "AlertLevel": f"ns={nsidx};s=AlertLevel",
            "FailureProbability": f"ns={nsidx};s=FailureProbability",
            "RecommendedAction": f"ns={nsidx};s=RecommendedAction"
        }
        
        # Alternative: Browse from root
        root = client.get_objects_node()
        
        # Navigate to MultiAgentSystem/PredictiveMaintenance
        try:
            mas_node = await root.get_child([f"{nsidx}:MultiAgentSystem"])
            pm_folder = await mas_node.get_child([f"{nsidx}:PredictiveMaintenance"])
            
            # Read all children
            children = await pm_folder.get_children()
            
            for child in children:
                name = await child.read_browse_name()
                value = await child.read_value()
                print(f"  {name.Name}: {value}")
        
        except Exception as e:
            print(f"  Error browsing PM nodes: {e}")
        
        print()
        
        # Read Energy Optimization nodes
        print("Energy Optimization:")
        print("-" * 40)
        
        try:
            energy_folder = await mas_node.get_child([f"{nsidx}:EnergyOptimization"])
            children = await energy_folder.get_children()
            
            for child in children:
                name = await child.read_browse_name()
                value = await child.read_value()
                print(f"  {name.Name}: {value}")
        
        except Exception as e:
            print(f"  Error browsing Energy nodes: {e}")
        
        print()
        
        # Read System Status
        print("System Status:")
        print("-" * 40)
        
        try:
            status_folder = await mas_node.get_child([f"{nsidx}:SystemStatus"])
            children = await status_folder.get_children()
            
            for child in children:
                name = await child.read_browse_name()
                value = await child.read_value()
                print(f"  {name.Name}: {value}")
        
        except Exception as e:
            print(f"  Error browsing System Status nodes: {e}")
        
        print("\n✓ Test completed successfully")
    
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await client.disconnect()
        print("\nDisconnected from OPC UA server")


if __name__ == "__main__":
    asyncio.run(test_opcua_client())
