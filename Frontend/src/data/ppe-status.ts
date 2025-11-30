export interface Worker {
  id: string;
  name: string;
  zone: string;
  ppeStatus: "Compliant" | "Non-Compliant" | "Warning";
  confidence: number;
  lastUpdated: string;
  phone: string;
}

export const workersData: Worker[] = [
  {
    id: "W001",
    name: "John Anderson",
    zone: "Zone A",
    ppeStatus: "Compliant",
    confidence: 98,
    lastUpdated: "2025-11-29 08:45",
    phone: "+1-555-0101",
  },
  {
    id: "W002",
    name: "Sarah Mitchell",
    zone: "Zone B",
    ppeStatus: "Non-Compliant",
    confidence: 87,
    lastUpdated: "2025-11-29 09:12",
    phone: "+1-555-0102",
  },
  {
    id: "W003",
    name: "Michael Chen",
    zone: "Zone A",
    ppeStatus: "Warning",
    confidence: 72,
    lastUpdated: "2025-11-29 09:30",
    phone: "+1-555-0103",
  },
  {
    id: "W004",
    name: "Emily Rodriguez",
    zone: "Zone C",
    ppeStatus: "Compliant",
    confidence: 95,
    lastUpdated: "2025-11-29 08:20",
    phone: "+1-555-0104",
  },
  {
    id: "W005",
    name: "James Wilson",
    zone: "Zone B",
    ppeStatus: "Compliant",
    confidence: 92,
    lastUpdated: "2025-11-29 09:45",
    phone: "+1-555-0105",
  },
  {
    id: "W006",
    name: "Maria Garcia",
    zone: "Zone D",
    ppeStatus: "Non-Compliant",
    confidence: 85,
    lastUpdated: "2025-11-29 10:05",
    phone: "+1-555-0106",
  },
  {
    id: "W007",
    name: "David Thompson",
    zone: "Zone A",
    ppeStatus: "Compliant",
    confidence: 97,
    lastUpdated: "2025-11-29 07:55",
    phone: "+1-555-0107",
  },
  {
    id: "W008",
    name: "Lisa Brown",
    zone: "Zone C",
    ppeStatus: "Warning",
    confidence: 68,
    lastUpdated: "2025-11-29 10:15",
    phone: "+1-555-0108",
  },
  {
    id: "W009",
    name: "Robert Taylor",
    zone: "Zone B",
    ppeStatus: "Compliant",
    confidence: 94,
    lastUpdated: "2025-11-29 08:30",
    phone: "+1-555-0109",
  },
  {
    id: "W010",
    name: "Jennifer Lee",
    zone: "Zone D",
    ppeStatus: "Compliant",
    confidence: 96,
    lastUpdated: "2025-11-29 09:00",
    phone: "+1-555-0110",
  },
  {
    id: "W011",
    name: "Christopher Martinez",
    zone: "Zone A",
    ppeStatus: "Non-Compliant",
    confidence: 81,
    lastUpdated: "2025-11-29 10:20",
    phone: "+1-555-0111",
  },
  {
    id: "W012",
    name: "Amanda White",
    zone: "Zone C",
    ppeStatus: "Compliant",
    confidence: 93,
    lastUpdated: "2025-11-29 08:10",
    phone: "+1-555-0112",
  },
];

export const ppeOverview = {
  totalWorkers: 12,
  compliantWorkers: 7,
  nonCompliantWorkers: 3,
  lastAlertSent: "2025-11-29 09:12",
};
