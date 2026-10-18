import { useEffect, useState } from "react";
import { Links, Meta, Outlet, Scripts, ScrollRestoration } from "react-router";
import { AuthProvider, useAuth } from "@/context/AuthContext";
import { validateCurrentSession } from "@/services/auth";

function AuthBootstrap({ children }: { children: React.ReactNode }) {
	const { setIsAuthenticated } = useAuth();
	const [ready, setReady] = useState<boolean>(false);

	useEffect(() => {
		let cancelled = false;

		validateCurrentSession()
			.then(async (result) => {
				if (cancelled) return;
				if (!cancelled) {
					setIsAuthenticated(result.valid);
				}
			})
			.catch(() => {
				if (!cancelled) {
					setIsAuthenticated(false);
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

export function meta() {
	return [{ title: "PersV" }];
}

export function Layout({ children }: { children: React.ReactNode }) {
	return (
		<html lang="en">
			<head>
				<meta charSet="UTF-8" />
				<meta name="viewport" content="width=device-width, initial-scale=1.0" />
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
