import { useEffect, useState } from "react";
import { Links, Meta, Outlet, Scripts, ScrollRestoration } from "react-router";
import { AuthProvider, useAuth } from "@/context/AuthContext";
import { rotateTokens, validateCurrentSession } from "@/services/auth";

function AuthBootstrap({ children }: { children: React.ReactNode }) {
	const { setAccessToken, setIsAuthenticated } = useAuth();
	const [ready, setReady] = useState(false);

	useEffect(() => {
		let cancelled = false;

		validateCurrentSession()
			.then(async (result) => {
				if (cancelled) return;
				setIsAuthenticated(result.valid);

				if (result.valid) {
					try {
						const { token } = await rotateTokens();
						if (!cancelled) setAccessToken(token);
					} catch {
						if (!cancelled) {
							setIsAuthenticated(false);
							setAccessToken(null);
						}
					}
				}
			})
			.catch(() => {
				if (!cancelled) {
					setIsAuthenticated(false);
					setAccessToken(null);
				}
			})
			.finally(() => {
				if (!cancelled) setReady(true);
			});

		return () => {
			cancelled = true;
		};
	}, []);

	if (!ready) return null;
	return <>{children}</>;
}

export function Layout({ children }: { children: React.ReactNode }) {
	return (
		<html lang="en">
			<head>
				<meta charSet="UTF-8" />
				<meta name="viewport" content="width=device-width, initial-scale=1.0" />
				<title>PersV</title>
				<Meta />
				<Links />
			</head>
			<body>
				{children}
				<ScrollRestoration />
				<Scripts />
			</body>
		</html>
	);
}

export default function Root() {
	return (
		<AuthProvider>
			<AuthBootstrap>
				<Outlet />
			</AuthBootstrap>
		</AuthProvider>
	);
}
