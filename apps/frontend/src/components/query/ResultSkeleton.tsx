import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

export function ResultSkeleton() {
  return (
    <Card aria-live="polite" aria-busy>
      <CardContent className="flex flex-col gap-3">
        <span className="sr-only">Processing...</span>
        <Skeleton className="h-4 w-1/3" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-2/3" />
      </CardContent>
    </Card>
  );
}
