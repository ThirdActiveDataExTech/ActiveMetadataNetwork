export type ID = number;

export interface GraphNode {
  id: ID;
  group: string;
  report_type: string;
  summary: string;
  fx: number;
  fy: number;
  fz: number;
  x?: number;
  y?: number;
  z?: number;
  // 필요 필드 자유롭게 확장
  [k: string]: unknown;
}

export interface GraphLink {
  source: ID | GraphNode;
  target: ID | GraphNode;
  type: string;
  report_type: string;
  weight: number;
  [k: string]: unknown;
}

export interface GraphData {
  nodes: GraphNode[];
  links: GraphLink[];
}
