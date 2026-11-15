import { CopyButton, HelpTip } from "@/components/shared";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function SqlCard({ sql }: { sql?: string | null }) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>SQL</CardTitle>
        <div className="flex items-center gap-2">
          <HelpTip label="About the SQL">
            The SQL script the agent generated and ran against your database to reach its answer.
          </HelpTip>
          {sql && <CopyButton text={sql} />}
        </div>
      </CardHeader>
      <CardContent>
        {sql ? (
          <pre className="overflow-x-auto rounded-md bg-muted p-4 font-mono text-sm">
            <code>{sql}</code>
          </pre>
        ) : (
          <p className="text-sm text-muted-foreground">No SQL was generated.</p>
        )}
      </CardContent>
    </Card>
  );
}
