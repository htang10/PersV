import { useNavigate } from "react-router";
import { DatabaseConnectionForm, NavigationBar, Notice } from "@/components";

export function meta() {
	return [{ title: "Connect to database - PersV" }];
}

export default function ConnectPage() {
	const navigate = useNavigate();

	return (
		<>
			<NavigationBar />
			<Notice />
			<DatabaseConnectionForm onConnected={() => navigate("/query")} />
		</>
	);
}
