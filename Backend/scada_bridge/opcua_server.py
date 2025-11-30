"""
OPC UA Server Module
Exposes AI agent predictions via hierarchical OPC UA namespace.
Supports read-only prediction nodes and read/write configuration nodes.
"""
import logging
import asyncio
from typing import Dict, Any, Optional
from asyncua import Server, ua
from asyncua.common.methods import uamethod

import config
from data_transformer import DataTransformer

logger = logging.getLogger(__name__)


class OPCUABridgeServer:
    """OPC UA server for SCADA Bridge."""
    
    def __init__(self, mqtt_client=None):
        self.server = Server()
        self.mqtt_client = mqtt_client
        self.transformer = DataTransformer()
        
        # Node references (populated during setup)
        self.nodes = {}
        self.namespace_idx = None
        
    async def init(self):
        """Initialize OPC UA server."""
        await self.server.init()
        self.server.set_endpoint(config.OPCUA_ENDPOINT)
        self.server.set_server_name(config.OPCUA_SERVER_NAME)
        
        # Security settings
        if config.OPCUA_ALLOW_ANONYMOUS:
            self.server.set_security_policy([ua.SecurityPolicyType.NoSecurity])
        
        # Register namespace
        self.namespace_idx = await self.server.register_namespace(config.OPCUA_NAMESPACE)
        
        logger.info(f"OPC UA server initialized with namespace index: {self.namespace_idx}")
        
        # Create node structure
        await self._create_node_structure()
    
    async def _create_node_structure(self):
        """Create hierarchical OPC UA node structure."""
        # Get objects node
        objects = self.server.get_objects_node()
        
        # Root folder
        root = await objects.add_folder(self.namespace_idx, "MultiAgentSystem")
        logger.info("Created root folder: MultiAgentSystem")
        
        # System Status folder
        await self._create_system_status_nodes(root)
        
        # Predictive Maintenance folder
        await self._create_pm_nodes(root)
        
        # Energy Optimization folder
        await self._create_energy_nodes(root)
        
        # Cyber Security folder
        await self._create_cyber_nodes(root)
        
        # Workplace Safety folder
        await self._create_safety_nodes(root)
        
        # PPE Compliance folder
        await self._create_ppe_nodes(root)
        
        logger.info("OPC UA node structure created successfully")
    
    async def _create_system_status_nodes(self, parent):
        """Create System Status nodes."""
        folder = await parent.add_folder(self.namespace_idx, "SystemStatus")
        
        self.nodes["SystemStatus.OverallHealth"] = await folder.add_variable(
            self.namespace_idx, "OverallHealth", 100.0, ua.VariantType.Float
        )
        self.nodes["SystemStatus.ActiveAgents"] = await folder.add_variable(
            self.namespace_idx, "ActiveAgents", 0, ua.VariantType.Int32
        )
        self.nodes["SystemStatus.TotalAlerts"] = await folder.add_variable(
            self.namespace_idx, "TotalAlerts", 0, ua.VariantType.Int32
        )
        
        # Make read-only
        for node in [self.nodes["SystemStatus.OverallHealth"], 
                     self.nodes["SystemStatus.ActiveAgents"],
                     self.nodes["SystemStatus.TotalAlerts"]]:
            await node.set_writable(False)
    
    async def _create_pm_nodes(self, parent):
        """Create Predictive Maintenance nodes."""
        folder = await parent.add_folder(self.namespace_idx, "PredictiveMaintenance")
        
        # Read-only prediction nodes
        self.nodes["PM.RemainingUsefulLife"] = await folder.add_variable(
            self.namespace_idx, "RemainingUsefulLife", 0.0, ua.VariantType.Float
        )
        self.nodes["PM.HealthScore"] = await folder.add_variable(
            self.namespace_idx, "HealthScore", 0.0, ua.VariantType.Float
        )
        self.nodes["PM.AlertLevel"] = await folder.add_variable(
            self.namespace_idx, "AlertLevel", "normal", ua.VariantType.String
        )
        self.nodes["PM.FailureProbability"] = await folder.add_variable(
            self.namespace_idx, "FailureProbability", 0.0, ua.VariantType.Float
        )
        self.nodes["PM.RecommendedAction"] = await folder.add_variable(
            self.namespace_idx, "RecommendedAction", "No action required", ua.VariantType.String
        )
        
        # Read/Write configuration nodes
        self.nodes["PM.ThresholdCritical"] = await folder.add_variable(
            self.namespace_idx, "ThresholdCritical", 20.0, ua.VariantType.Float
        )
        self.nodes["PM.ThresholdWarning"] = await folder.add_variable(
            self.namespace_idx, "ThresholdWarning", 50.0, ua.VariantType.Float
        )
        
        # Set read-only on prediction nodes
        for key in ["PM.RemainingUsefulLife", "PM.HealthScore", "PM.AlertLevel", 
                    "PM.FailureProbability", "PM.RecommendedAction"]:
            await self.nodes[key].set_writable(False)
        
        # Set writable on config nodes
        await self.nodes["PM.ThresholdCritical"].set_writable(True)
        await self.nodes["PM.ThresholdWarning"].set_writable(True)
        
        logger.info("Created Predictive Maintenance nodes")
    
    async def _create_energy_nodes(self, parent):
        """Create Energy Optimization nodes."""
        folder = await parent.add_folder(self.namespace_idx, "EnergyOptimization")
        
        self.nodes["Energy.ConsumptionKWh"] = await folder.add_variable(
            self.namespace_idx, "ConsumptionKWh", 0.0, ua.VariantType.Float
        )
        self.nodes["Energy.EfficiencyScore"] = await folder.add_variable(
            self.namespace_idx, "EfficiencyScore", 0.0, ua.VariantType.Float
        )
        self.nodes["Energy.PredictedConsumption"] = await folder.add_variable(
            self.namespace_idx, "PredictedConsumption", 0.0, ua.VariantType.Float
        )
        self.nodes["Energy.IsAnomaly"] = await folder.add_variable(
            self.namespace_idx, "IsAnomaly", False, ua.VariantType.Boolean
        )
        self.nodes["Energy.AnomalyScore"] = await folder.add_variable(
            self.namespace_idx, "AnomalyScore", 0.0, ua.VariantType.Float
        )
        
        for key in self.nodes:
            if key.startswith("Energy."):
                await self.nodes[key].set_writable(False)
        
        logger.info("Created Energy Optimization nodes")
    
    async def _create_cyber_nodes(self, parent):
        """Create Cyber Security nodes."""
        folder = await parent.add_folder(self.namespace_idx, "CyberSecurity")
        
        self.nodes["Cyber.ThreatLevel"] = await folder.add_variable(
            self.namespace_idx, "ThreatLevel", "low", ua.VariantType.String
        )
        self.nodes["Cyber.AnomalyScore"] = await folder.add_variable(
            self.namespace_idx, "AnomalyScore", 0.0, ua.VariantType.Float
        )
        self.nodes["Cyber.ActiveThreats"] = await folder.add_variable(
            self.namespace_idx, "ActiveThreats", 0, ua.VariantType.Int32
        )
        self.nodes["Cyber.NetworkHealth"] = await folder.add_variable(
            self.namespace_idx, "NetworkHealth", 100.0, ua.VariantType.Float
        )
        
        for key in self.nodes:
            if key.startswith("Cyber."):
                await self.nodes[key].set_writable(False)
        
        logger.info("Created Cyber Security nodes")
    
    async def _create_safety_nodes(self, parent):
        """Create Workplace Safety nodes."""
        folder = await parent.add_folder(self.namespace_idx, "WorkplaceSafety")
        
        self.nodes["Safety.RiskLevel"] = await folder.add_variable(
            self.namespace_idx, "RiskLevel", "low", ua.VariantType.String
        )
        self.nodes["Safety.HazardCount"] = await folder.add_variable(
            self.namespace_idx, "HazardCount", 0, ua.VariantType.Int32
        )
        self.nodes["Safety.SafetyScore"] = await folder.add_variable(
            self.namespace_idx, "SafetyScore", 100.0, ua.VariantType.Float
        )
        self.nodes["Safety.ActiveWarnings"] = await folder.add_variable(
            self.namespace_idx, "ActiveWarnings", 0, ua.VariantType.Int32
        )
        
        for key in self.nodes:
            if key.startswith("Safety."):
                await self.nodes[key].set_writable(False)
        
        logger.info("Created Workplace Safety nodes")
    
    async def _create_ppe_nodes(self, parent):
        """Create PPE Compliance nodes."""
        folder = await parent.add_folder(self.namespace_idx, "PPECompliance")
        
        self.nodes["PPE.ComplianceRate"] = await folder.add_variable(
            self.namespace_idx, "ComplianceRate", 100.0, ua.VariantType.Float
        )
        self.nodes["PPE.ViolationsCount"] = await folder.add_variable(
            self.namespace_idx, "ViolationsCount", 0, ua.VariantType.Int32
        )
        self.nodes["PPE.WorkersMonitored"] = await folder.add_variable(
            self.namespace_idx, "WorkersMonitored", 0, ua.VariantType.Int32
        )
        self.nodes["PPE.HelmetCompliance"] = await folder.add_variable(
            self.namespace_idx, "HelmetCompliance", 100.0, ua.VariantType.Float
        )
        self.nodes["PPE.VestCompliance"] = await folder.add_variable(
            self.namespace_idx, "VestCompliance", 100.0, ua.VariantType.Float
        )
        
        for key in self.nodes:
            if key.startswith("PPE."):
                await self.nodes[key].set_writable(False)
        
        logger.info("Created PPE Compliance nodes")
    
    async def update_from_mqtt(self, agent_id: str, prediction_data: Dict[str, Any]):
        """
        Update OPC UA nodes from MQTT prediction.
        Called by MQTT client callback.
        """
        try:
            # Transform to OPC UA format
            opcua_values = self.transformer.to_opcua(agent_id, prediction_data)
            
            # Map agent_id to node prefix
            prefix_map = {
                "pm_agent": "PM",
                "energy_agent": "Energy",
                "cyber_agent": "Cyber",
                "hazard_agent": "Safety",
                "ppe_agent": "PPE"
            }
            
            prefix = prefix_map.get(agent_id)
            if not prefix:
                logger.warning(f"Unknown agent_id: {agent_id}")
                return
            
            # Update nodes
            for node_name, value in opcua_values.items():
                full_key = f"{prefix}.{node_name}"
                if full_key in self.nodes:
                    await self.nodes[full_key].write_value(value)
                    logger.debug(f"Updated {full_key} = {value}")
            
            # Update system status
            await self._update_system_status()
            
        except Exception as e:
            logger.error(f"Error updating OPC UA nodes from {agent_id}: {e}", exc_info=True)
    
    async def _update_system_status(self):
        """Update system-level status nodes."""
        # Count active agents (simplified - just set to 5)
        await self.nodes["SystemStatus.ActiveAgents"].write_value(5)
        
        # Calculate overall health (average of available health scores)
        health_scores = []
        if "PM.HealthScore" in self.nodes:
            pm_health = await self.nodes["PM.HealthScore"].read_value()
            health_scores.append(pm_health)
        if "Safety.SafetyScore" in self.nodes:
            safety_score = await self.nodes["Safety.SafetyScore"].read_value()
            health_scores.append(safety_score)
        
        if health_scores:
            overall_health = sum(health_scores) / len(health_scores)
            await self.nodes["SystemStatus.OverallHealth"].write_value(overall_health)
    
    async def start(self):
        """Start OPC UA server."""
        async with self.server:
            logger.info(f"OPC UA Server started at {config.OPCUA_ENDPOINT}")
            
            # Keep running
            while True:
                await asyncio.sleep(1)
    
    async def stop(self):
        """Stop OPC UA server."""
        logger.info("Stopping OPC UA server...")
        await self.server.stop()
        logger.info("OPC UA server stopped")
