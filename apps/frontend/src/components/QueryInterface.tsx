import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import type { Components } from "react-markdown";
import remarkGfm from "remark-gfm";
import { useQueryClient, useQuery, useMutation } from "@tanstack/react-query";
import { errorMessage } from "@/errors/error-message";
import { useNavigateNotice } from "@/hooks/useNavigateNotice";
import { checkConnStatus, disconnect, query } from "@/services/connection";
import { AlertCircle, Play, Unplug } from "lucide-react";
import { CopyButton } from "@/components/CopyButton";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { Textarea } from "@/components/ui/textarea";
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

export function QueryInterface() {
  const navigateNotice = useNavigateNotice();
  const queryClient = useQueryClient();

  const [prompt, setPrompt] = useState<string>("");

  const status = useQuery({
    queryKey: ["connection-status"],
    queryFn: checkConnStatus,
    staleTime: 0, // always treat as stale, so every focus or mount re-checks
    gcTime: 0, // drop the cache on unmount, so a stale "connected" is never shown on re-entry
    retry: false,
  });

  const queryMutation = useMutation({
    mutationFn: query,
    // a failed query may mean the connection expired: re-check, and the effect above redirects if so
    onError: () => queryClient.invalidateQueries({ queryKey: ["connection-status"] }),
  });

  const disconnectMutation = useMutation({
    mutationFn: disconnect,
    onSuccess: () =>
      navigateNotice("/connect", { type: "info", message: "Disconnected from the database." }),
  });

  const handleSubmit = (event: React.SubmitEvent<HTMLFormElement>) => {
    event.preventDefault();
    queryMutation.mutate(prompt);
  };

  const handleKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Ctrl/Cmd + Enter submits, plain Enter adds a new line
    if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
      event.preventDefault();
      event.currentTarget.form?.requestSubmit();
    }
  };

  useEffect(() => {
    /*
    Only redirect users if they failed to connect, meaning data wasn't returned.
    A network error can potentially trigger before a request even succeeds due to focus refetching.
    */
    if (status.isError && !status.data) {
      navigateNotice("/connect", { type: "error", message: errorMessage(status.error) });
    } else if (status.data && !status.data.connected) {
      navigateNotice("/connect", {
        type: "error",
        message: "Not connected to any database yet or the session expired. Please connect first.",
      });
    }
  }, [status.isError, status.error, status.data]);

  if (!status.data?.connected) return null; // pending, error, or not connected: the effect redirects

  return (
    <main className="mx-auto flex w-full max-w-4xl flex-col gap-6 px-6 py-8">
      <div className="flex items-center justify-between">
        <p className="flex items-center gap-2 text-sm text-muted-foreground">
          <span className="size-2 rounded-full bg-success" aria-hidden />
          Connected to <span className="font-mono text-foreground">{status.data.database}</span>
        </p>
        <Button
          variant="outline"
          size="sm"
          onClick={() => disconnectMutation.mutate()}
          disabled={disconnectMutation.isPending}
        >
          <Unplug className="size-4" />
          {disconnectMutation.isPending ? "Disconnecting..." : "Disconnect"}
        </Button>
      </div>

      <Card>
        <CardContent>
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <Label htmlFor="prompt" className="sr-only">
              Query
            </Label>
            <Textarea
              id="prompt"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask something about your data..."
              rows={3}
              required
            />
            <div className="flex items-center justify-between">
              <span className="text-xs text-muted-foreground">Ctrl + Enter to run</span>
              <Button type="submit" disabled={queryMutation.isPending}>
                <Play className="size-4" />
                {queryMutation.isPending ? "Running..." : "Query"}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      {(queryMutation.error || disconnectMutation.error) && (
        <Alert variant="destructive">
          <AlertCircle className="size-4" />
          <AlertDescription>
            {queryMutation.error
              ? errorMessage(queryMutation.error, {
                  400: "An unexpected error occurred. Please reconnect to the database and try again.",
                })
              : errorMessage(disconnectMutation.error)}
          </AlertDescription>
        </Alert>
      )}

      {queryMutation.isPending && (
        <Card aria-live="polite" aria-busy>
          <CardContent className="flex flex-col gap-3">
            <span className="sr-only">Processing...</span>
            <Skeleton className="h-4 w-1/3" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-2/3" />
          </CardContent>
        </Card>
      )}

      {queryMutation.data && !queryMutation.isPending && (
        <>
          <Card>
            <CardHeader>
              <CardTitle>Result</CardTitle>
            </CardHeader>
            <CardContent className="overflow-x-auto">
              <div className="query-result">
                <ReactMarkdown remarkPlugins={[remarkGfm]} components={markdownComponents}>
                  {queryMutation.data.result}
                </ReactMarkdown>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>SQL</CardTitle>
              {queryMutation.data.sql && <CopyButton text={queryMutation.data.sql} />}
            </CardHeader>
            <CardContent>
              {queryMutation.data.sql ? (
                <pre className="overflow-x-auto rounded-md bg-muted p-4 font-mono text-sm">
                  <code>{queryMutation.data.sql}</code>
                </pre>
              ) : (
                <p className="text-sm text-muted-foreground">No SQL was generated.</p>
              )}
            </CardContent>
          </Card>
        </>
      )}
    </main>
  );
}
