import { Unplug } from "lucide-react";
import { Button } from "@/components/ui/button";

type ConnectionBarProps = {
  database: string | null | undefined;
  onDisconnect: () => void;
  isDisconnecting: boolean;
};

export function ConnectionBar({ database, onDisconnect, isDisconnecting }: ConnectionBarProps) {
  return (
    <div className="flex items-center justify-between">
      <p className="flex items-center gap-2 text-sm text-muted-foreground">
        <span className="size-2 rounded-full bg-success" aria-hidden />
        Connected to <span className="font-mono text-foreground">{database}</span>
      </p>
      <Button variant="outline" size="sm" onClick={onDisconnect} disabled={isDisconnecting}>
        <Unplug className="size-4" />
        {isDisconnecting ? "Disconnecting..." : "Disconnect"}
      </Button>
    </div>
  );
}
