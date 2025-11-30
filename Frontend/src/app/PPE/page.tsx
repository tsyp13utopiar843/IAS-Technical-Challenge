"use client";

import { useState } from "react";
import { Phone, Eye, Search } from "lucide-react";
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
import { workersData, ppeOverview, type Worker } from "@/data/ppe-status";
import { useToast } from "@/components/ui/use-toast";
import { chartTitle } from "@/components/primitives";
import { cn } from "@/lib/utils";

export default function PPEStatusPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedWorker, setSelectedWorker] = useState<Worker | null>(null);
  const [alertDialogOpen, setAlertDialogOpen] = useState(false);
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false);
  const [alertMessage, setAlertMessage] = useState("");
  const { toast } = useToast();

  const filteredWorkers = workersData.filter(
    (worker) =>
      worker.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      worker.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      worker.zone.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleSendAlert = (worker: Worker) => {
    setSelectedWorker(worker);
    setAlertMessage(
      `ALERT: ${worker.name}, your PPE status is ${worker.ppeStatus}. Please ensure all safety equipment is properly worn. This is a mandatory safety requirement.`
    );
    setAlertDialogOpen(true);
  };

  const handleViewDetails = (worker: Worker) => {
    setSelectedWorker(worker);
    setDetailsDialogOpen(true);
  };

  const confirmSendAlert = () => {
    if (selectedWorker) {
      // Simulate Twilio API call
      toast({
        title: "Alert Sent Successfully",
        description: `SMS alert sent to ${selectedWorker.name} at ${selectedWorker.phone}`,
      });
      setAlertDialogOpen(false);
    }
  };

  const getStatusBadge = (status: Worker["ppeStatus"]) => {
    switch (status) {
      case "Compliant":
        return <Badge variant="success">Compliant</Badge>;
      case "Non-Compliant":
        return <Badge variant="danger">Non-Compliant</Badge>;
      case "Warning":
        return <Badge variant="warning">Warning</Badge>;
    }
  };

  return (
    <div>
      {/* Overview Cards */}
      <div className="grid grid-cols-1 gap-4 border-b border-border p-4 tablet:grid-cols-2 laptop:grid-cols-4">
        <Container className="rounded-lg border bg-card p-6 shadow-sm">
          <h2 className={cn(chartTitle({ color: "mute", size: "sm" }), "mb-1")}>
            Total Workers
          </h2>
          <p className="text-3xl font-bold text-primary">
            {ppeOverview.totalWorkers}
          </p>
        </Container>

        <Container className="rounded-lg border bg-card p-6 shadow-sm">
          <h2 className={cn(chartTitle({ color: "mute", size: "sm" }), "mb-1")}>
            Compliant Workers
          </h2>
          <p className="text-3xl font-bold text-green-600 dark:text-green-500">
            {ppeOverview.compliantWorkers}
          </p>
        </Container>

        <Container className="rounded-lg border bg-card p-6 shadow-sm">
          <h2 className={cn(chartTitle({ color: "mute", size: "sm" }), "mb-1")}>
            Non-Compliant Workers
          </h2>
          <p className="text-3xl font-bold text-red-600 dark:text-red-500">
            {ppeOverview.nonCompliantWorkers}
          </p>
        </Container>

        <Container className="rounded-lg border bg-card p-6 shadow-sm">
          <h2 className={cn(chartTitle({ color: "mute", size: "sm" }), "mb-1")}>
            Last Alert Sent
          </h2>
          <p className="text-lg font-medium text-foreground">
            {ppeOverview.lastAlertSent}
          </p>
        </Container>
      </div>

      {/* Workers Table */}
      <Container className="p-4">
        <div className="rounded-lg border bg-card shadow-sm">
          <div className="border-b p-4">
            <h2 className="mb-4 text-xl font-semibold">Workers PPE Status</h2>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Search by worker ID, name, or zone..."
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
                  <TableHead>Worker ID</TableHead>
                  <TableHead>Worker Name</TableHead>
                  <TableHead>Zone</TableHead>
                  <TableHead>PPE Status</TableHead>
                  <TableHead>Confidence %</TableHead>
                  <TableHead>Last Updated</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredWorkers.map((worker) => (
                  <TableRow key={worker.id}>
                    <TableCell className="font-medium">{worker.id}</TableCell>
                    <TableCell>{worker.name}</TableCell>
                    <TableCell>{worker.zone}</TableCell>
                    <TableCell>{getStatusBadge(worker.ppeStatus)}</TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <span>{worker.confidence}%</span>
                        <div className="h-2 w-20 overflow-hidden rounded-full bg-secondary">
                          <div
                            className="h-full bg-primary"
                            style={{ width: `${worker.confidence}%` }}
                          />
                        </div>
                      </div>
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {worker.lastUpdated}
                    </TableCell>
                    <TableCell>
                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleSendAlert(worker)}
                        >
                          <Phone className="mr-1 h-3 w-3" />
                          Alert
                        </Button>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleViewDetails(worker)}
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
            <DialogTitle>Send PPE Alert</DialogTitle>
            <DialogDescription>
              Send an SMS alert to the worker via Twilio messaging service.
            </DialogDescription>
          </DialogHeader>

          {selectedWorker && (
            <div className="space-y-4">
              <div className="rounded-md border bg-muted/50 p-4">
                <div className="mb-2 flex items-center justify-between">
                  <span className="text-sm font-medium">Worker Info</span>
                  {getStatusBadge(selectedWorker.ppeStatus)}
                </div>
                <p className="text-sm">
                  <strong>ID:</strong> {selectedWorker.id}
                </p>
                <p className="text-sm">
                  <strong>Name:</strong> {selectedWorker.name}
                </p>
                <p className="text-sm">
                  <strong>Zone:</strong> {selectedWorker.zone}
                </p>
                <p className="text-sm">
                  <strong>Phone:</strong> {selectedWorker.phone}
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
              <Phone className="mr-2 h-4 w-4" />
              Send Alert
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* View Details Dialog */}
      <Dialog open={detailsDialogOpen} onOpenChange={setDetailsDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Worker Details</DialogTitle>
            <DialogDescription>
              Detailed information about worker PPE compliance
            </DialogDescription>
          </DialogHeader>

          {selectedWorker && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">Worker ID</p>
                  <p className="font-medium">{selectedWorker.id}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Name</p>
                  <p className="font-medium">{selectedWorker.name}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Zone</p>
                  <p className="font-medium">{selectedWorker.zone}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Status</p>
                  {getStatusBadge(selectedWorker.ppeStatus)}
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">
                    Confidence Level
                  </p>
                  <p className="font-medium">{selectedWorker.confidence}%</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Last Updated</p>
                  <p className="font-medium">{selectedWorker.lastUpdated}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Phone</p>
                  <p className="font-medium">{selectedWorker.phone}</p>
                </div>
              </div>

              <div className="rounded-md border bg-muted/50 p-4">
                <h4 className="mb-2 font-medium">Detection Details</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span>Helmet Detection:</span>
                    <span className="font-medium text-green-600">✓ Detected</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Gloves Detection:</span>
                    <span className="font-medium text-green-600">✓ Detected</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Boots Detection:</span>
                    <span className={selectedWorker.ppeStatus === "Compliant" ? "font-medium text-green-600" : "font-medium text-red-600"}>
                      {selectedWorker.ppeStatus === "Compliant" ? "✓ Detected" : "✗ Not Detected"}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}

          <DialogFooter>
            <Button onClick={() => setDetailsDialogOpen(false)} className="text-white">Close</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

