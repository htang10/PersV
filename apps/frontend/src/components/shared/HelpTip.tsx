import { CircleHelp } from "lucide-react";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";

export function HelpTip({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <Popover>
      <PopoverTrigger
        openOnHover
        delay={150}
        aria-label={label}
        className="text-muted-foreground hover:text-foreground"
      >
        <CircleHelp className="size-4" />
      </PopoverTrigger>
      <PopoverContent className="max-w-xs text-sm">{children}</PopoverContent>
    </Popover>
  );
}
