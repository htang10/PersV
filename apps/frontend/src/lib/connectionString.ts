import type { ParsedConnection, Dbms } from "@/types/connection";

const SCHEME_TO_DBMS: Record<string, Dbms> = {
  postgresql: "postgresql",
  postgres: "postgresql",
  mysql: "mysql",
  mariadb: "mariadb",
  sqlite: "sqlite",
  oracle: "oracle",
  mssql: "mssql",
  sqlserver: "mssql",
};

function decode(value: string): string {
  try {
    return decodeURIComponent(value);
  } catch {
    return value;
  }
}

function parseSqlServerConnectionString(value: string): ParsedConnection | null {
  const parts = value.split(";").filter(Boolean);

  const entries = new Map<string, string>();

  for (const part of parts) {
    const separator = part.indexOf("=");

    if (separator === -1) continue;

    const key = part.slice(0, separator).trim().toLowerCase();
    const val = part.slice(separator + 1).trim();

    entries.set(key, val);
  }

  const get = (...keys: string[]) => {
    for (const key of keys) {
      const value = entries.get(key);

      if (value !== undefined) return value;
    }

    return undefined;
  };

  const server = get("server", "data source", "address", "addr", "network address");

  if (!server) return null;

  // Supports hostname, hostname,port and tcp:hostname,port.
  const normalizedServer = server.replace(/^tcp:/i, "");
  const serverParts = normalizedServer.match(/^(.+?)(?:,(\d+))?$/);

  const host = serverParts?.[1];
  const port = serverParts?.[2];

  if (!host) return null;

  return {
    dbms: "mssql",
    host,
    port: port ?? "1433",
    username: get("user id", "uid", "user"),
    password: get("password", "pwd"),
    database: get("initial catalog", "database"),
  };
}

export function parseConnectionString(input: string): ParsedConnection | null {
  const value = input.trim();

  if (!value) return null;

  // SQL Server's ADO.NET connection string format.
  if (/^(server|data source|address|addr|network address)\s*=/i.test(value)) {
    return parseSqlServerConnectionString(value);
  }

  // Handle SQLAlchemy and other driver-specific schemes.
  const schemeMatch = value.match(/^([a-z][a-z0-9+.-]*):\/\//i);

  if (!schemeMatch) {
    throw new Error("Unsupported connection string format.");
  }

  const scheme = schemeMatch[1].toLowerCase().split("+")[0];
  const dbms = SCHEME_TO_DBMS[scheme];

  if (!dbms) {
    throw new Error(`Unsupported database scheme: ${scheme}`);
  }

  const url = new URL(value);

  // SQLite uses a file path rather than network credentials.
  if (dbms === "sqlite") {
    return { dbms };
  }

  const pathname = decode(url.pathname).replace(/^\/+/, "");

  const parsed: ParsedConnection = {
    dbms,
    host: url.hostname || undefined,
    port: url.port || undefined,
    username: url.username ? decode(url.username) : undefined,
    password: url.password ? decode(url.password) : undefined,
    database: pathname || undefined,
  };

  // Allow an optional schema query parameter.
  const schema = url.searchParams.get("schema");

  if (schema) {
    parsed.schema = schema;
  }

  return parsed;
}

export function maskPassword(value: string): string {
  // SQL Server style: Password=...; or Pwd=...;
  if (/^\s*(server|data source|address|addr|network address)\s*=/i.test(value)) {
    return value.replace(
      /((?:password|pwd)\s*=)([^;]*)/i,
      (_, key: string, secret: string) => key + "*".repeat(secret.length),
    );
  }

  // URL style: scheme://user:password@host
  const schemeEnd = value.indexOf("://") + 3;
  const at = value.lastIndexOf("@");
  if (schemeEnd === 2 || at === -1) return value;

  const colon = value.lastIndexOf(":", at);
  if (colon < schemeEnd) return value; // user without a password

  return value.slice(0, colon + 1) + "*".repeat(at - colon - 1) + value.slice(at);
}
