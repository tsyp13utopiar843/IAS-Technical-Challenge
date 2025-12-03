"use server";

import { SystemState } from "@/types/agent";

const BASE_URL =
    process.env.NEXT_PUBLIC_API_GATEWAY || "http://localhost:8080";
const ORCHESTRATOR_PATH = "/api/orchestrator";

/**
 * Fetch system-wide state from the Orchestrator
 * @returns SystemState object with alerts, decisions, and last_update
 */
export async function fetchSystemState(): Promise<SystemState | null> {
    try {
        const response = await fetch(
            `${BASE_URL}${ORCHESTRATOR_PATH}/system-state`,
            {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                },
                cache: "no-store", // Ensure fresh data
            }
        );

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
        const response = await fetch(
            `${BASE_URL}${ORCHESTRATOR_PATH}/status`,
            {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                },
                cache: "no-store",
            }
        );

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
