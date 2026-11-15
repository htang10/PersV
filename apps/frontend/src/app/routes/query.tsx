import { NavigationBar } from "@/components/navigation";
import { QueryInterface } from "@/components/query";

export function meta() {
  return [{ title: "Query database - PersV" }];
}

export default function QueryPage() {
  return (
    <>
      <NavigationBar />
      <QueryInterface />
    </>
  );
}
