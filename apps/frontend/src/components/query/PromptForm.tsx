import { Play } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

type PromptFormProps = {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  isPending: boolean;
  textareaRef: React.Ref<HTMLTextAreaElement>;
};

export function PromptForm({ value, onChange, onSubmit, isPending, textareaRef }: PromptFormProps) {
  const handleSubmit = (event: React.SubmitEvent<HTMLFormElement>) => {
    event.preventDefault();
    onSubmit();
  };

  const handleKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
      event.preventDefault();
      event.currentTarget.form?.requestSubmit();
    }
  };

  return (
    <Card>
      <CardContent>
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <Label htmlFor="prompt" className="sr-only">
            Query
          </Label>
          <Textarea
            ref={textareaRef}
            id="prompt"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask something about your data..."
            rows={3}
            required
          />
          <div className="flex items-center justify-between">
            <span className="text-xs text-muted-foreground">Ctrl + Enter to run</span>
            <Button type="submit" disabled={isPending}>
              <Play className="size-4" />
              {isPending ? "Running..." : "Query"}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
