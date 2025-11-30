export interface MaintenanceLog {
  id: string;
  component: string;
  technician: string;
  description: string;
  status: "Completed" | "Pending" | "In Progress";
  timestamp: string;
}

export interface TimelineEvent {
  id: string;
  title: string;
  description: string;
  date: string;
  type: "incident" | "completed" | "scheduled";
}

export const maintenanceLogsData: MaintenanceLog[] = [
  {
    id: "M001",
    component: "Camera Unit A3",
    technician: "Alex Johnson",
    description: "Replaced lens and recalibrated detection system",
    status: "Completed",
    timestamp: "2025-11-28 14:30",
  },
  {
    id: "M002",
    component: "Processing Server 2",
    technician: "Maria Santos",
    description: "Updated AI model and optimized inference pipeline",
    status: "Completed",
    timestamp: "2025-11-27 10:15",
  },
  {
    id: "M003",
    component: "Network Switch B",
    technician: "Tom Harrison",
    description: "Firmware update and connectivity check",
    status: "In Progress",
    timestamp: "2025-11-29 09:00",
  },
  {
    id: "M004",
    component: "Camera Unit D7",
    technician: "Sarah Kim",
    description: "Hardware inspection and cleaning",
    status: "Pending",
    timestamp: "2025-11-30 08:00",
  },
  {
    id: "M005",
    component: "Alert System",
    technician: "David Chen",
    description: "Tested Twilio integration and notification delivery",
    status: "Completed",
    timestamp: "2025-11-26 16:45",
  },
  {
    id: "M006",
    component: "Database Server",
    technician: "Lisa Wong",
    description: "Performance tuning and index optimization",
    status: "Completed",
    timestamp: "2025-11-25 11:20",
  },
  {
    id: "M007",
    component: "Camera Unit B5",
    technician: "Alex Johnson",
    description: "Replace faulty power supply unit",
    status: "Pending",
    timestamp: "2025-12-01 10:00",
  },
  {
    id: "M008",
    component: "Edge Computing Node",
    technician: "Tom Harrison",
    description: "Routine maintenance and software updates",
    status: "In Progress",
    timestamp: "2025-11-29 11:00",
  },
];

export const timelineEvents: TimelineEvent[] = [
  {
    id: "T001",
    title: "Camera A3 Maintenance",
    description: "Lens replacement completed successfully",
    date: "2025-11-28",
    type: "completed",
  },
  {
    id: "T002",
    title: "PPE Detection Failure",
    description: "Multiple workers reported as non-compliant in Zone B",
    date: "2025-11-27",
    type: "incident",
  },
  {
    id: "T003",
    title: "AI Model Update",
    description: "Processing Server 2 upgraded with improved detection",
    date: "2025-11-27",
    type: "completed",
  },
  {
    id: "T004",
    title: "Scheduled: Camera D7 Inspection",
    description: "Hardware inspection and cleaning scheduled",
    date: "2025-11-30",
    type: "scheduled",
  },
  {
    id: "T005",
    title: "Network Switch Update",
    description: "Firmware update in progress",
    date: "2025-11-29",
    type: "completed",
  },
  {
    id: "T006",
    title: "Scheduled: Camera B5 Repair",
    description: "Power supply replacement scheduled",
    date: "2025-12-01",
    type: "scheduled",
  },
];
