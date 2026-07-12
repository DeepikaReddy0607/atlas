import {
  Image,
  Brain,
  Network,
  Map,
  ShieldAlert,
  FileText,
  Settings,
} from "lucide-react";

export const dockItems = [
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
    id: "simulation",
    label: "Simulation",
    icon: ShieldAlert,
  },
  {
    id: "report",
    label: "Reports",
    icon: FileText,
  },
  {
    id: "settings",
    label: "Settings",
    icon: Settings,
  },
];