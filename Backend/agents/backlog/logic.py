"""
Backlog Agent Logic Component
Decision rules engine for shift timing and data aggregation.
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger("BacklogAgent.Logic")


class BacklogLogic:
    """
    Backlog Generation Logic Component.
    
    Handles shift timing (8-hour shifts), data aggregation,
    and categorization of violations and anomalies.
    """
    
    def __init__(self, shift_duration_hours: int = 8):
        """
        Initialize logic component.
        
        Args:
            shift_duration_hours: Duration of each shift in hours (default: 8)
        """
        self.shift_duration_hours = shift_duration_hours
        self.shift_duration_seconds = shift_duration_hours * 3600
        
        logger.info(f"Initialized Backlog Logic (shift_duration={shift_duration_hours} hours)")
    
    def is_shift_complete(self, shift_start: datetime, current_time: datetime) -> bool:
        """
        Check if current shift is complete.
        
        Args:
            shift_start: Shift start timestamp
            current_time: Current timestamp
        
        Returns:
            True if shift duration has elapsed
        """
        elapsed = (current_time - shift_start).total_seconds()
        return elapsed >= self.shift_duration_seconds
    
    def get_next_shift_start(self, current_time: datetime) -> datetime:
        """
        Calculate next shift start time.
        
        Args:
            current_time: Current timestamp
        
        Returns:
            Next shift start timestamp (aligned to shift boundaries)
        """
        # Align to shift boundaries (e.g., shifts start at 00:00, 08:00, 16:00)
        hours_per_day = 24
        shifts_per_day = hours_per_day // self.shift_duration_hours
        
        current_hour = current_time.hour
        current_shift = current_hour // self.shift_duration_hours
        
        # Next shift starts at the next shift boundary
        next_shift = (current_shift + 1) % shifts_per_day
        next_shift_hour = next_shift * self.shift_duration_hours
        
        # Calculate next shift start
        next_start = current_time.replace(hour=next_shift_hour, minute=0, second=0, microsecond=0)
        
        # If next shift is tomorrow
        if next_shift_hour <= current_hour:
            next_start += timedelta(days=1)
        
        return next_start
    
    def aggregate_shift_data(self, events: List[Dict[str, Any]], 
                            shift_start: datetime, shift_end: datetime) -> Dict[str, Any]:
        """
        Aggregate events into shift data structure.
        
        Args:
            events: List of all events (violations and anomalies) from the shift
            shift_start: Shift start timestamp
            shift_end: Shift end timestamp
        
        Returns:
            Aggregated shift data dictionary
        """
        # Separate violations and anomalies
        violations = []
        anomalies = []
        
        for event in events:
            alert_level = event.get('alert_level', 'NORMAL')
            agent_id = event.get('agent_id', 'unknown')
            
            # Determine if it's a violation or anomaly based on agent type
            if agent_id in ['ppe_agent', 'hazard_agent']:
                # These are violations
                violations.append(event)
            elif agent_id in ['cyber_agent', 'energy_agent']:
                # These are anomalies
                anomalies.append(event)
            elif agent_id == 'pm_agent':
                # PM agent can have both - check alert level
                if alert_level in ['CRITICAL', 'EMERGENCY']:
                    violations.append(event)
                else:
                    anomalies.append(event)
            else:
                # Default: treat as anomaly
                anomalies.append(event)
        
        # Calculate summary statistics
        summary_stats = self._calculate_statistics(violations, anomalies, shift_start, shift_end)
        
        return {
            "shift_start": shift_start.isoformat(),
            "shift_end": shift_end.isoformat(),
            "violations": violations,
            "anomalies": anomalies,
            "summary_stats": summary_stats
        }
    
    def _calculate_statistics(self, violations: List[Dict[str, Any]], 
                             anomalies: List[Dict[str, Any]],
                             shift_start: datetime, shift_end: datetime) -> Dict[str, Any]:
        """Calculate summary statistics for the shift."""
        # Count by severity
        violation_counts = {
            "CRITICAL": len([v for v in violations if v.get('alert_level') == 'CRITICAL']),
            "EMERGENCY": len([v for v in violations if v.get('alert_level') == 'EMERGENCY']),
            "WARNING": len([v for v in violations if v.get('alert_level') == 'WARNING']),
            "CAUTION": len([v for v in violations if v.get('alert_level') == 'CAUTION'])
        }
        
        anomaly_counts = {
            "CRITICAL": len([a for a in anomalies if a.get('alert_level') == 'CRITICAL']),
            "EMERGENCY": len([a for a in anomalies if a.get('alert_level') == 'EMERGENCY']),
            "WARNING": len([a for a in anomalies if a.get('alert_level') == 'WARNING']),
            "CAUTION": len([a for a in anomalies if a.get('alert_level') == 'CAUTION'])
        }
        
        # Count by agent
        agent_counts = {}
        for event in violations + anomalies:
            agent_id = event.get('agent_id', 'unknown')
            agent_counts[agent_id] = agent_counts.get(agent_id, 0) + 1
        
        # Calculate shift duration
        shift_duration_hours = (shift_end - shift_start).total_seconds() / 3600
        
        return {
            "total_violations": len(violations),
            "total_anomalies": len(anomalies),
            "violation_counts": violation_counts,
            "anomaly_counts": anomaly_counts,
            "agent_counts": agent_counts,
            "shift_duration_hours": round(shift_duration_hours, 2),
            "events_per_hour": round((len(violations) + len(anomalies)) / shift_duration_hours, 2) if shift_duration_hours > 0 else 0
        }
    
    def apply_logic(self, shift_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply business rules to shift data.
        
        Args:
            shift_data: Aggregated shift data
        
        Returns:
            Logic output with categorization and priorities
        """
        violations = shift_data.get('violations', [])
        anomalies = shift_data.get('anomalies', [])
        stats = shift_data.get('summary_stats', {})
        
        # Determine overall shift status
        critical_count = stats.get('violation_counts', {}).get('CRITICAL', 0) + \
                        stats.get('violation_counts', {}).get('EMERGENCY', 0) + \
                        stats.get('anomaly_counts', {}).get('CRITICAL', 0) + \
                        stats.get('anomaly_counts', {}).get('EMERGENCY', 0)
        
        if critical_count > 0:
            shift_status = "CRITICAL"
            priority = 1
        elif len(violations) + len(anomalies) > 20:
            shift_status = "WARNING"
            priority = 2
        elif len(violations) + len(anomalies) > 10:
            shift_status = "CAUTION"
            priority = 3
        else:
            shift_status = "NORMAL"
            priority = 4
        
        return {
            "shift_status": shift_status,
            "priority": priority,
            "requires_attention": critical_count > 0 or len(violations) > 5,
            "total_events": len(violations) + len(anomalies),
            "critical_events": critical_count
        }

