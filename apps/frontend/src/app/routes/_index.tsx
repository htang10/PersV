import { redirect } from "react-router";

export function meta() {
  return [
    {
      title: "PersV: Reliable database query assistant for non-technical users",
    },
  ];
}

export async function clientLoader() {
  // Runs only in the browser, so cookies/credentials work correctly
  return redirect("/connect");
}

clientLoader.hydrate = true as const; // ensures it runs on initial load too, not just client-side navigation

export default function Index() {
  return null;
}
