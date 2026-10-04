import { createContext, type ReactNode, useContext, useState } from "react";

interface AuthContextValue {
	accessToken: string | null;
	setAccessToken: (token: string | null) => void;
	isAuthenticated: boolean;
	setIsAuthenticated: (value: boolean) => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
	const [accessToken, setAccessToken] = useState<string | null>(null);
	const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);

	return (
		<AuthContext.Provider
			value={{
				accessToken,
				setAccessToken,
				isAuthenticated,
				setIsAuthenticated,
			}}
		>
			{children}
		</AuthContext.Provider>
	);
}

export function useAuth() {
	const ctx = useContext(AuthContext);
	if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
	return ctx;
}
