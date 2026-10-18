import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { PostConnectionQueryResponse } from "@/client";
import { errorMessage } from "@/errors/error-message";
import { useNavigateNotice } from "@/hooks/useNavigateNotice";
import { checkConnStatus, disconnect, query } from "@/services/connection";

export function meta() {
	return [{ title: "Query database - PersV" }];
}

export default function QueryPage() {
	const navigateNotice = useNavigateNotice();

	const [checking, setChecking] = useState<boolean>(true);
	const [connectedDB, setConnectedDB] = useState<string | null | undefined>(
		null,
	);
	const [prompt, setPrompt] = useState<string>("");
	const [processing, setProcessing] = useState<boolean>(false);
	const [queryResult, setQueryResult] =
		useState<PostConnectionQueryResponse | null>(null);
	const [queryError, setQueryError] = useState<string | null>(null);

	const checkConnection = async (): Promise<boolean> => {
		try {
			const connStatus = await checkConnStatus();

			if (!connStatus.connected) {
				navigateNotice("/connect", {
					type: "error",
					message:
						"Not connected to any database yet or session expired due to inactivity. Please establish a database connection in order to query.",
				});

				return false;
			}
			setChecking(false);
			setConnectedDB(connStatus.database);

			return connStatus.connected;
		} catch (error) {
			navigateNotice("/connect", {
				type: "error",
				message: errorMessage(error),
			});

			return false;
		}
	};

	useEffect(() => {
		checkConnection();
	}, []);

	// Don't render the query page until the connection check completes
	if (checking) {
		return null;
	}

	const handleQuery = async (event: React.SubmitEvent<HTMLFormElement>) => {
		event.preventDefault();

		// Re-check in case the connection expired since the last check
		const connected = await checkConnection();
		if (!connected) return;

		setProcessing(true);

		try {
			const result = await query(prompt);
			setQueryResult(result);
			setQueryError(null);
		} catch (error) {
			setQueryError(
				errorMessage(error, {
					400: "An unexpected error occurred. Please reconnect to the database and try again.",
				}),
			);
			setQueryResult(null);
		} finally {
			setProcessing(false);
		}
	};

	const handleDisconnect = async () => {
		await disconnect();
		navigateNotice("/connect", {
			type: "info",
			message: "Disconnected from the database.",
		});
	};

	return (
		<div>
			{(connectedDB && <span>Connected to {connectedDB}</span>) || (
				<span>Not connected to any database</span>
			)}
			<form onSubmit={handleQuery} onReset={handleDisconnect}>
				<textarea
					value={prompt}
					onChange={(e) => setPrompt(e.target.value)}
					rows={1}
					required
				/>
				<div>
					<button type="submit">Query</button>
					<button type="reset">Disconnect</button>
				</div>
			</form>
			{processing && <p>Processing...</p>}
			{queryError && <p>{queryError}</p>}
			{queryResult && (
				<div>
					<section>
						<p>
							<b>Result:</b>
						</p>
						<div className="query-result">
							<ReactMarkdown remarkPlugins={[remarkGfm]}>
								{queryResult.result}
							</ReactMarkdown>
						</div>
					</section>
					<section>
						<p>
							<b>SQL:</b>
						</p>
						{queryResult.sql ? (
							<pre>
								<code>{queryResult.sql}</code>
							</pre>
						) : (
							<p>None</p>
						)}
					</section>
				</div>
			)}
		</div>
	);
}
