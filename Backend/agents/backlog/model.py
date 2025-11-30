"""
Backlog Agent Model Component
Handles GEMINI API integration via LangChain for generating shift backlogs.
"""
import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain.prompts import ChatPromptTemplate
    from langchain.schema import HumanMessage, SystemMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logging.warning("LangChain not available. Install with: pip install langchain langchain-google-genai")

logger = logging.getLogger("BacklogAgent.Model")


class BacklogModel:
    """
    Backlog Generation Model Component.
    
    Uses GEMINI API via LangChain to generate structured shift backlogs
    from violations and anomalies collected during the shift.
    """
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-pro"):
        """
        Initialize model component.
        
        Args:
            api_key: GEMINI API key (or from GEMINI_API_KEY env var)
            model_name: GEMINI model name to use
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.model_name = model_name
        self.llm = None
        
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not set. Backlog generation will use mock responses.")
        elif LANGCHAIN_AVAILABLE:
            try:
                self.llm = ChatGoogleGenerativeAI(
                    model=model_name,
                    google_api_key=self.api_key,
                    temperature=0.3  # Lower temperature for more consistent, structured output
                )
                logger.info(f"Initialized GEMINI model: {model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize GEMINI model: {e}", exc_info=True)
                self.llm = None
        else:
            logger.warning("LangChain not available. Install required packages.")
        
        logger.info(f"Initialized Backlog Model (model={model_name}, llm_available={self.llm is not None})")
    
    def generate_backlog(self, shift_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate shift backlog using GEMINI API.
        
        Args:
            shift_data: Dictionary containing:
                - shift_start: Shift start timestamp
                - shift_end: Shift end timestamp
                - violations: List of violations from all agents
                - anomalies: List of anomalies from all agents
                - summary_stats: Summary statistics
        
        Returns:
            Dictionary with generated backlog:
            - backlog_id: Unique backlog identifier
            - shift_period: Shift time period
            - summary: Executive summary
            - violations: Categorized violations
            - anomalies: Categorized anomalies
            - recommendations: AI-generated recommendations
            - priority_items: High-priority items requiring attention
            - generated_at: Generation timestamp
        """
        try:
            if self.llm is None:
                return self._mock_generate_backlog(shift_data)
            
            # Build prompt for GEMINI
            prompt = self._build_prompt(shift_data)
            
            # Generate backlog using LangChain
            response = self.llm.invoke(prompt)
            
            # Parse response
            backlog = self._parse_response(response, shift_data)
            
            logger.info("Backlog generated successfully using GEMINI")
            return backlog
            
        except Exception as e:
            logger.error(f"Error generating backlog: {e}", exc_info=True)
            return self._mock_generate_backlog(shift_data)
    
    def _build_prompt(self, shift_data: Dict[str, Any]) -> str:
        """Build prompt for GEMINI API."""
        shift_start = shift_data.get('shift_start', '')
        shift_end = shift_data.get('shift_end', '')
        violations = shift_data.get('violations', [])
        anomalies = shift_data.get('anomalies', [])
        summary_stats = shift_data.get('summary_stats', {})
        
        prompt = f"""You are an AI assistant that creates comprehensive shift backlogs for industrial operations.

SHIFT PERIOD: {shift_start} to {shift_end}

SUMMARY STATISTICS:
{json.dumps(summary_stats, indent=2)}

VIOLATIONS DETECTED ({len(violations)} total):
"""
        for i, violation in enumerate(violations[:50], 1):  # Limit to 50 for token efficiency
            prompt += f"\n{i}. [{violation.get('agent_id', 'unknown')}] {violation.get('alert_level', 'UNKNOWN')} - {violation.get('message', 'No message')}\n"
            prompt += f"   Timestamp: {violation.get('timestamp', 'unknown')}\n"
            if violation.get('data'):
                prompt += f"   Details: {json.dumps(violation.get('data', {}), indent=6)}\n"
        
        prompt += f"\n\nANOMALIES DETECTED ({len(anomalies)} total):\n"
        for i, anomaly in enumerate(anomalies[:50], 1):
            prompt += f"\n{i}. [{anomaly.get('agent_id', 'unknown')}] {anomaly.get('alert_level', 'UNKNOWN')} - {anomaly.get('message', 'No message')}\n"
            prompt += f"   Timestamp: {anomaly.get('timestamp', 'unknown')}\n"
            if anomaly.get('data'):
                prompt += f"   Details: {json.dumps(anomaly.get('data', {}), indent=6)}\n"
        
        prompt += """
TASK: Generate a comprehensive shift backlog in JSON format with the following structure:
{
  "summary": "Executive summary of the shift (2-3 sentences)",
  "violations": {
    "critical": [list of critical violations with details],
    "warning": [list of warning violations with details],
    "caution": [list of caution violations with details]
  },
  "anomalies": {
    "critical": [list of critical anomalies with details],
    "warning": [list of warning anomalies with details],
    "caution": [list of caution anomalies with details]
  },
  "recommendations": [
    "Action item 1",
    "Action item 2",
    ...
  ],
  "priority_items": [
    {
      "priority": "HIGH/MEDIUM/LOW",
      "item": "Description of priority item",
      "agent": "agent_id",
      "action_required": "What needs to be done"
    },
    ...
  ],
  "trends": "Analysis of trends and patterns observed during the shift"
}

IMPORTANT: 
- Return ONLY valid JSON, no markdown formatting
- Categorize violations and anomalies by severity (critical, warning, caution)
- Provide actionable recommendations
- Identify priority items that require immediate attention
- Analyze trends and patterns
"""
        
        return prompt
    
    def _parse_response(self, response: Any, shift_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse GEMINI response into backlog structure."""
        try:
            # Extract content from LangChain response
            if hasattr(response, 'content'):
                content = response.content
            elif isinstance(response, str):
                content = response
            else:
                content = str(response)
            
            # Try to extract JSON from response
            # Remove markdown code blocks if present
            content = content.strip()
            if content.startswith('```json'):
                content = content[7:]
            if content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            # Parse JSON
            backlog_data = json.loads(content)
            
            # Build complete backlog
            backlog = {
                "backlog_id": f"backlog_{shift_data.get('shift_start', datetime.utcnow().isoformat()).replace(':', '-').replace(' ', '_')}",
                "shift_period": {
                    "start": shift_data.get('shift_start'),
                    "end": shift_data.get('shift_end')
                },
                "summary": backlog_data.get('summary', 'No summary generated'),
                "violations": backlog_data.get('violations', {}),
                "anomalies": backlog_data.get('anomalies', {}),
                "recommendations": backlog_data.get('recommendations', []),
                "priority_items": backlog_data.get('priority_items', []),
                "trends": backlog_data.get('trends', 'No trend analysis available'),
                "statistics": shift_data.get('summary_stats', {}),
                "generated_at": datetime.utcnow().isoformat(),
                "total_violations": len(shift_data.get('violations', [])),
                "total_anomalies": len(shift_data.get('anomalies', []))
            }
            
            return backlog
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Response content: {content[:500]}")
            return self._mock_generate_backlog(shift_data)
        except Exception as e:
            logger.error(f"Error parsing response: {e}", exc_info=True)
            return self._mock_generate_backlog(shift_data)
    
    def _mock_generate_backlog(self, shift_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate mock backlog when GEMINI is not available."""
        violations = shift_data.get('violations', [])
        anomalies = shift_data.get('anomalies', [])
        
        # Categorize violations
        violations_by_severity = {
            "critical": [v for v in violations if v.get('alert_level') in ['CRITICAL', 'EMERGENCY']],
            "warning": [v for v in violations if v.get('alert_level') == 'WARNING'],
            "caution": [v for v in violations if v.get('alert_level') == 'CAUTION']
        }
        
        # Categorize anomalies
        anomalies_by_severity = {
            "critical": [a for a in anomalies if a.get('alert_level') in ['CRITICAL', 'EMERGENCY']],
            "warning": [a for a in anomalies if a.get('alert_level') == 'WARNING'],
            "caution": [a for a in anomalies if a.get('alert_level') == 'CAUTION']
        }
        
        # Generate simple recommendations
        recommendations = []
        if violations_by_severity['critical']:
            recommendations.append("Address critical violations immediately")
        if anomalies_by_severity['critical']:
            recommendations.append("Investigate critical anomalies")
        if len(violations) > 10:
            recommendations.append("Review operational procedures to reduce violation frequency")
        
        backlog = {
            "backlog_id": f"backlog_{shift_data.get('shift_start', datetime.utcnow().isoformat()).replace(':', '-').replace(' ', '_')}",
            "shift_period": {
                "start": shift_data.get('shift_start'),
                "end": shift_data.get('shift_end')
            },
            "summary": f"Shift completed with {len(violations)} violations and {len(anomalies)} anomalies detected across all monitoring agents.",
            "violations": violations_by_severity,
            "anomalies": anomalies_by_severity,
            "recommendations": recommendations,
            "priority_items": [
                {
                    "priority": "HIGH",
                    "item": f"Review {len(violations_by_severity['critical'])} critical violations",
                    "agent": "multiple",
                    "action_required": "Immediate attention required"
                }
            ] if violations_by_severity['critical'] else [],
            "trends": f"Total of {len(violations)} violations and {len(anomalies)} anomalies detected during this shift.",
            "statistics": shift_data.get('summary_stats', {}),
            "generated_at": datetime.utcnow().isoformat(),
            "total_violations": len(violations),
            "total_anomalies": len(anomalies)
        }
        
        logger.info("Generated mock backlog (GEMINI not available)")
        return backlog

