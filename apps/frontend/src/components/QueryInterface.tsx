import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useQueryClient, useQuery, useMutation } from "@tanstack/react-query";
import { errorMessage } from "@/errors/error-message";
import { useNavigateNotice } from "@/hooks/useNavigateNotice";
import { checkConnStatus, disconnect, query } from "@/services/connection";

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

  if (!status.data?.connected) return null; // pending, error, or not connected: the effect redirects

  const handleSubmit = (event: React.SubmitEvent<HTMLFormElement>) => {
    event.preventDefault();
    queryMutation.mutate(prompt);
  };

  return (
    <div>
      <span>Connected to {status.data.database}</span>
      <form onSubmit={handleSubmit}>
        <textarea value={prompt} onChange={(e) => setPrompt(e.target.value)} rows={1} required />
        <div>
          <button type="submit" disabled={queryMutation.isPending}>
            Query
          </button>
          <button
            type="button"
            onClick={() => disconnectMutation.mutate()}
            disabled={disconnectMutation.isPending}
          >
            Disconnect
          </button>
        </div>
      </form>

      {queryMutation.isPending && <p aria-live="polite">Processing...</p>}
      {queryMutation.error && (
        <p role="alert">
          {errorMessage(queryMutation.error, {
            400: "An unexpected error occurred. Please reconnect to the database and try again.",
          })}
        </p>
      )}
      {disconnectMutation.error && <p role="alert">{errorMessage(disconnectMutation.error)}</p>}
      {queryMutation.data && (
        <div>
          <section>
            <p>
              <b>Result:</b>
            </p>
            <div className="query-result">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{queryMutation.data.result}</ReactMarkdown>
            </div>
          </section>
          <section>
            <p>
              <b>SQL:</b>
            </p>
            {queryMutation.data.sql ? (
              <pre>
                <code>{queryMutation.data.sql}</code>
              </pre>
            ) : (
              <p>None</p>
            )}
          </section>
        </div>
      )}
    </div>
  );
}
