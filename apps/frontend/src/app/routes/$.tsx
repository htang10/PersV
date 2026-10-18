import { Link } from "react-router";

export function meta() {
	return [{ title: "Page Not Found - PersV" }];
}

export default function UnknownPages() {
	return (
		<div>
			<h1>404 - Page Not Found</h1>
			<p>The page you are looking for does not exist.</p>
			<Link to="/connect">Go to home</Link>
		</div>
	);
}
