import {
  Image,
  Brain,
  Network,
  Map,
  ShieldAlert,
  ShieldCheck,
  FileText,
  type LucideIcon,
} from "lucide-react";

import type { DockTab } from "../../context/DockContext";

interface DockItem {
  id: DockTab;
  label: string;
  icon: LucideIcon;
}

export const dockItems: DockItem[] = [
  {
    id: "imagery",
    label: "Imagery",
    icon: Image,
  },

  {
    id: "ai",
    label: "AI Analysis",
    icon: Brain,
  },

  {
    id: "graph",
    label: "Topology",
    icon: Network,
  },

  {
    id: "map",
    label: "Map",
    icon: Map,
  },

  {
    id: "risk",
    label: "Risk & Resilience",
    icon: ShieldCheck,
  },

  {
    id: "simulation",
    label: "Simulation",
    icon: ShieldAlert,
  },

  {
    id: "report",
    label: "Reports",
    icon: FileText,
  },
];