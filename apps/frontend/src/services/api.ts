import { API_URL } from "@/config";
import { APIError } from "@/errors/api-error";

type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
type RequestOptions<TRequest> = TRequest extends { body: infer B }
	? { body: B; accessToken?: string | null }
	: { body?: never; accessToken?: string | null };

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
	const accessToken = options.accessToken;

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
		throw new APIError(0);
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
		return {} as TResponse;
	}

	try {
		const parsed: APIResponse<TResponse> = await response.json();
		return parsed.data;
	} catch {
		throw new APIError(response.status);
	}
}
