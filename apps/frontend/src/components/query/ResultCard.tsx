import ReactMarkdown from "react-markdown";
import type { Components } from "react-markdown";
import remarkGfm from "remark-gfm";
import { HelpTip } from "@/components/shared";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

const markdownComponents: Components = {
  table: ({ node, ...props }) => (
    <div className="my-4 rounded-md border">
      <Table {...props} />
    </div>
  ),
  thead: ({ node, ...props }) => <TableHeader {...props} />,
  tbody: ({ node, ...props }) => <TableBody {...props} />,
  tr: ({ node, ...props }) => <TableRow {...props} />,
  th: ({ node, ...props }) => <TableHead {...props} />,
  td: ({ node, ...props }) => <TableCell {...props} />,
};

type ResultCardProps = {
  result: string;
  suggestions?: string[] | null;
  onSelectSuggestion: (suggestion: string) => void;
};

export function ResultCard({ result, suggestions, onSelectSuggestion }: ResultCardProps) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Result</CardTitle>
        <HelpTip label="About results">
          Some questions may get no answer. If the request tried to change data (DML such as INSERT,
          UPDATE, or DELETE) or the schema (DDL such as CREATE, ALTER, or DROP). Those queries are
          blocked and never executed. Only read-only questions are supported.
        </HelpTip>
      </CardHeader>
      <CardContent className="flex flex-col gap-5 overflow-x-auto">
        <div className="query-result">
          <ReactMarkdown remarkPlugins={[remarkGfm]} components={markdownComponents}>
            {result}
          </ReactMarkdown>
        </div>
        {!!suggestions?.length && (
          <div className="flex flex-wrap gap-2">
            {suggestions.map((suggestion) => (
              <Button
                key={suggestion}
                type="button"
                variant="outline"
                size="sm"
                onClick={() => onSelectSuggestion(suggestion)}
              >
                {suggestion}
              </Button>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
