import { useState } from "react";
import { DEFAULT_PORTS, DEFAULT_SCHEMAS } from "./connectionOptions";
import type { ConnectionFormState, FieldChangeHandler } from "@/types/connection";
import { RevealButton } from "@/components/shared/RevealButton";
import { Field, FieldLabel } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { InputGroup, InputGroupAddon, InputGroupInput } from "@/components/ui/input-group";

type CredentialFieldsProps = {
  form: ConnectionFormState;
  onFieldChange: FieldChangeHandler;
};

export function CredentialFields({ form, onFieldChange }: CredentialFieldsProps) {
  const [showPassword, setShowPassword] = useState(false);
  const hasSchema = DEFAULT_SCHEMAS[form.dbms] !== undefined;

  return (
    <>
      <div className="grid grid-cols-[1fr_6rem] gap-3">
        <Field>
          <FieldLabel htmlFor="host">Host</FieldLabel>
          <Input
            id="host"
            name="host"
            value={form.host}
            onChange={(e) => onFieldChange("host", e.target.value)}
            placeholder="localhost"
            className="font-mono"
            required
          />
        </Field>
        <Field>
          <FieldLabel htmlFor="port">Port</FieldLabel>
          <Input
            id="port"
            name="port"
            value={form.port}
            onChange={(e) => onFieldChange("port", e.target.value.replace(/[^0-9]/g, ""))}
            inputMode="numeric"
            placeholder={DEFAULT_PORTS[form.dbms]}
            className="font-mono"
            required
          />
        </Field>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <Field>
          <FieldLabel htmlFor="username">Username</FieldLabel>
          <Input
            id="username"
            name="username"
            value={form.username}
            onChange={(e) => onFieldChange("username", e.target.value)}
            autoComplete="off"
            className="font-mono"
            required
          />
        </Field>
        <Field>
          <FieldLabel htmlFor="password">Password</FieldLabel>
          <InputGroup>
            <InputGroupInput
              id="password"
              name="password"
              type={showPassword ? "text" : "password"}
              value={form.password}
              onChange={(e) => onFieldChange("password", e.target.value)}
              autoComplete="new-password"
              required
            />
            <InputGroupAddon align="inline-end">
              <RevealButton
                revealed={showPassword}
                label="password"
                onToggle={() => setShowPassword((shown) => !shown)}
              />
            </InputGroupAddon>
          </InputGroup>
        </Field>
      </div>

      <div className={hasSchema ? "grid grid-cols-2 gap-3" : "grid gap-3"}>
        <Field>
          <FieldLabel htmlFor="database">Database</FieldLabel>
          <Input
            id="database"
            name="database"
            value={form.database}
            onChange={(e) => onFieldChange("database", e.target.value)}
            className="font-mono"
            required
          />
        </Field>
        {hasSchema && (
          <Field>
            <FieldLabel htmlFor="schema">Schema</FieldLabel>
            <Input
              id="schema"
              name="schema"
              value={form.schema}
              onChange={(e) => onFieldChange("schema", e.target.value)}
              placeholder={DEFAULT_SCHEMAS[form.dbms]}
              className="font-mono"
            />
          </Field>
        )}
      </div>
    </>
  );
}
