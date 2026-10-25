import { API_URL } from "@/config";
import { APIError, MalformedJSON } from "@/errors/error-type";
import { authTokenStore } from "@/services/token";

type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
type RequestOptions<TRequest> = TRequest extends { body: infer B }
	? { body: B }
	: { body?: never };

interface APIResponse<TResponse> {
	data: TResponse;
	metadata: unknown | null;
}

export async function fetchAPI<TRequest extends { url: string }, TResponse>(
	method: HttpMethod,
	path: TRequest["url"],
	...args: TRequest extends { body: unknown }
		? [options: RequestOptions<TRequest>]
		: [options?: RequestOptions<TRequest>]
): Promise<TResponse> {
	const options = (args[0] ?? {}) as RequestOptions<TRequest>;
	const payload = "body" in options ? JSON.stringify(options.body) : undefined;
	const accessToken = authTokenStore.getToken();

	let response: Response;

	try {
		response = await fetch(`${API_URL}${path}`, {
			method,
			headers: {
				"Content-Type": "application/json",
				...(accessToken && {
					Authorization: `Bearer ${accessToken}`,
				}),
			},
			body: payload,
			credentials: "include",
		});
		const newAccessToken = response.headers.get("X-New-Access-Token");
		if (newAccessToken) {
			authTokenStore.setToken(newAccessToken);
		}
	} catch {
		throw new APIError(0); // Usually network error
	}

	if (!response.ok) {
		const error: unknown = await response.json().catch(() => null);
		const detail =
			typeof error === "object" && error !== null && "detail" in error
				? error.detail
				: undefined;
		throw new APIError(response.status, detail);
	}

	if (response.status === 204) {
		// No JSON returned
		return {} as TResponse;
	}

	try {
		const parsed: APIResponse<TResponse> = await response.json();
		return parsed.data;
	} catch (error) {
		if (error instanceof SyntaxError) {
			throw new MalformedJSON();
		}
		throw error;
	}
}
