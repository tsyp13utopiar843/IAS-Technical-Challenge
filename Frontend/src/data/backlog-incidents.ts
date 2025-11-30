export interface Incident {
    id: string;
    type: "Machine" | "Worker";
    entityName: string;
    zone: string;
    description: string;
    detectedBy: string;
    detectionTime: string;
    status: "Critical" | "Pending" | "Resolved";
    severity: number; // 1-10 scale
    relatedData?: {
        machinePerformance?: number;
        temperature?: number;
        ppeCompliance?: string;
        confidence?: number;
    };
}

export const incidentsData: Incident[] = [
    {
        id: "INC-20251130-001",
        type: "Machine",
        entityName: "Hydraulic Press Beta",
        zone: "Zone A",
        description: "Critical temperature threshold exceeded - immediate shutdown required",
        detectedBy: "Temperature Monitoring AI",
        detectionTime: "2025-11-30 20:45",
        status: "Critical",
        severity: 9,
        relatedData: {
            machinePerformance: 52,
            temperature: 102,
        },
    },
    {
        id: "INC-20251130-002",
        type: "Worker",
        entityName: "Sarah Mitchell",
        zone: "Zone B",
        description: "PPE non-compliance detected - missing safety helmet",
        detectedBy: "PPE Detection AI",
        detectionTime: "2025-11-30 20:12",
        status: "Resolved",
        severity: 7,
        relatedData: {
            ppeCompliance: "Non-Compliant",
            confidence: 87,
        },
    },
    {
        id: "INC-20251130-003",
        type: "Machine",
        entityName: "CNC Mill Delta",
        zone: "Zone B",
        description: "Performance degradation detected - maintenance required",
        detectedBy: "Performance Analytics AI",
        detectionTime: "2025-11-30 19:50",
        status: "Critical",
        severity: 8,
        relatedData: {
            machinePerformance: 45,
            temperature: 95,
        },
    },
    {
        id: "INC-20251130-004",
        type: "Worker",
        entityName: "Michael Chen",
        zone: "Zone A",
        description: "PPE compliance warning - gloves not properly secured",
        detectedBy: "PPE Detection AI",
        detectionTime: "2025-11-30 19:30",
        status: "Pending",
        severity: 5,
        relatedData: {
            ppeCompliance: "Warning",
            confidence: 72,
        },
    },
    {
        id: "INC-20251130-005",
        type: "Machine",
        entityName: "Assembly Line 2",
        zone: "Zone D",
        description: "Unexpected slowdown in production line speed",
        detectedBy: "Production Monitoring AI",
        detectionTime: "2025-11-30 18:45",
        status: "Pending",
        severity: 6,
        relatedData: {
            machinePerformance: 88,
            temperature: 70,
        },
    },
    {
        id: "INC-20251130-006",
        type: "Worker",
        entityName: "Maria Garcia",
        zone: "Zone D",
        description: "PPE non-compliance - safety boots not detected",
        detectedBy: "PPE Detection AI",
        detectionTime: "2025-11-30 18:05",
        status: "Resolved",
        severity: 7,
        relatedData: {
            ppeCompliance: "Non-Compliant",
            confidence: 85,
        },
    },
    {
        id: "INC-20251130-007",
        type: "Machine",
        entityName: "Robotic Arm X1",
        zone: "Zone C",
        description: "Abnormal vibration pattern detected during operation",
        detectedBy: "Vibration Analysis AI",
        detectionTime: "2025-11-30 17:20",
        status: "Pending",
        severity: 6,
        relatedData: {
            machinePerformance: 78,
            temperature: 81,
        },
    },
    {
        id: "INC-20251130-008",
        type: "Machine",
        entityName: "Assembly Line 1",
        zone: "Zone C",
        description: "Emergency stop triggered - component jam detected",
        detectedBy: "Safety Monitoring AI",
        detectionTime: "2025-11-30 16:45",
        status: "Critical",
        severity: 9,
        relatedData: {
            machinePerformance: 38,
            temperature: 98,
        },
    },
    {
        id: "INC-20251130-009",
        type: "Worker",
        entityName: "Lisa Brown",
        zone: "Zone C",
        description: "PPE compliance warning - safety vest improperly worn",
        detectedBy: "PPE Detection AI",
        detectionTime: "2025-11-30 16:15",
        status: "Resolved",
        severity: 4,
        relatedData: {
            ppeCompliance: "Warning",
            confidence: 68,
        },
    },
    {
        id: "INC-20251130-010",
        type: "Machine",
        entityName: "Laser Cutter Pro",
        zone: "Zone B",
        description: "Calibration drift detected - precision affected",
        detectedBy: "Quality Control AI",
        detectionTime: "2025-11-30 15:50",
        status: "Resolved",
        severity: 5,
        relatedData: {
            machinePerformance: 95,
            temperature: 75,
        },
    },
    {
        id: "INC-20251130-011",
        type: "Worker",
        entityName: "Christopher Martinez",
        zone: "Zone A",
        description: "PPE non-compliance - multiple safety items missing",
        detectedBy: "PPE Detection AI",
        detectionTime: "2025-11-30 15:20",
        status: "Resolved",
        severity: 8,
        relatedData: {
            ppeCompliance: "Non-Compliant",
            confidence: 81,
        },
    },
    {
        id: "INC-20251130-012",
        type: "Machine",
        entityName: "Conveyor System 1",
        zone: "Zone A",
        description: "Belt tension anomaly - potential slip risk",
        detectedBy: "Mechanical Monitoring AI",
        detectionTime: "2025-11-30 14:30",
        status: "Pending",
        severity: 6,
        relatedData: {
            machinePerformance: 92,
            temperature: 68,
        },
    },
    {
        id: "INC-20251130-013",
        type: "Worker",
        entityName: "David Thompson",
        zone: "Zone A",
        description: "Worker entered restricted zone without proper clearance",
        detectedBy: "Zone Access AI",
        detectionTime: "2025-11-30 14:00",
        status: "Pending",
        severity: 7,
        relatedData: {
            ppeCompliance: "Compliant",
            confidence: 97,
        },
    },
    {
        id: "INC-20251130-014",
        type: "Machine",
        entityName: "Robotic Arm X2",
        zone: "Zone B",
        description: "Scheduled maintenance window approaching within 48 hours",
        detectedBy: "Maintenance Scheduler AI",
        detectionTime: "2025-11-30 13:45",
        status: "Pending",
        severity: 5,
        relatedData: {
            machinePerformance: 82,
            temperature: 79,
        },
    },
    {
        id: "INC-20251130-015",
        type: "Worker",
        entityName: "Jennifer Lee",
        zone: "Zone D",
        description: "Extended work duration detected - fatigue risk assessment triggered",
        detectedBy: "Worker Safety AI",
        detectionTime: "2025-11-30 13:00",
        status: "Resolved",
        severity: 4,
        relatedData: {
            ppeCompliance: "Compliant",
            confidence: 96,
        },
    },
];

export const backlogOverview = {
    totalIncidents: 15,
    machineIncidents: 8,
    workerIncidents: 7,
    unresolvedCases: 9,
    resolvedCases: 6,
    criticalIncidents: 3,
    lastIncidentTime: "2025-11-30 20:45",
};

// Helper function to get incidents by time range
export function getIncidentsByHours(hours: number): Incident[] {
    const now = new Date("2025-11-30T21:03:46+01:00");
    const cutoffTime = new Date(now.getTime() - hours * 60 * 60 * 1000);

    return incidentsData.filter((incident) => {
        const incidentTime = new Date(incident.detectionTime);
        return incidentTime >= cutoffTime;
    });
}

// Helper function to get incident statistics
export function getIncidentStats(incidents: Incident[]) {
    return {
        total: incidents.length,
        machine: incidents.filter((i) => i.type === "Machine").length,
        worker: incidents.filter((i) => i.type === "Worker").length,
        critical: incidents.filter((i) => i.status === "Critical").length,
        pending: incidents.filter((i) => i.status === "Pending").length,
        resolved: incidents.filter((i) => i.status === "Resolved").length,
    };
}
