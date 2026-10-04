import { Link } from "react-router";
import { useAuth } from "@/context/AuthContext";

export function NavigationBar() {
	const { isAuthenticated } = useAuth();

	console.log("render, isAuthenticated =", isAuthenticated);

	return (
		<header>
			<nav>
				<Link to="/connect" rel="noopener noreferrer">
					<img src="src/assets/logo.png" alt="Logo" width="100" height="100" />
				</Link>
			</nav>
			<div>
				{isAuthenticated ? (
					<Link to="/profile" rel="noopener noreferrer">
						Profile
					</Link>
				) : (
					<Link to="/login" target="_blank" rel="noopener noreferrer">
						Log in
					</Link>
				)}
			</div>
		</header>
	);
}
