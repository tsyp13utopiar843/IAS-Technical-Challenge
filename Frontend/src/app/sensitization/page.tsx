"use client";

import { useState } from "react";
import { Save, RotateCcw } from "lucide-react";
import Container from "@/components/container";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useToast } from "@/components/ui/use-toast";
import { defaultSettings, type SensitizationSettings } from "@/data/sensitization";

export default function SensitizationPage() {
  const [settings, setSettings] = useState<SensitizationSettings>(defaultSettings);
  const { toast } = useToast();

  const handleSave = () => {
    // Simulate saving settings to backend
    toast({
      title: "Settings Saved",
      description: "Your detection parameters have been updated successfully.",
    });
  };

  const handleReset = () => {
    setSettings(defaultSettings);
    toast({
      title: "Settings Reset",
      description: "All parameters have been reset to default values.",
    });
  };

  return (
    <div className="p-4">
      <Container className="mx-auto max-w-4xl">
        <div className="mb-6">
          <h1 className="text-3xl font-bold">Sensitization Settings</h1>
          <p className="text-muted-foreground">
            Configure agent detection sensitivity and alert parameters
          </p>
        </div>

        {/* Settings Cards */}
        <div className="space-y-6">
          {/* Detection Thresholds Card */}
          <div className="rounded-lg border bg-card p-6 shadow-sm">
            <h2 className="mb-4 text-xl font-semibold">Detection Thresholds</h2>
            <p className="mb-6 text-sm text-muted-foreground">
              Adjust the confidence threshold for each PPE detection category. Higher values require more confidence before marking as detected.
            </p>

            <div className="space-y-6">
              {/* Helmet Threshold */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="helmet-threshold">Helmet Detection Threshold</Label>
                  <span className="text-sm font-medium text-primary">
                    {settings.helmetThreshold}%
                  </span>
                </div>
                <Slider
                  id="helmet-threshold"
                  min={50}
                  max={100}
                  step={5}
                  value={[settings.helmetThreshold]}
                  onValueChange={(value) =>
                    setSettings({ ...settings, helmetThreshold: value[0] })
                  }
                  className="w-full"
                />
              </div>

              {/* Glove Threshold */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="glove-threshold">Glove Detection Threshold</Label>
                  <span className="text-sm font-medium text-primary">
                    {settings.gloveThreshold}%
                  </span>
                </div>
                <Slider
                  id="glove-threshold"
                  min={50}
                  max={100}
                  step={5}
                  value={[settings.gloveThreshold]}
                  onValueChange={(value) =>
                    setSettings({ ...settings, gloveThreshold: value[0] })
                  }
                  className="w-full"
                />
              </div>

              {/* Boot Threshold */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="boot-threshold">Boot Detection Threshold</Label>
                  <span className="text-sm font-medium text-primary">
                    {settings.bootThreshold}%
                  </span>
                </div>
                <Slider
                  id="boot-threshold"
                  min={50}
                  max={100}
                  step={5}
                  value={[settings.bootThreshold]}
                  onValueChange={(value) =>
                    setSettings({ ...settings, bootThreshold: value[0] })
                  }
                  className="w-full"
                />
              </div>
            </div>
          </div>

          {/* Alert Configuration Card */}
          <div className="rounded-lg border bg-card p-6 shadow-sm">
            <h2 className="mb-4 text-xl font-semibold">Alert Configuration</h2>
            <p className="mb-6 text-sm text-muted-foreground">
              Configure how and when alerts are sent to workers and supervisors.
            </p>

            <div className="space-y-6">
              {/* Alert Delay */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="alert-delay">Alert Delay (seconds)</Label>
                    <p className="text-xs text-muted-foreground">
                      Delay before sending alert after detection
                    </p>
                  </div>
                  <span className="text-sm font-medium text-primary">
                    {settings.alertDelay}s
                  </span>
                </div>
                <Slider
                  id="alert-delay"
                  min={0}
                  max={30}
                  step={1}
                  value={[settings.alertDelay]}
                  onValueChange={(value) =>
                    setSettings({ ...settings, alertDelay: value[0] })
                  }
                  className="w-full"
                />
              </div>

              {/* Allow Notifications */}
              <div className="flex items-center justify-between rounded-md border p-4">
                <div className="space-y-0.5">
                  <Label htmlFor="notifications">Allow Notifications</Label>
                  <p className="text-xs text-muted-foreground">
                    Enable SMS and push notifications for alerts
                  </p>
                </div>
                <Switch
                  id="notifications"
                  checked={settings.allowNotifications}
                  onCheckedChange={(checked) =>
                    setSettings({ ...settings, allowNotifications: checked })
                  }
                />
              </div>

              {/* Auto-Escalation Level */}
              <div className="space-y-2">
                <Label htmlFor="escalation">Auto-Escalation Level</Label>
                <p className="text-xs text-muted-foreground">
                  Who should receive escalated alerts for repeated violations
                </p>
                <Select
                  value={settings.autoEscalationLevel}
                  onValueChange={(value) =>
                    setSettings({ ...settings, autoEscalationLevel: value })
                  }
                >
                  <SelectTrigger id="escalation">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="worker">Worker Only</SelectItem>
                    <SelectItem value="supervisor">Supervisor</SelectItem>
                    <SelectItem value="manager">Manager</SelectItem>
                    <SelectItem value="safety-officer">Safety Officer</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Incident Logging */}
              <div className="flex items-center justify-between rounded-md border p-4">
                <div className="space-y-0.5">
                  <Label htmlFor="logging">Incident Logging</Label>
                  <p className="text-xs text-muted-foreground">
                    Record all PPE violations to the database
                  </p>
                </div>
                <Switch
                  id="logging"
                  checked={settings.incidentLogging}
                  onCheckedChange={(checked) =>
                    setSettings({ ...settings, incidentLogging: checked })
                  }
                />
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex justify-end gap-3">
            <Button variant="outline" onClick={handleReset}>
              <RotateCcw className="mr-2 h-4 w-4" />
              Reset to Default
            </Button>
            <Button onClick={handleSave} className="text-white">
              <Save className="mr-2 h-4 w-4" />
              Save Configuration
            </Button>
          </div>
        </div>
      </Container>
    </div>
  );
}
