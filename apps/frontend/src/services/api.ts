import { API_URL } from "@/config";
import { APIError, MalformedJSON } from "@/errors/error-type";
import { rotateTokens } from "@/services/auth";
import { authTokenStore } from "@/services/token";

type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
type RequestOptions<TRequest> = TRequest extends { body: infer B }
	? { body: B }
	: { body?: never };

interface APIResponse<TResponse> {
	data: TResponse;
	metadata: unknown | null;
}

const MAX_RETRIES = 1;

export async function fetchAPI<TRequest extends { url: string }, TResponse>(
	method: HttpMethod,
	path: TRequest["url"],
	...args: TRequest extends { body: unknown }
		? [options: RequestOptions<TRequest>]
		: [options?: RequestOptions<TRequest>]
): Promise<TResponse> {
	return fetchAPIWithRetry<TRequest, TResponse>(method, path, 0, ...args);
}

async function fetchAPIWithRetry<TRequest extends { url: string }, TResponse>(
	method: HttpMethod,
	path: TRequest["url"],
	retries: number,
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
	} catch {
		throw new APIError(0); // Usually network error
	}

	if (!response.ok) {
		if (response.status === 401) {
			// Unauthorized request
			if (accessToken && retries < MAX_RETRIES) {
				/*
				 * Perform token rotation if user's token exists but expired
				 * AND maximum retry attempts haven't been reached yet
				 */
				try {
					const payload = await rotateTokens();
					authTokenStore.setToken(payload.token);
					return fetchAPIWithRetry<TRequest, TResponse>(
						method,
						path,
						retries + 1,
						...args,
					); // Retry with new access token
				} catch {
					// Both access and refresh tokens expired
					authTokenStore.expireSession();
				}
			}
		}
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
