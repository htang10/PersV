import { Field, FieldDescription, FieldLabel } from "@/components/ui/field";
import { Input } from "@/components/ui/input";

export function SqliteFileField({ showPathNote }: { showPathNote: boolean }) {
  return (
    <Field>
      <FieldLabel htmlFor="sqliteFile">Database file</FieldLabel>
      <Input
        type="file"
        name="sqliteFile"
        id="sqliteFile"
        accept=".sqlite,.sqlite3,.db,.db3"
        required
      />
      <FieldDescription>Allowed extensions: .sqlite, .sqlite3, .db, .db3</FieldDescription>
      {showPathNote && (
        <FieldDescription>
          SQLite connection strings identify a file path. Please upload the database file manually.
        </FieldDescription>
      )}
    </Field>
  );
}
