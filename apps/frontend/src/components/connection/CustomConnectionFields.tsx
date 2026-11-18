import { useState } from "react";
import { parseConnectionString } from "@/lib/connectionString";
import { ConnectionStringInput } from "./ConnectionStringInput";
import { CredentialFields } from "./CredentialFields";
import { SqliteFileField } from "./SqliteFileField";
import { DBMS_OPTIONS, DEFAULT_PORTS, DEFAULT_SCHEMAS, INITIAL_FORM } from "./connectionOptions";
import type { ConnectionFormState, Dbms } from "@/types/connection";
import { Field, FieldGroup, FieldLabel, FieldLegend, FieldSet } from "@/components/ui/field";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export function CustomConnectionFields({ disabled }: { disabled: boolean }) {
  const [form, setForm] = useState<ConnectionFormState>(INITIAL_FORM);
  const [connectionString, setConnectionString] = useState("");
  const [connectionStringError, setConnectionStringError] = useState("");
  // Bumping this remounts ConnectionStringInput, which resets its "hide secrets" state
  const [connectionStringKey, setConnectionStringKey] = useState(0);

  const isSqlite = form.dbms === "sqlite";

  function handleConnectionStringChange(value: string) {
    setConnectionString(value);
    setConnectionStringError("");

    if (!value.trim()) return;

    try {
      const parsed = parseConnectionString(value);
      if (!parsed) return;

      setForm({
        dbms: parsed.dbms,
        host: parsed.host ?? "",
        port: parsed.port ?? DEFAULT_PORTS[parsed.dbms],
        username: parsed.username ?? "",
        password: parsed.password ?? "",
        database: parsed.database ?? "",
        schema: parsed.schema ?? DEFAULT_SCHEMAS[parsed.dbms] ?? "",
      });
    } catch {
      // Allow users to finish typing before showing an error.
    }
  }

  function validateConnectionString() {
    if (!connectionString.trim()) {
      setConnectionStringError("");
      return;
    }

    try {
      if (!parseConnectionString(connectionString)) {
        throw new Error("Invalid connection string.");
      }
      setConnectionStringError("");
    } catch (error) {
      setConnectionStringError(
        error instanceof Error ? error.message : "Invalid connection string.",
      );
    }
  }

  function updateField<K extends keyof ConnectionFormState>(
    field: K,
    value: ConnectionFormState[K],
  ) {
    setForm((previous) => ({ ...previous, [field]: value }));
    // Manual edits invalidate the original connection string.
    setConnectionStringError("");
  }

  function handleDBMSChange(dbms: Dbms) {
    setForm((previous) => ({
      ...previous,
      dbms,
      port: DEFAULT_PORTS[dbms],
      schema: DEFAULT_SCHEMAS[dbms] ?? "",
    }));
    setConnectionString("");
    setConnectionStringError("");
    setConnectionStringKey((key) => key + 1);
  }

  return (
    <fieldset disabled={disabled} className="min-w-0 space-y-5 disabled:opacity-60">
      {!isSqlite && (
        <>
          <ConnectionStringInput
            key={connectionStringKey}
            value={connectionString}
            error={connectionStringError}
            onChange={handleConnectionStringChange}
            onBlur={validateConnectionString}
          />

          {/* OR separator */}
          <div className="flex items-center gap-3">
            <div className="h-px flex-1 bg-border" />
            <span className="text-xs font-medium text-muted-foreground">OR</span>
            <div className="h-px flex-1 bg-border" />
          </div>
        </>
      )}

      <FieldSet>
        {!isSqlite && <FieldLegend variant="label">Configure manually</FieldLegend>}
        <FieldGroup id="connectionForm">
          <Field>
            <FieldLabel htmlFor="dbms">DBMS</FieldLabel>
            <Select
              name="dbms"
              items={DBMS_OPTIONS}
              value={form.dbms}
              onValueChange={(value) => handleDBMSChange(value as Dbms)}
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

          {isSqlite ? (
            <SqliteFileField showPathNote={!!connectionString} />
          ) : (
            <CredentialFields form={form} onFieldChange={updateField} />
          )}
        </FieldGroup>
      </FieldSet>
    </fieldset>
  );
}
