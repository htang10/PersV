import { useState } from "react";
import type { Dbms } from "@/client";
import { Field, FieldDescription, FieldGroup, FieldLabel } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectTrigger,
  SelectValue,
  SelectItem,
} from "@/components/ui/select";

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

const DEFAULT_PORTS: Record<Dbms, string> = {
  postgresql: "5432",
  mysql: "3306",
  mariadb: "3306",
  sqlite: "",
  oracle: "1521",
  mssql: "1433",
};

export function CustomConnectionFields({ disabled }: { disabled: boolean }) {
  const [dbms, setDBMS] = useState<Dbms>("postgresql");
  const defaultSchema = DEFAULT_SCHEMAS[dbms];

  return (
    <fieldset disabled={disabled} className="min-w-0 disabled:opacity-60">
      <FieldGroup>
        <Field>
          <FieldLabel htmlFor="dbms">DBMS</FieldLabel>
          <Select
            name="dbms"
            items={DBMS_OPTIONS}
            value={dbms}
            onValueChange={(value) => setDBMS(value as Dbms)}
            required
          >
            <SelectTrigger id="dbms" className="w-full">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {DBMS_OPTIONS.map(({ value, label }) => (
                <SelectItem key={value} value={value}>
                  {label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </Field>

        {dbms === "sqlite" ? (
          <Field>
            <FieldLabel htmlFor="sqliteFile">Database file</FieldLabel>
            <Input
              type="file"
              name="sqliteFile"
              id="sqliteFile"
              accept=".sqlite, .sqlite3, .db, .db3"
              required
            />
            <FieldDescription>Allowed extensions: .sqlite, .sqlite3, .db, .db3</FieldDescription>
          </Field>
        ) : (
          <>
            <div className="grid grid-cols-[1fr_6rem] gap-3">
              <Field>
                <FieldLabel htmlFor="host">Host</FieldLabel>
                <Input
                  id="host"
                  name="host"
                  placeholder="localhost"
                  className="font-mono"
                  required
                />
              </Field>
              <Field>
                <FieldLabel htmlFor="port">Port</FieldLabel>
                <Input
                  name="port"
                  id="port"
                  key={dbms}
                  inputMode="numeric"
                  pattern="[0-9]*"
                  placeholder={DEFAULT_PORTS[dbms]}
                  className="font-mono"
                  onChange={(e) => {
                    e.currentTarget.value = e.currentTarget.value.replace(/[^0-9]/g, "");
                  }}
                  required
                />
              </Field>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <Field>
                <FieldLabel htmlFor="username">Username</FieldLabel>
                <Input
                  name="username"
                  id="username"
                  autoComplete="off"
                  className="font-mono"
                  required
                />
              </Field>
              <Field>
                <FieldLabel htmlFor="password">Password</FieldLabel>
                <Input type="password" name="password" id="password" autoComplete="off" required />
              </Field>
            </div>

            <div className={defaultSchema !== undefined ? "grid grid-cols-2 gap-3" : "grid gap-3"}>
              <Field>
                <FieldLabel htmlFor="database">Database</FieldLabel>
                <Input name="database" id="database" className="font-mono" required />
              </Field>
              {defaultSchema !== undefined && (
                <Field>
                  <FieldLabel htmlFor="schema">Schema</FieldLabel>
                  <Input
                    key={dbms}
                    name="schema"
                    id="schema"
                    placeholder={DEFAULT_SCHEMAS[dbms]}
                    className="font-mono"
                  />
                </Field>
              )}
            </div>
          </>
        )}
      </FieldGroup>
    </fieldset>
  );
}
