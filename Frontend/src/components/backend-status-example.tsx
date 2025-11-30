"use client";

import { useEffect, useState } from "react";
import { RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import Container from "@/components/container";
import { fetchSystemState } from "@/app/actions/orchestrator";
import { fetchAllAgentStatuses } from "@/app/actions/agents";
import type { SystemState } from "@/types/agent";

/**
 * Example Dashboard Component showing backend integration
 * This demonstrates how to:
 * 1. Fetch data from backend using Server Actions
 * 2. Implement client-side polling for updates
 * 3. Handle loading and error states
 */
export default function BackendStatusExample() {
    const [systemState, setSystemState] = useState<SystemState | null>(null);
    const [agentStatuses, setAgentStatuses] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [lastUpdate, setLastUpdate] = useState<string>("");

    // Fetch data function
    const fetchData = async () => {
        setLoading(true);
        try {
            // Fetch system state from Orchestrator
            const state = await fetchSystemState();
            setSystemState(state);

            // Fetch all agent statuses
            const statuses = await fetchAllAgentStatuses();
            setAgentStatuses(statuses);

            setLastUpdate(new Date().toLocaleTimeString());
        } catch (error) {
            console.error("Error fetching backend data:", error);
        } finally {
            setLoading(false);
        }
    };

    // Fetch data on mount
    useEffect(() => {
        fetchData();
    }, []);

    // Optional: Polling - fetch data every 5 seconds
    useEffect(() => {
        const interval = setInterval(() => {
            fetchData();
        }, 5000); // 5 seconds

        return () => clearInterval(interval);
    }, []);

    return (
        <Container className="p-6 space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold">Backend Integration Status</h1>
                    <p className="text-sm text-muted-foreground">
                        Last updated: {lastUpdate || "Never"}
                    </p>
                </div>
                <Button
                    onClick={fetchData}
                    disabled={loading}
                    variant="outline"
                    size="sm"
                >
                    <RefreshCw className={`h-4 w-4 mr-2 ${loading ? "animate-spin" : ""}`} />
                    Refresh
                </Button>
            </div>

            {/* System State from Orchestrator */}
            <div className="rounded-lg border bg-card p-6 shadow-sm">
                <h2 className="text-xl font-semibold mb-4">System State (Orchestrator)</h2>
                {systemState ? (
                    <div className="space-y-4">
                        <div>
                            <h3 className="font-medium mb-2">Alerts ({systemState.alerts?.length || 0})</h3>
                            {systemState.alerts && systemState.alerts.length > 0 ? (
                                <div className="space-y-2">
                                    {systemState.alerts.slice(0, 3).map((alert, idx) => (
                                        <div key={idx} className="flex items-center gap-2">
                                            <Badge
                                                variant={
                                                    alert.level === "critical"
                                                        ? "danger"
                                                        : alert.level === "warning"
                                                            ? "warning"
                                                            : "default"
                                                }
                                            >
                                                {alert.level}
                                            </Badge>
                                            <span className="text-sm">{alert.source}: {alert.details}</span>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <p className="text-sm text-muted-foreground">No alerts</p>
                            )}
                        </div>

                        <div>
                            <h3 className="font-medium mb-2">Recent Decisions ({systemState.decisions?.length || 0})</h3>
                            {systemState.decisions && systemState.decisions.length > 0 ? (
                                <div className="space-y-2">
                                    {systemState.decisions.slice(0, 3).map((decision, idx) => (
                                        <div key={idx} className="text-sm">
                                            <strong>{decision.plan?.action || "N/A"}</strong>
                                            <span className="text-muted-foreground ml-2">
                                                ({new Date(decision.timestamp).toLocaleTimeString()})
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <p className="text-sm text-muted-foreground">No decisions</p>
                            )}
                        </div>
                    </div>
                ) : (
                    <p className="text-muted-foreground">
                        {loading ? "Loading..." : "Failed to fetch system state. Ensure backend is running."}
                    </p>
                )}
            </div>

            {/* Agent Statuses */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {agentStatuses ? (
                    <>
                        <AgentStatusCard
                            name="PM Agent"
                            status={agentStatuses.pm}
                            loading={loading}
                        />
                        <AgentStatusCard
                            name="Energy Agent"
                            status={agentStatuses.energy}
                            loading={loading}
                        />
                        <AgentStatusCard
                            name="Cyber Agent"
                            status={agentStatuses.cyber}
                            loading={loading}
                        />
                        <AgentStatusCard
                            name="Safety Agent"
                            status={agentStatuses.safety}
                            loading={loading}
                        />
                        <AgentStatusCard
                            name="PPE Agent"
                            status={agentStatuses.ppe}
                            loading={loading}
                        />
                    </>
                ) : (
                    <p className="col-span-full text-muted-foreground">
                        {loading ? "Loading agents..." : "Failed to fetch agent statuses"}
                    </p>
                )}
            </div>
        </Container>
    );
}

// Helper component for agent status cards
function AgentStatusCard({
    name,
    status,
    loading,
}: {
    name: string;
    status: any;
    loading: boolean;
}) {
    return (
        <div className="rounded-lg border bg-card p-4 shadow-sm">
            <h3 className="font-semibold mb-2">{name}</h3>
            {status ? (
                <div className="space-y-1 text-sm">
                    <div className="flex items-center justify-between">
                        <span className="text-muted-foreground">Status:</span>
                        <Badge variant="success">{status.status || "Active"}</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                        <span className="text-muted-foreground">Agent ID:</span>
                        <span className="font-mono text-xs">{status.agent_id || "N/A"}</span>
                    </div>
                    {status.last_prediction && (
                        <div className="mt-2 pt-2 border-t">
                            <span className="text-xs text-muted-foreground">Last Prediction:</span>
                            <pre className="text-xs mt-1 overflow-auto max-h-20 bg-muted/50 p-2 rounded">
                                {JSON.stringify(status.last_prediction, null, 2)}
                            </pre>
                        </div>
                    )}
                </div>
            ) : (
                <p className="text-sm text-muted-foreground">
                    {loading ? "Loading..." : "Offline or unavailable"}
                </p>
            )}
        </div>
    );
}
