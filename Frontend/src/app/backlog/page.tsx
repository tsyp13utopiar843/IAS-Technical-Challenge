"use client";

import { useState, useMemo } from "react";
import { VChart } from "@visactor/react-vchart";
import type { IPieChartSpec, IBarChartSpec, ILineChartSpec } from "@visactor/vchart";
import {
  Search,
  Eye,
  CheckCircle,
  AlertTriangle,
  Bot,
  User,
  Filter,
  Calendar,
  TrendingUp,
  XCircle,
  Clock,
  BarChart3,
  PieChart,
  Activity,
} from "lucide-react";
import Container from "@/components/container";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  backlogOverview,
  getIncidentsByHours,
  type Incident,
} from "@/data/backlog-incidents";
import { useToast } from "@/components/ui/use-toast";
import { chartTitle } from "@/components/primitives";
import { cn } from "@/lib/utils";

type FilterType = "all" | "machine" | "worker" | "critical" | "pending";

export default function BacklogPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null);
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false);
  const [activeFilter, setActiveFilter] = useState<FilterType>("all");
  const { toast } = useToast();

  // Get incidents from last 8 hours
  const last8HoursIncidents = useMemo(() => getIncidentsByHours(8), []);

  // Filter and search incidents
  const filteredIncidents = useMemo(() => {
    let filtered = last8HoursIncidents;

    // Apply filter
    switch (activeFilter) {
      case "machine":
        filtered = filtered.filter((i) => i.type === "Machine");
        break;
      case "worker":
        filtered = filtered.filter((i) => i.type === "Worker");
        break;
      case "critical":
        filtered = filtered.filter((i) => i.status === "Critical");
        break;
      case "pending":
        filtered = filtered.filter((i) => i.status === "Pending");
        break;
    }

    // Apply search
    if (searchQuery) {
      filtered = filtered.filter(
        (incident) =>
          incident.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
          incident.entityName.toLowerCase().includes(searchQuery.toLowerCase()) ||
          incident.zone.toLowerCase().includes(searchQuery.toLowerCase()) ||
          incident.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
          incident.detectedBy.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    return filtered;
  }, [last8HoursIncidents, activeFilter, searchQuery]);

  const handleViewDetails = (incident: Incident) => {
    setSelectedIncident(incident);
    setDetailsDialogOpen(true);
  };

  const handleMarkResolved = (incident: Incident) => {
    toast({
      title: "Incident Resolved",
      description: `${incident.id} has been marked as resolved`,
    });
    // In a real app, this would update the backend
  };

  const getStatusBadge = (status: Incident["status"]) => {
    switch (status) {
      case "Critical":
        return <Badge variant="danger">Critical</Badge>;
      case "Pending":
        return <Badge variant="warning">Pending</Badge>;
      case "Resolved":
        return <Badge variant="success">Resolved</Badge>;
    }
  };

  const getTypeIcon = (type: Incident["type"]) => {
    return type === "Machine" ? (
      <Bot className="h-4 w-4 text-blue-500" />
    ) : (
      <User className="h-4 w-4 text-purple-500" />
    );
  };

  const getSeverityColor = (severity: number) => {
    if (severity >= 8) return "text-red-600 dark:text-red-500";
    if (severity >= 5) return "text-yellow-600 dark:text-yellow-500";
    return "text-green-600 dark:text-green-500";
  };

  const getSeverityBg = (severity: number) => {
    if (severity >= 8) return "bg-red-600 dark:bg-red-500";
    if (severity >= 5) return "bg-yellow-600 dark:bg-yellow-500";
    return "bg-green-600 dark:bg-green-500";
  };

  // Calculate incident frequency by hour for mini chart
  const hourlyIncidents = useMemo(() => {
    const hours = Array.from({ length: 8 }, (_, i) => i);
    return hours.map((hour) => {
      const incidents = getIncidentsByHours(hour + 1).length - getIncidentsByHours(hour).length;
      return incidents;
    }).reverse();
  }, []);

  return (
    <div>
      {/* Overview Cards */}
      <div className="grid grid-cols-1 gap-4 border-b border-border p-4 tablet:grid-cols-2 laptop:grid-cols-5">
        <Container className="rounded-lg border bg-card p-6 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between mb-2">
            <h2 className={cn(chartTitle({ color: "mute", size: "sm" }), "mb-0")}>
              Total Incidents
            </h2>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </div>
          <p className="text-3xl font-bold text-primary">
            {backlogOverview.totalIncidents}
          </p>
          <p className="text-xs text-muted-foreground mt-1">Last 8 hours</p>
        </Container>

        <Container className="rounded-lg border bg-card p-6 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between mb-2">
            <h2 className={cn(chartTitle({ color: "mute", size: "sm" }), "mb-0")}>
              Machine Incidents
            </h2>
            <Bot className="h-4 w-4 text-blue-500" />
          </div>
          <p className="text-3xl font-bold text-blue-600 dark:text-blue-500">
            {backlogOverview.machineIncidents}
          </p>
          <p className="text-xs text-muted-foreground mt-1">Equipment issues</p>
        </Container>

        <Container className="rounded-lg border bg-card p-6 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between mb-2">
            <h2 className={cn(chartTitle({ color: "mute", size: "sm" }), "mb-0")}>
              Worker Incidents
            </h2>
            <User className="h-4 w-4 text-purple-500" />
          </div>
          <p className="text-3xl font-bold text-purple-600 dark:text-purple-500">
            {backlogOverview.workerIncidents}
          </p>
          <p className="text-xs text-muted-foreground mt-1">Safety alerts</p>
        </Container>

        <Container className="rounded-lg border bg-card p-6 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between mb-2">
            <h2 className={cn(chartTitle({ color: "mute", size: "sm" }), "mb-0")}>
              Critical Cases
            </h2>
            <XCircle className="h-4 w-4 text-red-500" />
          </div>
          <p className="text-3xl font-bold text-red-600 dark:text-red-500">
            {backlogOverview.criticalIncidents}
          </p>
          <p className="text-xs text-muted-foreground mt-1">Needs attention</p>
        </Container>

        <Container className="rounded-lg border bg-card p-6 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between mb-2">
            <h2 className={cn(chartTitle({ color: "mute", size: "sm" }), "mb-0")}>
              Resolved Cases
            </h2>
            <CheckCircle className="h-4 w-4 text-green-500" />
          </div>
          <p className="text-3xl font-bold text-green-600 dark:text-green-500">
            {backlogOverview.resolvedCases}
          </p>
          <p className="text-xs text-muted-foreground mt-1">Completed</p>
        </Container>
      </div>

      {/* Professional Charts Section */}
      <Container className="p-4 border-b border-border">
        <div className="grid grid-cols-1 gap-4 laptop:grid-cols-3">
          {/* Incident Type Distribution */}
          <div className="rounded-lg border bg-card p-4 shadow-sm">
            <div className="flex items-center gap-2 mb-4">
              <PieChart className="h-4 w-4 text-muted-foreground" />
              <h3 className="text-sm font-medium">Incident Distribution</h3>
            </div>
            <VChart
              spec={{
                type: "pie",
                background: "transparent",
                data: [
                  {
                    id: "incident-type",
                    values: [
                      { type: "Machine", value: backlogOverview.machineIncidents, color: "#3b82f6" },
                      { type: "Worker", value: backlogOverview.workerIncidents, color: "#a855f7" },
                    ],
                  },
                ],
                categoryField: "type",
                valueField: "value",
                seriesField: "type",
                outerRadius: 0.8,
                innerRadius: 0.5,
                legends: {
                  visible: true,
                  orient: "bottom",
                  item: {
                    label: {
                      style: {
                        fill: "hsl(var(--foreground))",
                      },
                    },
                  },
                },
                label: {
                  visible: true,
                  position: "outside",
                  style: {
                    fill: "hsl(var(--foreground))",
                  },
                },
                tooltip: {
                  mark: {
                    content: [
                      {
                        key: (datum: { type: string; value: number }) => datum.type,
                        value: (datum: { type: string; value: number }) => datum.value,
                      },
                    ],
                  },
                },
                color: {
                  specified: {
                    Machine: "#3b82f6",
                    Worker: "#a855f7",
                  },
                },
              } as unknown as IPieChartSpec}
              style={{ height: "250px" }}
            />
          </div>

          {/* Incidents by Zone */}
          <div className="rounded-lg border bg-card p-4 shadow-sm">
            <div className="flex items-center gap-2 mb-4">
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
              <h3 className="text-sm font-medium">Incidents by Zone</h3>
            </div>
            <VChart
              spec={{
                type: "bar",
                background: "transparent",
                data: [
                  {
                    id: "zone-data",
                    values: (() => {
                      const zoneCounts = last8HoursIncidents.reduce((acc: Record<string, number>, inc) => {
                        acc[inc.zone] = (acc[inc.zone] || 0) + 1;
                        return acc;
                      }, {});
                      return Object.entries(zoneCounts).map(([zone, count]) => ({
                        zone,
                        count,
                      }));
                    })(),
                  },
                ],
                xField: "zone",
                yField: "count",
                seriesField: "zone",
                label: {
                  visible: true,
                  position: "top",
                  style: {
                    fill: "hsl(var(--foreground))",
                  },
                },
                axes: [
                  {
                    orient: "bottom",
                    type: "band",
                    label: {
                      style: {
                        fill: "hsl(var(--muted-foreground))",
                      },
                    },
                  },
                  {
                    orient: "left",
                    type: "linear",
                    label: {
                      style: {
                        fill: "hsl(var(--muted-foreground))",
                      },
                    },
                    grid: {
                      visible: true,
                      style: {
                        stroke: "hsl(var(--border))",
                        lineWidth: 1,
                        lineDash: [4, 4],
                      },
                    },
                  },
                ],
                bar: {
                  style: {
                    fill: "#10b981",
                  },
                },
              } as IBarChartSpec}
              style={{ height: "250px" }}
            />
          </div>

          {/* Status Distribution */}
          <div className="rounded-lg border bg-card  p-4 shadow-sm">
            <div className="flex items-center gap-2 mb-4">
              <Activity className="h-4 w-4 text-muted-foreground" />
              <h3 className="text-sm font-medium">Status Breakdown</h3>
            </div>
            <VChart
              spec={{
                type: "pie",
                background: "transparent",
                data: [
                  {
                    id: "status-data",
                    values: [
                      { status: "Critical", value: last8HoursIncidents.filter(i => i.status === "Critical").length },
                      { status: "Pending", value: last8HoursIncidents.filter(i => i.status === "Pending").length },
                      { status: "Resolved", value: last8HoursIncidents.filter(i => i.status === "Resolved").length },
                    ],
                  },
                ],
                categoryField: "status",
                valueField: "value",
                seriesField: "status",
                outerRadius: 0.8,
                innerRadius: 0.5,
                legends: {
                  visible: true,
                  orient: "bottom",
                  item: {
                    label: {
                      style: {
                        fill: "hsl(var(--foreground))",
                      },
                    },
                  },
                },
                label: {
                  visible: true,
                  position: "outside",
                  style: {
                    fill: "hsl(var(--foreground))",
                  },
                },
                color: {
                  specified: {
                    Critical: "#ef4444",
                    Pending: "#f59e0b",
                    Resolved: "#10b981",
                  },
                },
              } as unknown as IPieChartSpec}
              style={{ height: "250px" }}
            />
          </div>
        </div>
      </Container>

      {/* Hourly Trend Line Chart */}
      <Container className="p-4 border-b border-border">
        <div className="rounded-lg border bg-card p-4 shadow-sm">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
            <h3 className="text-sm font-medium">Incident Trend (Last 8 Hours)</h3>
          </div>
          <VChart
            spec={{
              type: "line",
              background: "transparent",
              data: [
                {
                  id: "hourly-trend",
                  values: hourlyIncidents.map((count, index) => ({
                    hour: `-${7 - index}h`,
                    count,
                    timestamp: index,
                  })),
                },
              ],
              xField: "hour",
              yField: "count",
              point: {
                visible: true,
                style: {
                  size: 5,
                  fill: "#3b82f6",
                  stroke: "#1e40af",
                  lineWidth: 2,
                },
              },
              line: {
                style: {
                  stroke: "#3b82f6",
                  lineWidth: 2,
                },
              },
              area: {
                visible: true,
                style: {
                  fill: "#3b82f6",
                  fillOpacity: 0.2,
                },
              },
              axes: [
                {
                  orient: "bottom",
                  type: "band",
                  label: {
                    style: {
                      fill: "hsl(var(--muted-foreground))",
                    },
                  },
                },
                {
                  orient: "left",
                  type: "linear",
                  label: {
                    style: {
                      fill: "hsl(var(--muted-foreground))",
                    },
                  },
                  grid: {
                    visible: true,
                    style: {
                      stroke: "hsl(var(--border))",
                      lineWidth: 1,
                      lineDash: [4, 4],
                    },
                  },
                },
              ],
              legends: {
                visible: false,
              },
            } as ILineChartSpec}
            style={{ height: "200px" }}
          />
        </div>
      </Container>

      {/* Incidents Table */}
      <Container className="p-4">
        <div className="rounded-lg border bg-card shadow-sm">
          <div className="border-b p-4">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold">Recent Incidents Log (Last 8 Hours)</h2>
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Calendar className="h-4 w-4" />
                <span>{new Date().toLocaleDateString()}</span>
              </div>
            </div>
            
            {/* Quick Filters */}
            <div className="flex flex-wrap gap-2 mb-4">
              <Button
                size="sm"
                variant={activeFilter === "all" ? "default" : "outline"}
                onClick={() => setActiveFilter("all")}
                className={activeFilter === "all" ? "text-white" : ""}
              >
                <Filter className="mr-1 h-3 w-3" />
                All Incidents
              </Button>
              <Button
                size="sm"
                variant={activeFilter === "critical" ? "default" : "outline"}
                onClick={() => setActiveFilter("critical")}
                className={activeFilter === "critical" ? "text-white" : ""}
              >
                <AlertTriangle className="mr-1 h-3 w-3" />
                Critical
              </Button>
              <Button
                size="sm"
                variant={activeFilter === "machine" ? "default" : "outline"}
                onClick={() => setActiveFilter("machine")}
                className={activeFilter === "machine" ? "text-white" : ""}
              >
                <Bot className="mr-1 h-3 w-3" />
                Machine
              </Button>
              <Button
                size="sm"
                variant={activeFilter === "worker" ? "default" : "outline"}
                onClick={() => setActiveFilter("worker")}
                className={activeFilter === "worker" ? "text-white" : ""}
              >
                <User className="mr-1 h-3 w-3" />
                Worker
              </Button>
              <Button
                size="sm"
                variant={activeFilter === "pending" ? "default" : "outline"}
                onClick={() => setActiveFilter("pending")}
                className={activeFilter === "pending" ? "text-white" : ""}
              >
                <Clock className="mr-1 h-3 w-3" />
                Pending
              </Button>
            </div>
            
            <div className="relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Search by incident ID, entity name, zone, description..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
            {searchQuery || activeFilter !== "all" ? (
              <div className="mt-2 text-sm text-muted-foreground">
                Showing {filteredIncidents.length} of {last8HoursIncidents.length} incidents
              </div>
            ) : null}
          </div>

          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Incident ID</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Entity Name</TableHead>
                  <TableHead>Zone</TableHead>
                  <TableHead>Description</TableHead>
                  <TableHead>Detected By</TableHead>
                  <TableHead>Detection Time</TableHead>
                  <TableHead>Severity</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredIncidents.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={10} className="text-center py-8 text-muted-foreground">
                      No incidents found matching your criteria
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredIncidents.map((incident) => (
                    <TableRow key={incident.id} className="hover:bg-muted/50">
                      <TableCell className="font-medium font-mono text-xs">
                        {incident.id}
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          {getTypeIcon(incident.type)}
                          <span className="text-sm">{incident.type}</span>
                        </div>
                      </TableCell>
                      <TableCell className="font-medium">{incident.entityName}</TableCell>
                      <TableCell>
                        <Badge variant="outline">{incident.zone.replace("Zone ", "")}</Badge>
                      </TableCell>
                      <TableCell className="max-w-xs">
                        <p className="text-sm truncate" title={incident.description}>
                          {incident.description}
                        </p>
                      </TableCell>
                      <TableCell className="text-sm text-muted-foreground">
                        {incident.detectedBy}
                      </TableCell>
                      <TableCell className="text-sm whitespace-nowrap">
                        {incident.detectionTime}
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <div className="flex items-center gap-1">
                            <span className={cn("text-sm font-medium", getSeverityColor(incident.severity))}>
                              {incident.severity}/10
                            </span>
                          </div>
                          <div className="h-1.5 w-16 bg-secondary rounded-full overflow-hidden">
                            <div
                              className={cn("h-full", getSeverityBg(incident.severity))}
                              style={{ width: `${incident.severity * 10}%` }}
                            />
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>{getStatusBadge(incident.status)}</TableCell>
                      <TableCell>
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => handleViewDetails(incident)}
                          >
                            <Eye className="mr-1 h-3 w-3" />
                            Details
                          </Button>
                          {incident.status !== "Resolved" && (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleMarkResolved(incident)}
                            >
                              <CheckCircle className="mr-1 h-3 w-3" />
                              Resolve
                            </Button>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </div>
      </Container>

      {/* View Details Dialog */}
      <Dialog open={detailsDialogOpen} onOpenChange={setDetailsDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Incident Details</DialogTitle>
            <DialogDescription>
              Comprehensive information about the detected incident
            </DialogDescription>
          </DialogHeader>

          <div className="max-h-[60vh] overflow-y-auto pr-2">
            {selectedIncident && (
              <div className="space-y-4">
                {/* Header Info */}
                <div className="rounded-md border bg-muted/50 p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <p className="text-sm text-muted-foreground">Incident ID</p>
                      <p className="font-mono font-medium">{selectedIncident.id}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      {getTypeIcon(selectedIncident.type)}
                      {getStatusBadge(selectedIncident.status)}
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-muted-foreground">Type</p>
                      <p className="font-medium">{selectedIncident.type}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Entity</p>
                      <p className="font-medium">{selectedIncident.entityName}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Zone</p>
                      <p className="font-medium">{selectedIncident.zone}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Detection Time</p>
                      <p className="font-medium">{selectedIncident.detectionTime}</p>
                    </div>
                  </div>
                </div>

                {/* Description */}
                <div className="rounded-md border bg-muted/50 p-4">
                  <h4 className="mb-2 font-medium">Incident Description</h4>
                  <p className="text-sm">{selectedIncident.description}</p>
                </div>

                {/* Detection Info */}
                <div className="rounded-md border bg-muted/50 p-4">
                  <h4 className="mb-3 font-medium">Detection Information</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Detected By:</span>
                      <span className="font-medium">{selectedIncident.detectedBy}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Severity Score:</span>
                      <span className={cn("font-medium", getSeverityColor(selectedIncident.severity))}>
                        {selectedIncident.severity}/10
                      </span>
                    </div>
                    <div className="mt-2">
                      <div className="h-2 w-full bg-secondary rounded-full overflow-hidden">
                        <div
                          className={cn("h-full transition-all", getSeverityBg(selectedIncident.severity))}
                          style={{ width: `${selectedIncident.severity * 10}%` }}
                        />
                      </div>
                    </div>
                  </div>
                </div>

                {/* Related Data */}
                {selectedIncident.relatedData && (
                  <div className="rounded-md border bg-muted/50 p-4">
                    <h4 className="mb-3 font-medium">Related Data</h4>
                    <div className="grid grid-cols-2 gap-3">
                      {selectedIncident.relatedData.machinePerformance !== undefined && (
                        <div>
                          <p className="text-sm text-muted-foreground">Performance</p>
                          <p className="font-medium">{selectedIncident.relatedData.machinePerformance}%</p>
                        </div>
                      )}
                      {selectedIncident.relatedData.temperature !== undefined && (
                        <div>
                          <p className="text-sm text-muted-foreground">Temperature</p>
                          <p className="font-medium">{selectedIncident.relatedData.temperature}°C</p>
                        </div>
                      )}
                      {selectedIncident.relatedData.ppeCompliance !== undefined && (
                        <div>
                          <p className="text-sm text-muted-foreground">PPE Status</p>
                          <p className="font-medium">{selectedIncident.relatedData.ppeCompliance}</p>
                        </div>
                      )}
                      {selectedIncident.relatedData.confidence !== undefined && (
                        <div>
                          <p className="text-sm text-muted-foreground">Confidence</p>
                          <p className="font-medium">{selectedIncident.relatedData.confidence}%</p>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Alert for Critical Status */}
                {selectedIncident.status === "Critical" && (
                  <div className="rounded-md border border-red-500 bg-red-500/10 p-4">
                    <h4 className="mb-2 font-medium text-red-600 dark:text-red-500 flex items-center gap-2">
                      <AlertTriangle className="h-4 w-4" />
                      Critical Priority
                    </h4>
                    <p className="text-sm text-muted-foreground">
                      This incident requires immediate attention. Please address this issue as soon
                      as possible to ensure safety and operational continuity.
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>

          <DialogFooter>
            {selectedIncident?.status !== "Resolved" && (
              <Button
                onClick={() => {
                  if (selectedIncident) handleMarkResolved(selectedIncident);
                  setDetailsDialogOpen(false);
                }}
                className="text-white"
              >
                <CheckCircle className="mr-2 h-4 w-4" />
                Mark as Resolved
              </Button>
            )}
            <Button variant="outline" onClick={() => setDetailsDialogOpen(false)}>
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
