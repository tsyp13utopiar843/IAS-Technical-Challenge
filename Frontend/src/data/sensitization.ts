export interface SensitizationSettings {
  helmetThreshold: number;
  gloveThreshold: number;
  bootThreshold: number;
  alertDelay: number;
  allowNotifications: boolean;
  autoEscalationLevel: string;
  incidentLogging: boolean;
}

export const defaultSettings: SensitizationSettings = {
  helmetThreshold: 85,
  gloveThreshold: 80,
  bootThreshold: 75,
  alertDelay: 5,
  allowNotifications: true,
  autoEscalationLevel: "supervisor",
  incidentLogging: true,
};
