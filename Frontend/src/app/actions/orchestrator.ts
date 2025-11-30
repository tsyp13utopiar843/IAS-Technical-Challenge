"use server";

import { SystemState } from "@/types/agent";

const ORCHESTRATOR_URL =
    process.env.ORCHESTRATOR_URL || "http://localhost:8000";

/**
 * Fetch system-wide state from the Orchestrator
 * @returns SystemState object with alerts, decisions, and last_update
 */
export async function fetchSystemState(): Promise<SystemState | null> {
    try {
        const response = await fetch(`${ORCHESTRATOR_URL}/system-state`, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
            cache: "no-store", // Ensure fresh data
        });

        if (!response.ok) {
            console.error(
                `Failed to fetch system state: ${response.status} ${response.statusText}`
            );
            return null;
        }

        const data: SystemState = await response.json();
        return data;
    } catch (error) {
        console.error("Error fetching system state:", error);
        return null;
    }
}

/**
 * Fetch orchestrator status
 * @returns Status object
 */
export async function fetchOrchestratorStatus(): Promise<any> {
    try {
        const response = await fetch(`${ORCHESTRATOR_URL}/status`, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
            cache: "no-store",
        });

        if (!response.ok) {
            console.error(
                `Failed to fetch orchestrator status: ${response.status} ${response.statusText}`
            );
            return null;
        }

        return await response.json();
    } catch (error) {
        console.error("Error fetching orchestrator status:", error);
        return null;
    }
}
