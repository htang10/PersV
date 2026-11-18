import type { Dbms, ConnectionFormState } from "@/types/connection";

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

export const INITIAL_FORM: ConnectionFormState = {
  dbms: "postgresql",
  host: "",
  port: DEFAULT_PORTS.postgresql,
  username: "",
  password: "",
  database: "",
  schema: DEFAULT_SCHEMAS.postgresql,
};
