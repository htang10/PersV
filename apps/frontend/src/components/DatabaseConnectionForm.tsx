import { useState, Activity } from "react";
import type { ConnectionConfig, Dbms } from "@/client";
import { useMutation } from "@tanstack/react-query";
import { errorMessage } from "@/errors/error-message";
import { connectCustom, connectDemo } from "@/services/connection";
import { CustomConnectionFields } from "@/components";

type ConnectionType = "demo" | "custom";

export function DatabaseConnectionForm({ onConnected }: { onConnected: () => void }) {
  const [connectionType, setConnectionType] = useState<ConnectionType>("demo");
  const [connError, setConnError] = useState<string | null>(null);

  const connection = useMutation({
    mutationFn: (config: ConnectionConfig | null) =>
      config ? connectCustom(config) : connectDemo(),
    onSuccess: () => {
      setConnError(null);
      onConnected();
    },
    onError: (error) => setConnError(errorMessage(error)),
  });

  const handleSubmit = (event: React.SubmitEvent<HTMLFormElement>) => {
    event.preventDefault();
    setConnError(null); // Clear previous error message

    if (connectionType === "demo") {
      connection.mutate(null);
      return;
    }

    const formData = new FormData(event.currentTarget);
    const field = (name: string) => {
      const value = formData.get(name);
      return typeof value === "string" ? value : "";
    };

    const dbms = field("dbms") as Dbms;

    if (dbms === "sqlite") {
      setConnError("SQLite upload isn't supported yet.");
      return;
    }

    const port = Number(formData.get("port"));
    if (!Number.isInteger(port) || port < 1 || port > 65535) {
      setConnError("Port must be between 1 and 65535.");
      return;
    }

    connection.mutate({
      dbms,
      username: field("username"),
      password: field("password"),
      host: field("host"),
      port,
      db: field("database"),
      schema: field("schema") || undefined,
    });
  };

  return (
    <div>
      {connError && <p role="alert">{connError}</p>}
      <form onSubmit={handleSubmit}>
        <input
          type="radio"
          name="connection"
          id="demo"
          value="demo"
          checked={connectionType === "demo"}
          onChange={(e) => setConnectionType(e.target.value as ConnectionType)}
        />
        <label htmlFor="demo">Demo</label>
        <br />
        <input
          type="radio"
          name="connection"
          id="custom"
          value="custom"
          checked={connectionType === "custom"}
          onChange={(e) => setConnectionType(e.target.value as ConnectionType)}
        />
        <label htmlFor="custom">Custom</label>
        <br />
        <Activity mode={connectionType === "custom" ? "visible" : "hidden"}>
          <CustomConnectionFields disabled={connectionType !== "custom"} />
        </Activity>
        <button type="submit" disabled={connection.isPending}>
          {connection.isPending ? "Connecting..." : "Connect"}
        </button>
      </form>
    </div>
  );
}
