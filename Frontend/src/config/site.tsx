import { Gauge, type LucideIcon, Shield, Settings, Wrench, Cog, ClipboardList } from "lucide-react";

export type SiteConfig = typeof siteConfig;
export type Navigation = {
  icon: LucideIcon;
  name: string;
  href: string;
};

export const siteConfig = {
  title: "IEEE IAS TSYP Challange",
  description: "IEEE IAS TSYP Challange",
};

export const navigations: Navigation[] = [
  {
    icon: Gauge,
    name: "Dashboard",
    href: "/",
  },
  {
    icon: Shield,
    name: "PPE Status",
    href: "/PPE",
  },
  {
    icon: Cog,
    name: "Machines Status",
    href: "/machines",
  },
  {
    icon: ClipboardList,
    name: "Backlog",
    href: "/backlog",
  },
  {
    icon: Settings,
    name: "Sensitization",
    href: "/sensitization",
  },
  {
    icon: Wrench,
    name: "Maintenance",
    href: "/maintenance",
  },
];
