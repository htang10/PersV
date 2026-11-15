import { useState, useRef } from "react";
import { useQueryClient, useMutation } from "@tanstack/react-query";
import { errorMessage } from "@/errors/error-message";
import { useNavigateNotice, CONNECTION_STATUS_KEY, useConnectionGuard } from "@/hooks";
import { disconnect, query } from "@/services/connection";
import { ConnectionBar } from "./ConnectionBar";
import { PromptForm } from "./PromptForm";
import { ResultSkeleton } from "./ResultSkeleton";
import { ResultCard } from "./ResultCard";
import { SqlCard } from "./SqlCard";
import { AlertCircle } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";

export function QueryInterface() {
  const navigateNotice = useNavigateNotice();
  const queryClient = useQueryClient();
  const status = useConnectionGuard();

  const [prompt, setPrompt] = useState("");
  const promptRef = useRef<HTMLTextAreaElement>(null);

  const queryMutation = useMutation({
    mutationFn: query,
    onError: () => queryClient.invalidateQueries({ queryKey: CONNECTION_STATUS_KEY }),
  });

  const disconnectMutation = useMutation({
    mutationFn: disconnect,
    onSuccess: () =>
      navigateNotice("/connect", { type: "info", message: "Disconnected from the database." }),
  });

  const handleSuggestionSelection = (suggestion: string) => {
    setPrompt(suggestion);
    promptRef.current?.focus();
  };

  if (!status.data?.connected) return null;

  const { database } = status.data;
  const response = queryMutation.data;
  const error = queryMutation.error || disconnectMutation.error;

  return (
    <main className="mx-auto flex w-full max-w-4xl flex-col gap-6 px-6 py-8">
      <ConnectionBar
        database={database}
        onDisconnect={() => disconnectMutation.mutate()}
        isDisconnecting={disconnectMutation.isPending}
      />
      <PromptForm
        value={prompt}
        onChange={setPrompt}
        onSubmit={() => queryMutation.mutate(prompt)}
        isPending={queryMutation.isPending}
        textareaRef={promptRef}
      />
      {error && (
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
      {queryMutation.isPending && <ResultSkeleton />}
      {response && !queryMutation.isPending && (
        <>
          <ResultCard
            result={response.result}
            suggestions={database === "demo" ? response.suggestions : undefined}
            onSelectSuggestion={handleSuggestionSelection}
          />
          <SqlCard sql={response.sql} />
        </>
      )}
    </main>
  );
}
