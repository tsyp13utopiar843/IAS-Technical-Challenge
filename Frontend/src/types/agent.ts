// Agent and System Types for Backend Integration

export interface Alert {
    level: "critical" | "warning" | "normal" | "info";
    type: string;
    source: string;
    details: string;
    timestamp?: string;
}

export interface Decision {
    timestamp: string;
    alert: Alert;
    plan: {
        action: string;
        steps?: string[];
        priority?: string;
    };
}

export interface SystemState {
    alerts: Alert[];
    decisions: Decision[];
    last_update: string;
}

// Generic Agent Status
export interface AgentStatus {
    status: string;
    agent_id: string;
    timestamp?: string;
    prediction_history?: any[];
    last_prediction?: any;
    metrics?: Record<string, any>;
}

// Predictive Maintenance Agent
export interface PMPrediction {
    rul_hours?: number;
    health_score?: number;
    failure_probability?: number;
    confidence?: number;
    alert_level?: string;
    action?: string;
    recommended_action?: string;
    timestamp?: string;
}

export interface PMStatus extends AgentStatus {
    last_prediction?: PMPrediction;
    prediction_history?: PMPrediction[];
}

// Energy Agent
export interface EnergyPrediction {
    consumption_kwh?: number;
    efficiency_score?: number;
    anomaly_detected?: boolean;
    alert_level?: string;
    action?: string;
    recommended_action?: string;
    timestamp?: string;
}

export interface EnergyStatus extends AgentStatus {
    last_prediction?: EnergyPrediction;
    prediction_history?: EnergyPrediction[];
}

// Cyber Security Agent
export interface CyberPrediction {
    threat_level?: string;
    threat_type?: string;
    confidence?: number;
    alert_level?: string;
    action?: string;
    recommended_action?: string;
    timestamp?: string;
}

export interface CyberStatus extends AgentStatus {
    last_prediction?: CyberPrediction;
    prediction_history?: CyberPrediction[];
}

// Safety Agent
export interface SafetyPrediction {
    hazard_detected?: boolean;
    hazard_type?: string;
    risk_level?: string;
    alert_level?: string;
    action?: string;
    recommended_action?: string;
    timestamp?: string;
}

export interface SafetyStatus extends AgentStatus {
    last_prediction?: SafetyPrediction;
    prediction_history?: SafetyPrediction[];
}

// PPE Agent
export interface PPEPrediction {
    compliance?: boolean;
    missing_equipment?: string[];
    confidence?: number;
    alert_level?: string;
    action?: string;
    recommended_action?: string;
    timestamp?: string;
}

export interface PPEStatus extends AgentStatus {
    last_prediction?: PPEPrediction;
    prediction_history?: PPEPrediction[];
}

// History Response
export interface HistoryResponse {
    history: any[];
}
