import type { ClientServerConnectionConfig } from "@/client";

export type ConnectionType = "demo" | "custom";

export type Dbms = ClientServerConnectionConfig["dbms"] | "sqlite";

export type ParsedConnection = {
  dbms: Dbms;
  host?: string;
  port?: string;
  username?: string;
  password?: string;
  database?: string;
  schema?: string;
};

export type ConnectionFormState = {
  dbms: Dbms;
  host: string;
  port: string;
  username: string;
  password: string;
  database: string;
  schema?: string; // MySQL and MariaDB have different schema concepts
};

export type FieldChangeHandler = <K extends keyof ConnectionFormState>(
  field: K,
  value: ConnectionFormState[K],
) => void;
