import { useState } from "react";
import { maskPassword } from "@/lib/connectionString";
import { RevealButton } from "@/components/shared/RevealButton";
import { Field, FieldDescription, FieldLabel } from "@/components/ui/field";
import { InputGroup, InputGroupAddon, InputGroupInput } from "@/components/ui/input-group";

type ConnectionStringInputProps = {
  value: string;
  error: string;
  onChange: (value: string) => void;
  onBlur: () => void;
};

export function ConnectionStringInput({
  value,
  error,
  onChange,
  onBlur,
}: ConnectionStringInputProps) {
  const [hideSecrets, setHideSecrets] = useState(false);

  const maskedValue = maskPassword(value);
  const hasSecret = maskedValue !== value;
  const isMasked = hasSecret && hideSecrets;

  function handlePaste(event: React.ClipboardEvent<HTMLInputElement>) {
    event.preventDefault(); // replace the whole value instead of inserting at the cursor
    const pasted = event.clipboardData.getData("text").trim();
    onChange(pasted);
    setHideSecrets(maskPassword(pasted) !== pasted);
  }

  return (
    <Field>
      <FieldLabel htmlFor="connectionString">Connection string</FieldLabel>
      <InputGroup>
        <InputGroupInput
          id="connectionString"
          value={isMasked ? maskedValue : value}
          readOnly={isMasked}
          onChange={(e) => onChange(e.target.value)}
          onPaste={handlePaste}
          onBlur={onBlur}
          placeholder="postgresql://user:password@host:5432/database"
          autoComplete="off"
          spellCheck={false}
          className="font-mono"
          aria-invalid={!!error}
        />
        {hasSecret && (
          <InputGroupAddon align="inline-end">
            <RevealButton
              revealed={!isMasked}
              label="connection string"
              onToggle={() => setHideSecrets((hidden) => !hidden)}
            />
          </InputGroupAddon>
        )}
      </InputGroup>
      <FieldDescription>
        Paste your database connection string to automatically populate the fields below.
      </FieldDescription>
      {error && (
        <p className="text-sm text-destructive" role="alert">
          {error}
        </p>
      )}
    </Field>
  );
}
