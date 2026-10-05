import { useNavigate } from "react-router";
import { DatabaseConnectionForm, NavigationBar, Notice } from "@/components";

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
