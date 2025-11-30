"use client";

import { useState } from "react";
import { Bell, Eye, Search, Settings, TrendingUp, Thermometer, Activity } from "lucide-react";
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
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { machinesData, machinesOverview, type Machine } from "@/data/machines-status";
import { useToast } from "@/components/ui/use-toast";
import { chartTitle } from "@/components/primitives";
import { cn } from "@/lib/utils";

export default function MachinesStatusPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedMachine, setSelectedMachine] = useState<Machine | null>(null);
  const [alertDialogOpen, setAlertDialogOpen] = useState(false);
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false);
  const [alertMessage, setAlertMessage] = useState("");
  const { toast } = useToast();

  const filteredMachines = machinesData.filter(
    (machine) =>
      machine.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      machine.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      machine.zone.toLowerCase().includes(searchQuery.toLowerCase()) ||
      machine.machineType.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleSendAlert = (machine: Machine) => {
    setSelectedMachine(machine);
    setAlertMessage(
      `URGENT: Machine ${machine.name} (${machine.id}) in ${machine.zone} requires immediate attention. Current status: ${machine.status}. Performance: ${machine.performance}%. Please dispatch maintenance team.`
    );
    setAlertDialogOpen(true);
  };

  const handleViewDetails = (machine: Machine) => {
    setSelectedMachine(machine);
    setDetailsDialogOpen(true);
  };

  const confirmSendAlert = () => {
    if (selectedMachine) {
      toast({
        title: "Alert Sent Successfully",
        description: `Maintenance alert sent for ${selectedMachine.name} to operations team`,
      });
      setAlertDialogOpen(false);
    }
  };

  const getStatusBadge = (status: Machine["status"]) => {
    switch (status) {
      case "Operational":
        return <Badge variant="success">Operational</Badge>;
      case "Faulty":
        return <Badge variant="danger">Faulty</Badge>;
      case "Maintenance Pending":
        return <Badge variant="warning">Maintenance Pending</Badge>;
    }
  };

  const getTemperatureColor = (temp: number) => {
    if (temp < 75) return "text-green-600 dark:text-green-500";
    if (temp < 90) return "text-yellow-600 dark:text-yellow-500";
    return "text-red-600 dark:text-red-500";
  };


const getMachineIcon = (_type: Machine["machineType"]) => {
  return <Settings className="h-4 w-4 text-muted-foreground" />;
};



  return (
    <div>
      {/* Overview Cards */}
      <div className="grid grid-cols-1 gap-4 border-b border-border p-4 tablet:grid-cols-2 laptop:grid-cols-4">
        <Container className="rounded-lg border bg-card p-6 shadow-sm">
          <h2 className={cn(chartTitle({ color: "mute", size: "sm" }), "mb-1")}>
            Total Machines
          </h2>
          <p className="text-3xl font-bold text-primary">
            {machinesOverview.totalMachines}
          </p>
        </Container>

        <Container className="rounded-lg border bg-card p-6 shadow-sm">
          <h2 className={cn(chartTitle({ color: "mute", size: "sm" }), "mb-1")}>
            Operational Machines
          </h2>
          <p className="text-3xl font-bold text-green-600 dark:text-green-500">
            {machinesOverview.operationalMachines}
          </p>
        </Container>

        <Container className="rounded-lg border bg-card p-6 shadow-sm">
          <h2 className={cn(chartTitle({ color: "mute", size: "sm" }), "mb-1")}>
            Faulty Machines
          </h2>
          <p className="text-3xl font-bold text-red-600 dark:text-red-500">
            {machinesOverview.faultyMachines}
          </p>
        </Container>

        <Container className="rounded-lg border bg-card p-6 shadow-sm">
          <h2 className={cn(chartTitle({ color: "mute", size: "sm" }), "mb-1")}>
            Last Maintenance Check
          </h2>
          <p className="text-lg font-medium text-foreground">
            {machinesOverview.lastMaintenanceCheck}
          </p>
        </Container>
      </div>

      {/* Machines Table */}
      <Container className="p-4">
        <div className="rounded-lg border bg-card shadow-sm">
          <div className="border-b p-4">
            <h2 className="mb-4 text-xl font-semibold">Machines Status Overview</h2>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Search by machine ID, name, zone, or type..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>

          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Machine ID</TableHead>
                  <TableHead>Machine Name</TableHead>
                  <TableHead>Zone / Department</TableHead>
                  <TableHead>Machine Status</TableHead>
                  <TableHead>Performance %</TableHead>
                  <TableHead>Temperature</TableHead>
                  <TableHead>Last Checked</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredMachines.map((machine) => (
                  <TableRow key={machine.id}>
                    <TableCell className="font-medium">{machine.id}</TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        {getMachineIcon(machine.machineType)}
                        <div>
                          <div className="font-medium">{machine.name}</div>
                          <div className="text-xs text-muted-foreground">
                            {machine.machineType}
                          </div>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>{machine.zone}</TableCell>
                    <TableCell>{getStatusBadge(machine.status)}</TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <span className="min-w-[3ch] text-sm">{machine.performance}%</span>
                        <div className="h-2 w-20 overflow-hidden rounded-full bg-secondary">
                          <div
                            className={cn(
                              "h-full transition-all",
                              machine.performance >= 90
                                ? "bg-green-600 dark:bg-green-500"
                                : machine.performance >= 70
                                  ? "bg-yellow-600 dark:bg-yellow-500"
                                  : "bg-red-600 dark:bg-red-500"
                            )}
                            style={{ width: `${machine.performance}%` }}
                          />
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-1">
                        <Thermometer className={cn("h-4 w-4", getTemperatureColor(machine.temperature))} />
                        <span className={cn("text-sm font-medium", getTemperatureColor(machine.temperature))}>
                          {machine.temperature}°C
                        </span>
                      </div>
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {machine.lastChecked}
                    </TableCell>
                    <TableCell>
                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleSendAlert(machine)}
                        >
                          <Bell className="mr-1 h-3 w-3" />
                          Alert
                        </Button>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleViewDetails(machine)}
                        >
                          <Eye className="mr-1 h-3 w-3" />
                          Details
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </div>
      </Container>

      {/* Send Alert Dialog */}
      <Dialog open={alertDialogOpen} onOpenChange={setAlertDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Send Machine Alert</DialogTitle>
            <DialogDescription>
              Send an alert notification to the maintenance operations team.
            </DialogDescription>
          </DialogHeader>

          {selectedMachine && (
            <div className="space-y-4">
              <div className="rounded-md border bg-muted/50 p-4">
                <div className="mb-2 flex items-center justify-between">
                  <span className="text-sm font-medium">Machine Info</span>
                  {getStatusBadge(selectedMachine.status)}
                </div>
                <p className="text-sm">
                  <strong>ID:</strong> {selectedMachine.id}
                </p>
                <p className="text-sm">
                  <strong>Name:</strong> {selectedMachine.name}
                </p>
                <p className="text-sm">
                  <strong>Type:</strong> {selectedMachine.machineType}
                </p>
                <p className="text-sm">
                  <strong>Zone:</strong> {selectedMachine.zone}
                </p>
                <p className="text-sm">
                  <strong>Performance:</strong> {selectedMachine.performance}%
                </p>
                <p className="text-sm">
                  <strong>Temperature:</strong>{" "}
                  <span className={getTemperatureColor(selectedMachine.temperature)}>
                    {selectedMachine.temperature}°C
                  </span>
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="alert-message">Alert Message</Label>
                <Textarea
                  id="alert-message"
                  value={alertMessage}
                  onChange={(e) => setAlertMessage(e.target.value)}
                  rows={4}
                />
              </div>
            </div>
          )}

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setAlertDialogOpen(false)}
            >
              Cancel
            </Button>
            <Button onClick={confirmSendAlert} className="text-white">
              <Bell className="mr-2 h-4 w-4" />
              Send Alert
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* View Details Dialog */}
      <Dialog open={detailsDialogOpen} onOpenChange={setDetailsDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Machine Details</DialogTitle>
            <DialogDescription>
              Comprehensive information about machine performance and status
            </DialogDescription>
          </DialogHeader>

          <div className="max-h-[60vh] overflow-y-auto pr-2">
            {selectedMachine && (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-muted-foreground">Machine ID</p>
                    <p className="font-medium">{selectedMachine.id}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Machine Name</p>
                    <p className="font-medium">{selectedMachine.name}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Machine Type</p>
                    <p className="font-medium">{selectedMachine.machineType}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Zone</p>
                    <p className="font-medium">{selectedMachine.zone}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Status</p>
                    {getStatusBadge(selectedMachine.status)}
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Performance</p>
                    <div className="flex items-center gap-2">
                      <p className="font-medium">{selectedMachine.performance}%</p>
                      <Activity className="h-4 w-4 text-muted-foreground" />
                    </div>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Temperature</p>
                    <div className="flex items-center gap-1">
                      <Thermometer className={cn("h-4 w-4", getTemperatureColor(selectedMachine.temperature))} />
                      <p className={cn("font-medium", getTemperatureColor(selectedMachine.temperature))}>
                        {selectedMachine.temperature}°C
                      </p>
                    </div>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Last Checked</p>
                    <p className="font-medium">{selectedMachine.lastChecked}</p>
                  </div>
                </div>

                <div className="rounded-md border bg-muted/50 p-4">
                  <h4 className="mb-3 font-medium flex items-center gap-2">
                    <TrendingUp className="h-4 w-4" />
                    Performance Metrics
                  </h4>
                  <div className="space-y-3">
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>Overall Performance</span>
                        <span className="font-medium">{selectedMachine.performance}%</span>
                      </div>
                      <div className="h-2 w-full overflow-hidden rounded-full bg-secondary">
                        <div
                          className={cn(
                            "h-full transition-all",
                            selectedMachine.performance >= 90
                              ? "bg-green-600 dark:bg-green-500"
                              : selectedMachine.performance >= 70
                                ? "bg-yellow-600 dark:bg-yellow-500"
                                : "bg-red-600 dark:bg-red-500"
                          )}
                          style={{ width: `${selectedMachine.performance}%` }}
                        />
                      </div>
                    </div>
                    
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>Temperature Status</span>
                        <span className={cn("font-medium", getTemperatureColor(selectedMachine.temperature))}>
                          {selectedMachine.temperature < 75 ? "Normal" : selectedMachine.temperature < 90 ? "Elevated" : "Critical"}
                        </span>
                      </div>
                      <div className="h-2 w-full overflow-hidden rounded-full bg-secondary">
                        <div
                          className={cn(
                            "h-full transition-all",
                            getTemperatureColor(selectedMachine.temperature).includes("green")
                              ? "bg-green-600 dark:bg-green-500"
                              : getTemperatureColor(selectedMachine.temperature).includes("yellow")
                                ? "bg-yellow-600 dark:bg-yellow-500"
                                : "bg-red-600 dark:bg-red-500"
                          )}
                          style={{ width: `${Math.min((selectedMachine.temperature / 120) * 100, 100)}%` }}
                        />
                      </div>
                    </div>
                  </div>
                </div>

                <div className="rounded-md border bg-muted/50 p-4">
                  <h4 className="mb-2 font-medium">Maintenance Information</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span>Next Maintenance Due:</span>
                      <span className={cn(
                        "font-medium",
                        selectedMachine.maintenanceDueIn <= 3
                          ? "text-red-600 dark:text-red-500"
                          : selectedMachine.maintenanceDueIn <= 7
                            ? "text-yellow-600 dark:text-yellow-500"
                            : "text-green-600 dark:text-green-500"
                      )}>
                        {selectedMachine.maintenanceDueIn === 0 
                          ? "Overdue" 
                          : `${selectedMachine.maintenanceDueIn} days`}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>Operational Hours (Today):</span>
                      <span className="font-medium">
                        {selectedMachine.status === "Operational" ? "8.5 hrs" : "0 hrs"}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>Last Service Date:</span>
                      <span className="font-medium">2025-11-15</span>
                    </div>
                  </div>
                </div>

                {selectedMachine.status === "Faulty" && (
                  <div className="rounded-md border border-red-500 bg-red-500/10 p-4">
                    <h4 className="mb-2 font-medium text-red-600 dark:text-red-500">
                      ⚠️ Issue Detected
                    </h4>
                    <p className="text-sm text-muted-foreground">
                      Machine requires immediate attention. Performance is below acceptable
                      threshold. Maintenance team has been notified.
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>

          <DialogFooter>
            <Button onClick={() => setDetailsDialogOpen(false)} className="text-white">
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
