import type { Dbms } from "@/client";

export const DBMS_OPTIONS = [
  { value: "postgresql", label: "PostgreSQL" },
  { value: "mysql", label: "MySQL" },
  { value: "mariadb", label: "MariaDB" },
  { value: "sqlite", label: "SQLite" },
  { value: "oracle", label: "Oracle" },
  { value: "mssql", label: "Microsoft SQL Server" },
] as const;

export const DEFAULT_SCHEMAS: Partial<Record<Dbms, string>> = {
  postgresql: "public",
  mssql: "dbo",
  oracle: "",
};

export const DEFAULT_PORTS: Record<Dbms, string> = {
  postgresql: "5432",
  mysql: "3306",
  mariadb: "3306",
  sqlite: "",
  oracle: "1521",
  mssql: "1433",
};

export type ConnectionFormState = {
  dbms: Dbms;
  host: string;
  port: string;
  username: string;
  password: string;
  database: string;
  schema: string;
};

export type FieldChangeHandler = <K extends keyof ConnectionFormState>(
  field: K,
  value: ConnectionFormState[K],
) => void;

export const INITIAL_FORM: ConnectionFormState = {
  dbms: "postgresql",
  host: "",
  port: DEFAULT_PORTS.postgresql,
  username: "",
  password: "",
  database: "",
  schema: DEFAULT_SCHEMAS.postgresql ?? "",
};
