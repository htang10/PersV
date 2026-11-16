import { Eye, EyeOff } from "lucide-react";
import { InputGroupButton } from "@/components/ui/input-group";

export function RevealButton({
  revealed,
  label,
  onToggle,
}: {
  revealed: boolean;
  label: string;
  onToggle: () => void;
}) {
  return (
    <InputGroupButton
      type="button"
      size="icon-xs"
      aria-label={revealed ? `Hide ${label}` : `Show ${label}`}
      aria-pressed={revealed}
      onClick={onToggle}
    >
      {revealed ? <EyeOff className="size-4" /> : <Eye className="size-4" />}
    </InputGroupButton>
  );
}
