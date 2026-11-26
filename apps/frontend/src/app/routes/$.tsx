import { Link } from "react-router";
import { ArrowLeft } from "lucide-react";
import { NavigationBar } from "@/components/navigation";
import { Button } from "@/components/ui/button";

export function meta() {
  return [{ title: "Page Not Found - PersV" }];
}

export default function UnknownPages() {
  return (
    <>
      <main className="mx-auto flex flex-col w-full max-w-md items-center gap-6 px-6 py-[18vh] text-center">
        <p className="font-mono font-semibold text-7xl tracking-tight text-primary">404</p>
        <div className="flex flex-col gap-2">
          <h1 className="text-xl font-semibold tracking-tight">Page not found</h1>
          <p className="text-sm text-muted-foreground">
            The page you are looking for doesn't exist or may have been moved.
          </p>
        </div>
        <Button className="group px-6" render={<Link to="/connect" />} nativeButton={false}>
          <span className="relative transition-transform duration-200 ease-out group-hover:translate-x-3 group-focus-visible:translate-x-3 motion-reduce:transition-none">
            <span className="absolute -left-6 top-1/2 flex w-0 translate-x-3 -translate-y-1/2 overflow-hidden transition-all duration-200 ease-out group-hover:w-4 group-hover:translate-x-0 group-focus-visible:w-4 group-focus-visible:translate-x-0 motion-reduce:transition-none">
              <ArrowLeft className="size-4 shrink-0" />
            </span>
            Back to connect
          </span>
        </Button>
      </main>
    </>
  );
}