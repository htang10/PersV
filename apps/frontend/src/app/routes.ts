import { index, type RouteConfig, route } from "@react-router/dev/routes";

export default [
	index("./home.tsx"),
	route("/login", "./auth/login.tsx"),
	route("/query", "./connection/query.tsx"),
] satisfies RouteConfig;
