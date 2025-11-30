"use client";

import { useState } from "react";
import { Plus, FileText, Calendar } from "lucide-react";
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
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useToast } from "@/components/ui/use-toast";
import {
  maintenanceLogsData,
  timelineEvents,
  type MaintenanceLog,
  type TimelineEvent,
} from "@/data/maintenance";
import { cn } from "@/lib/utils";

export default function MaintenanceHistoryPage() {
  const [logs, setLogs] = useState<MaintenanceLog[]>(maintenanceLogsData);
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [selectedLog, setSelectedLog] = useState<MaintenanceLog | null>(null);
  const [reportDialogOpen, setReportDialogOpen] = useState(false);
  const { toast } = useToast();

  // Form state for new maintenance
  const [newMaintenance, setNewMaintenance] = useState({
    component: "",
    technician: "",
    description: "",
    date: "",
    status: "Pending" as MaintenanceLog["status"],
  });

  const handleAddMaintenance = () => {
    const newLog: MaintenanceLog = {
      id: `M${String(logs.length + 1).padStart(3, "0")}`,
      component: newMaintenance.component,
      technician: newMaintenance.technician,
      description: newMaintenance.description,
      status: newMaintenance.status,
      timestamp: newMaintenance.date || new Date().toLocaleString(),
    };

    setLogs([newLog, ...logs]);
    setAddDialogOpen(false);
    setNewMaintenance({
      component: "",
      technician: "",
      description: "",
      date: "",
      status: "Pending",
    });

    toast({
      title: "Maintenance Added",
      description: "New maintenance entry has been created successfully.",
    });
  };

  const handleViewReport = (log: MaintenanceLog) => {
    setSelectedLog(log);
    setReportDialogOpen(true);
  };

  const getStatusBadge = (status: MaintenanceLog["status"]) => {
    switch (status) {
      case "Completed":
        return <Badge variant="success">Completed</Badge>;
      case "Pending":
        return <Badge variant="warning">Pending</Badge>;
      case "In Progress":
        return <Badge variant="default" className="text-white">In Progress</Badge>;
    }
  };

  const getTimelineIcon = (type: TimelineEvent["type"]) => {
    switch (type) {
      case "completed":
        return "bg-green-500";
      case "incident":
        return "bg-red-500";
      case "scheduled":
        return "bg-blue-500";
    }
  };

  return (
    <div className="p-4">
      <Container className="mx-auto max-w-7xl">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Maintenance History</h1>
            <p className="text-muted-foreground">
              Track and manage system maintenance activities
            </p>
          </div>
          <Button onClick={() => setAddDialogOpen(true)} className="text-white">
            <Plus className="mr-2 h-4 w-4 text-white" />
            Add Maintenance
          </Button>
        </div>

        <div className="space-y-6">
          {/* Horizontal Timeline Section */}
          <div className="w-full">
            <div className="rounded-lg border bg-card p-6 shadow-sm">
              <h2 className="mb-8 flex items-center text-xl font-semibold">
                <Calendar className="mr-2 h-5 w-5" />
                Timeline
              </h2>

              {/* Horizontal Timeline Container */}
              <div className="relative overflow-x-auto py-8">
                <div className="flex min-w-max justify-between gap-4 px-8">
                  {timelineEvents.map((event, index) => (
                    <div
                      key={event.id}
                      className="relative flex flex-col items-center"
                      style={{ minWidth: "200px" }}
                    >
                      {/* Event Content Above Node */}
                      <div className="mb-6 text-center">
                        <p className="mb-2 text-xs font-medium text-primary">
                          {event.date}
                        </p>
                        <p className="mb-2 text-sm font-semibold leading-tight">
                          {event.title}
                        </p>
                        <p className="text-xs leading-relaxed text-muted-foreground">
                          {event.description}
                        </p>
                      </div>

                      {/* Timeline Node and Line */}
                      <div className="relative flex items-center">
                        {/* Connecting Line Before */}
                        {index !== 0 && (
                          <div className="absolute right-1/2 h-0.5 w-24 bg-border" />
                        )}

                        {/* Node Circle */}
                        <div
                          className={cn(
                            "relative z-10 h-5 w-5 rounded-full ring-4 ring-background transition-transform hover:scale-110",
                            getTimelineIcon(event.type)
                          )}
                        />

                        {/* Connecting Line After */}
                        {index !== timelineEvents.length - 1 && (
                          <div className="absolute left-1/2 h-0.5 w-24 bg-border" />
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Maintenance Log Table */}
          <div className="w-full">
            <div className="rounded-lg border bg-card shadow-sm">
              <div className="border-b p-4">
                <h2 className="text-xl font-semibold">Maintenance Logs</h2>
              </div>

              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>ID</TableHead>
                      <TableHead>Component</TableHead>
                      <TableHead>Technician</TableHead>
                      <TableHead>Description</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Timestamp</TableHead>
                      <TableHead>Action</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {logs.map((log) => (
                      <TableRow key={log.id}>
                        <TableCell className="font-medium">{log.id}</TableCell>
                        <TableCell>{log.component}</TableCell>
                        <TableCell>{log.technician}</TableCell>
                        <TableCell className="max-w-xs truncate">
                          {log.description}
                        </TableCell>
                        <TableCell>{getStatusBadge(log.status)}</TableCell>
                        <TableCell className="text-sm text-muted-foreground">
                          {log.timestamp}
                        </TableCell>
                        <TableCell>
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => handleViewReport(log)}
                          >
                            <FileText className="mr-1 h-3 w-3" />
                            View
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </div>
          </div>
        </div>
      </Container>

      {/* Add Maintenance Dialog */}
      <Dialog open={addDialogOpen} onOpenChange={setAddDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add New Maintenance</DialogTitle>
            <DialogDescription>
              Create a new maintenance entry for system components.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="component">Component</Label>
              <Input
                id="component"
                placeholder="e.g., Camera Unit A3"
                value={newMaintenance.component}
                onChange={(e) =>
                  setNewMaintenance({
                    ...newMaintenance,
                    component: e.target.value,
                  })
                }
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="technician">Technician</Label>
              <Input
                id="technician"
                placeholder="e.g., John Smith"
                value={newMaintenance.technician}
                onChange={(e) =>
                  setNewMaintenance({
                    ...newMaintenance,
                    technician: e.target.value,
                  })
                }
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                placeholder="Describe the maintenance work..."
                value={newMaintenance.description}
                onChange={(e) =>
                  setNewMaintenance({
                    ...newMaintenance,
                    description: e.target.value,
                  })
                }
                rows={3}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="date">Maintenance Date</Label>
              <Input
                id="date"
                type="datetime-local"
                value={newMaintenance.date}
                onChange={(e) =>
                  setNewMaintenance({ ...newMaintenance, date: e.target.value })
                }
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="status">Status</Label>
              <Select
                value={newMaintenance.status}
                onValueChange={(value: MaintenanceLog["status"]) =>
                  setNewMaintenance({ ...newMaintenance, status: value })
                }
              >
                <SelectTrigger id="status">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Pending">Pending</SelectItem>
                  <SelectItem value="In Progress">In Progress</SelectItem>
                  <SelectItem value="Completed">Completed</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setAddDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleAddMaintenance} className="text-white">Add Maintenance</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* View Report Dialog */}
      <Dialog open={reportDialogOpen} onOpenChange={setReportDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Maintenance Report</DialogTitle>
            <DialogDescription>
              Detailed information about this maintenance entry
            </DialogDescription>
          </DialogHeader>

          {selectedLog && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">Maintenance ID</p>
                  <p className="font-medium">{selectedLog.id}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Status</p>
                  {getStatusBadge(selectedLog.status)}
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Component</p>
                  <p className="font-medium">{selectedLog.component}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Technician</p>
                  <p className="font-medium">{selectedLog.technician}</p>
                </div>
                <div className="col-span-2">
                  <p className="text-sm text-muted-foreground">Timestamp</p>
                  <p className="font-medium">{selectedLog.timestamp}</p>
                </div>
              </div>

              <div className="space-y-2">
                <p className="text-sm text-muted-foreground">Description</p>
                <div className="rounded-md border bg-muted/50 p-4">
                  <p className="text-sm">{selectedLog.description}</p>
                </div>
              </div>

              <div className="rounded-md border bg-muted/50 p-4">
                <h4 className="mb-2 font-medium">Additional Notes</h4>
                <p className="text-sm text-muted-foreground">
                  No additional notes available for this maintenance entry.
                </p>
              </div>
            </div>
          )}

          <DialogFooter>
            <Button onClick={() => setReportDialogOpen(false)} className="text-white">Close</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
