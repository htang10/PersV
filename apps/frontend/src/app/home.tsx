import { useState } from "react";
import { useLocation, useNavigate } from "react-router";
import type { ConnectionConfig, Dbms } from "@/client";
import { NavigationBar } from "@/components/NavigationBar";
import { connect, connectCustom } from "@/services/connection";
import { errorMessage } from "@/services/error-message";

export default function Home() {
	const [targetDB, setTargetDB] = useState<string>("demo");
	const [connError, setConnError] = useState<string | null>(null);
	const navigate = useNavigate();
	const location = useLocation();
	const noticeMessage = location.state?.message as string | undefined;

	async function handleConnection(event: React.SubmitEvent<HTMLFormElement>) {
		event.preventDefault();
		try {
			if (targetDB === "demo") {
				await connect();
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
			setConnError(null);
			navigate("/query");
		} catch (error) {
			setConnError(errorMessage(error));
		}
	}

	return (
		<>
			<NavigationBar />
			{connError && <p id="error">{connError}</p>}
			{noticeMessage && <p id="notice">{noticeMessage}</p>}
			<div>
				<form onSubmit={handleConnection} method="post">
					<input
						type="radio"
						name="connection"
						value="demo"
						checked={targetDB === "demo"}
						onChange={(e) => setTargetDB(e.target.value)}
					/>
					<label htmlFor="demo">Demo</label>
					<br />
					<input
						type="radio"
						name="connection"
						value="custom"
						checked={targetDB === "custom"}
						onChange={(e) => setTargetDB(e.target.value)}
					/>
					<label htmlFor="custom">Custom</label>
					<br />
					{targetDB === "custom" && (
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
										e.currentTarget.value = e.currentTarget.value.replace(/[^0-9]/g, "");
									}}
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
		</>
	);
}
