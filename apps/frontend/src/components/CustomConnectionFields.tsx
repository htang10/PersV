import { useState } from "react";
import type { Dbms } from "@/client";

const DBMS_OPTIONS = [
  { value: "postgresql", label: "PostgreSQL" },
  { value: "mysql", label: "MySQL" },
  { value: "mariadb", label: "MariaDB" },
  { value: "sqlite", label: "SQLite" },
  { value: "oracle", label: "Oracle" },
  { value: "mssql", label: "Microsoft SQL Server" },
] as const;

const DEFAULT_SCHEMAS: Partial<Record<Dbms, string>> = {
  postgresql: "public",
  mssql: "dbo",
  oracle: "",
};

export function CustomConnectionFields({ disabled }: { disabled: boolean }) {
  const [dbms, setDBMS] = useState<Dbms>("postgresql");
  const defaultSchema = DEFAULT_SCHEMAS[dbms];

  return (
    <fieldset disabled={disabled}>
      <div>
        <label htmlFor="dbms">DBMS: </label>
        <select
          name="dbms"
          id="dbms"
          value={dbms}
          onChange={(event) => setDBMS(event.target.value as Dbms)}
          required
        >
          {DBMS_OPTIONS.map(({ value, label }) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </select>
      </div>
      {dbms === "sqlite" ? (
        <div>
          <label htmlFor="sqliteFile">Database file</label>
          <div>
            <input
              type="file"
              name="sqliteFile"
              id="sqliteFile"
              accept=".sqlite, .sqlite3, .db, .db3"
              required
            />
          </div>
          <span>Allowed file extensions: .sqlite, .sqlite3, .db, .db3</span>
        </div>
      ) : (
        <>
          <div>
            <label htmlFor="username">Username: </label>
            <input type="text" name="username" id="username" autoComplete="off" required />
          </div>
          <div>
            <label htmlFor="password">Password: </label>
            <input type="password" name="password" id="password" autoComplete="off" required />
          </div>
          <div>
            <label htmlFor="host">Host: </label>
            <input type="text" name="host" id="host" required />
          </div>
          <div>
            <label htmlFor="port">Port: </label>
            <input
              type="text"
              name="port"
              id="port"
              inputMode="numeric"
              pattern="[0-9]*"
              onChange={(e) => {
                e.currentTarget.value = e.currentTarget.value.replace(/[^0-9]/g, "");
              }} // Only allow numeric input
              required
            />
          </div>
          <div>
            <label htmlFor="database">Database: </label>
            <input type="text" name="database" id="database" required />
          </div>
          {defaultSchema !== undefined && (
            <div>
              <label htmlFor="schema">Schema: </label>
              <input
                key={dbms}
                type="text"
                name="schema"
                id="schema"
                defaultValue={defaultSchema}
              />
            </div>
          )}
        </>
      )}
    </fieldset>
  );
}
