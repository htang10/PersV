import { useState, Activity } from "react";
import type { ClientServerConnectionConfig } from "@/client";
import type { ConnectionType, Dbms } from "@/types/connection";
import { useMutation } from "@tanstack/react-query";
import { errorMessage } from "@/errors/error-message";
import { connectCustom, connectDemo, connectSQLite } from "@/services/connection";
import { CustomConnectionFields } from "./CustomConnectionFields";
import { AlertCircle, Database, Loader2 } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Tabs as TabsPrimitive } from "@base-ui/react/tabs";

export function DatabaseConnectionForm({ onConnected }: { onConnected: () => void }) {
  const [connectionType, setConnectionType] = useState<ConnectionType>("demo");
  const [connError, setConnError] = useState<string | null>(null);

  const connection = useMutation({
    mutationFn: (config?: ClientServerConnectionConfig | File) => {
      if (!config) return connectDemo();
      if (config instanceof File) return connectSQLite(config);
      return connectCustom(config);
    },
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
      connection.mutate();
      return;
    }

    const formData = new FormData(event.currentTarget);
    const field = (name: string) => {
      const value = formData.get(name);
      return typeof value === "string" ? value : "";
    };

    const dbms = field("dbms") as Dbms;

    if (dbms === "sqlite") {
      const file = formData.get("sqliteFile");
      // An empty file input still yields a File object, with size 0
      if (!(file instanceof File) || file.size === 0) {
        setConnError("Please upload a database file.");
        return;
      }
      connection.mutate(file);
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
    <Card className="w-full">
      <form onSubmit={handleSubmit} className="flex flex-col gap-5">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database className="size-4" />
            Connect to a database
          </CardTitle>
          <CardDescription>Try the demo database or connect your own.</CardDescription>
        </CardHeader>

        <CardContent className="flex flex-col gap-4">
          <Tabs
            value={connectionType}
            onValueChange={(value) => setConnectionType(value as ConnectionType)}
          >
            <TabsList className="relative w-full">
              <TabsPrimitive.Indicator className="absolute left-0 top-(--active-tab-top) h-(--active-tab-height) w-(--active-tab-width) translate-x-(--active-tab-left) rounded-md bg-background shadow-sm transition-all duration-300 ease-out motion-reduce:transition-none" />
              <TabsTrigger value="demo">Demo</TabsTrigger>
              <TabsTrigger value="custom">Custom</TabsTrigger>
            </TabsList>
          </Tabs>

          <Activity mode={connectionType === "demo" ? "visible" : "hidden"}>
            <p className="text-sm text-muted-foreground">
              The demo uses{" "}
              <a
                href="https://github.com/lerocha/chinook-database"
                target="_blank"
                rel="noopener noreferrer"
                className="underline underline-offset-4 hover:text-foreground"
              >
                Chinook
              </a>
              , a sample database for a digital music store. It holds the catalog (artists, albums,
              tracks, genres), customers with their invoices, employees, and playlists. It's
              relatively small, widely used, and has enough relationships between tables to make it
              a good fit for demonstration purposes.
            </p>
          </Activity>

          <Activity mode={connectionType === "custom" ? "visible" : "hidden"}>
            <div className="animate-in fade-in-0 slide-in-from-top-1 duration-300 motion-reduce:animate-none">
              <CustomConnectionFields disabled={connectionType !== "custom"} />
            </div>
          </Activity>

          {connError && (
            <Alert variant="destructive" role="alert">
              <AlertCircle className="size-4" />
              <AlertDescription>{connError}</AlertDescription>
            </Alert>
          )}
        </CardContent>

        <CardFooter>
          <Button type="submit" className="w-full" disabled={connection.isPending}>
            {connection.isPending && <Loader2 className="size-4 animate-spin" />}
            {connection.isPending ? "Connecting..." : "Connect"}
          </Button>
        </CardFooter>
      </form>
    </Card>
  );
}
