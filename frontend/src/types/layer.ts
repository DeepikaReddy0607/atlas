export interface Layer {
  id: string;

  name: string;

  url?: string;

  visible: boolean;

  opacity: number;

  type:
    | "base"
    | "overlay"
    | "mask"
    | "graph"
    | "analysis";
}