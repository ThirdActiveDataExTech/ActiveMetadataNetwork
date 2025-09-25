export type Formatter =
  | "text"
  | "number"
  | "date"
  | "json"
  | ((v: unknown, field: Field, all: Record<string, unknown>) => string);

export interface TableColumn {
  key: string;
  label: string;
  align?: "left" | "right" | "center";
  format?: Formatter;
  width?: string;
}

export interface TableRow {
  [key: string]: any;
}
