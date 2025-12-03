"use server";

import {
    AgentStatus,
    PMStatus,
    EnergyStatus,
    CyberStatus,
    SafetyStatus,
    PPEStatus,
    HistoryResponse,
} from "@/types/agent";

// Base API Gateway URL (Nginx)
const BASE_URL =
    process.env.NEXT_PUBLIC_API_GATEWAY || "http://localhost:8080";

const PM_AGENT_PATH = "/api/pm";
const ENERGY_AGENT_PATH = "/api/energy";
const CYBER_AGENT_PATH = "/api/cyber";
const SAFETY_AGENT_PATH = "/api/safety";
const PPE_AGENT_PATH = "/api/ppe";

function buildAgentUrl(agentPath: string): string {
    return `${BASE_URL}${agentPath}`;
}

/**
 * Generic function to fetch agent status
 * @param agentPath - API path of the agent
 * @returns Agent status object or null on error
 */
export async function fetchAgentStatus(
    agentPath: string
): Promise<AgentStatus | null> {
    try {
        const response = await fetch(`${buildAgentUrl(agentPath)}/status`, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
            cache: "no-store",
        });

        if (!response.ok) {
            console.error(
                `Failed to fetch agent status from ${agentPath}: ${response.status} ${response.statusText}`
            );
            return null;
        }

        const data: AgentStatus = await response.json();
        return data;
    } catch (error) {
        console.error(`Error fetching agent status from ${agentPath}:`, error);
        return null;
    }
}

/**
 * Generic function to fetch agent prediction history
 * @param agentPath - API path of the agent
 * @param limit - Number of history items to fetch (default: 10)
 * @returns History response or null on error
 */
export async function fetchAgentHistory(
    agentPath: string,
    limit: number = 10
): Promise<HistoryResponse | null> {
    try {
        const response = await fetch(
            `${buildAgentUrl(agentPath)}/history?limit=${limit}`,
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
                `Failed to fetch agent history from ${agentPath}: ${response.status} ${response.statusText}`
            );
            return null;
        }

        const data: HistoryResponse = await response.json();
        return data;
    } catch (error) {
        console.error(`Error fetching agent history from ${agentPath}:`, error);
        return null;
    }
}

/**
 * Check agent health
 * @param agentUrl - Base URL of the agent
 * @returns Health status or null on error
 */
export async function fetchAgentHealth(agentUrl: string): Promise<any> {
    try {
        const response = await fetch(`${agentUrl}/health`, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
            cache: "no-store",
        });

        if (!response.ok) {
            console.error(
                `Failed to fetch agent health from ${agentUrl}: ${response.status} ${response.statusText}`
            );
            return null;
        }

        return await response.json();
    } catch (error) {
        console.error(`Error fetching agent health from ${agentUrl}:`, error);
        return null;
    }
}

// ==================== SPECIFIC AGENT HELPERS ====================

/**
 * Fetch Predictive Maintenance Agent status
 */
export async function fetchPMStatus(): Promise<PMStatus | null> {
    return fetchAgentStatus(PM_AGENT_PATH) as Promise<PMStatus | null>;
}

/**
 * Fetch PM Agent prediction history
 */
export async function fetchPMHistory(
    limit: number = 10
): Promise<HistoryResponse | null> {
    return fetchAgentHistory(PM_AGENT_PATH, limit);
}

/**
 * Fetch Energy Agent status
 */
export async function fetchEnergyStatus(): Promise<EnergyStatus | null> {
    return fetchAgentStatus(ENERGY_AGENT_PATH) as Promise<EnergyStatus | null>;
}

/**
 * Fetch Energy Agent prediction history
 */
export async function fetchEnergyHistory(
    limit: number = 10
): Promise<HistoryResponse | null> {
    return fetchAgentHistory(ENERGY_AGENT_PATH, limit);
}

/**
 * Fetch Cyber Security Agent status
 */
export async function fetchCyberStatus(): Promise<CyberStatus | null> {
    return fetchAgentStatus(CYBER_AGENT_PATH) as Promise<CyberStatus | null>;
}

/**
 * Fetch Cyber Agent prediction history
 */
export async function fetchCyberHistory(
    limit: number = 10
): Promise<HistoryResponse | null> {
    return fetchAgentHistory(CYBER_AGENT_PATH, limit);
}

/**
 * Fetch Safety Agent status
 */
export async function fetchSafetyStatus(): Promise<SafetyStatus | null> {
    return fetchAgentStatus(SAFETY_AGENT_PATH) as Promise<SafetyStatus | null>;
}

/**
 * Fetch Safety Agent prediction history
 */
export async function fetchSafetyHistory(
    limit: number = 10
): Promise<HistoryResponse | null> {
    return fetchAgentHistory(SAFETY_AGENT_PATH, limit);
}

/**
 * Fetch PPE Agent status
 */
export async function fetchPPEStatus(): Promise<PPEStatus | null> {
    return fetchAgentStatus(PPE_AGENT_PATH) as Promise<PPEStatus | null>;
}

/**
 * Fetch PPE Agent prediction history
 */
export async function fetchPPEHistory(
    limit: number = 10
): Promise<HistoryResponse | null> {
    return fetchAgentHistory(PPE_AGENT_PATH, limit);
}

/**
 * Fetch all agent statuses at once
 */
export async function fetchAllAgentStatuses() {
    const [pm, energy, cyber, safety, ppe] = await Promise.all([
        fetchPMStatus(),
        fetchEnergyStatus(),
        fetchCyberStatus(),
        fetchSafetyStatus(),
        fetchPPEStatus(),
    ]);

    return {
        pm,
        energy,
        cyber,
        safety,
        ppe,
    };
}
