import { NavigationBar, QueryInterface } from "@/components";

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
