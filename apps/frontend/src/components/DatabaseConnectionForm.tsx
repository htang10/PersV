import { useState } from "react";
import type { ConnectionConfig, Dbms } from "@/client";
import { errorMessage } from "@/errors/error-message";
import { connectCustom, connectDemo } from "@/services/connection";

type ConnectionType = "demo" | "custom";

export function DatabaseConnectionForm({
	onConnected,
}: {
	onConnected: () => void;
}) {
	const [connectionType, setConnectionType] = useState<ConnectionType>("demo");
	const [connError, setConnError] = useState<string | null>(null);

	async function handleConnection(event: React.SubmitEvent<HTMLFormElement>) {
		event.preventDefault();
		try {
			if (connectionType === "demo") {
				await connectDemo();
			} else {
				const formData = new FormData(event.currentTarget);
				const customPayload: ConnectionConfig = {
					dbms: formData.get("dbms") as Dbms,
					username: formData.get("username") as string,
					password: formData.get("password") as string,
					host: formData.get("host") as string,
					port: parseInt(formData.get("port") as string, 10) as number,
					db: formData.get("database") as string,
					schema: (formData.get("schema") as string) || undefined,
				};
				await connectCustom(customPayload);
			}
			setConnError(null); // Clear any previous connection errors
			onConnected(); // Call the onConnected callback after successful connection
		} catch (error) {
			setConnError(errorMessage(error));
		}
	}

	return (
		<div>
			{connError && <p>{connError}</p>}
			<form onSubmit={handleConnection}>
				<input
					type="radio"
					name="connection"
					id="demo"
					value="demo"
					checked={connectionType === "demo"}
					onChange={(e) => setConnectionType(e.target.value as ConnectionType)}
				/>
				<label htmlFor="demo">Demo</label>
				<br />
				<input
					type="radio"
					name="connection"
					id="custom"
					value="custom"
					checked={connectionType === "custom"}
					onChange={(e) => setConnectionType(e.target.value as ConnectionType)}
				/>
				<label htmlFor="custom">Custom</label>
				<br />
				{connectionType === "custom" && (
					<>
						<div>
							<label htmlFor="dbms">DBMS: </label>
							<select name="dbms" id="dbms" required>
								<option value="postgresql">PostgreSQL</option>
								<option value="mysql">MySQL</option>
								<option value="mariadb">MariaDB</option>
								<option value="sqlite">SQLite</option>
								<option value="oracle">Oracle</option>
								<option value="mssql">Microsoft SQL Server</option>
							</select>
						</div>
						<div>
							<label htmlFor="username">Username: </label>
							<input type="text" name="username" id="username" required />
						</div>
						<div>
							<label htmlFor="password">Password: </label>
							<input type="password" name="password" id="password" required />
						</div>
						<div>
							<label htmlFor="host">Host: </label>
							<input type="text" name="host" id="host" required />
						</div>
						<div>
							<label htmlFor="port">Port: </label>
							<input
								type="text"
								name="port"
								id="port"
								inputMode="numeric"
								pattern="[0-9]*"
								onChange={(e) => {
									e.currentTarget.value = e.currentTarget.value.replace(
										/[^0-9]/g,
										"",
									);
								}} // Only allow numeric input
								required
							/>
						</div>
						<div>
							<label htmlFor="database">Database: </label>
							<input type="text" name="database" id="database" required />
						</div>
						<div>
							<label htmlFor="schema">Schema: </label>
							<input
								type="text"
								name="schema"
								id="schema"
								placeholder="Leave blank if not applicable"
							/>
						</div>
					</>
				)}
				<button type="submit">Connect</button>
			</form>
		</div>
	);
}
