import { useNavigate } from "react-router";
import { NavigationBar } from "@/components/navigation";
import { DatabaseConnectionForm } from "@/components/connection";
import { Notice } from "@/components/shared";

export function meta() {
  return [{ title: "Connect to database - PersV" }];
}

export default function ConnectPage() {
  const navigate = useNavigate();

  return (
    <>
      <NavigationBar />
      <main className="mx-auto flex w-full max-w-3xl flex-col gap-4 px-6 pt-[12vh]">
        <Notice />
        <DatabaseConnectionForm onConnected={() => navigate("/query")} />
      </main>
    </>
  );
}
