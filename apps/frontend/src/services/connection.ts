import type {
	ConnectionConfig,
	GetConnectionStatusData,
	GetConnectionStatusError,
	GetConnectionStatusResponse,
	PostConnectionCustomData,
	PostConnectionCustomError,
	PostConnectionCustomResponse,
	PostConnectionDemoData,
	PostConnectionDemoError,
	PostConnectionDemoResponse,
} from "@/client";
import { API_URL } from "@/config";
import { APIError } from "./api-error";

interface APIResponse<T> {
	data: T;
	metadata: unknown | null;
}

export async function connect(): Promise<PostConnectionDemoResponse> {
	const payload: PostConnectionDemoData = {
		url: "/connection/demo",
	};
	const demoURL = `${API_URL}${payload.url}`;
	const requestOptions: RequestInit = {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		credentials: "include",
	};

	let response: Response;
	try {
		response = await fetch(demoURL, requestOptions);
	} catch {
		throw new APIError(0);
	}

	if (!response.ok) {
		const error: PostConnectionDemoError = await response
			.json()
			.catch(() => null);
		throw new APIError(response.status, error?.detail);
	}

	const success: APIResponse<PostConnectionDemoResponse> =
		await response.json();
	return success.data;
}

export async function connectCustom(
	config: ConnectionConfig,
): Promise<PostConnectionCustomResponse> {
	const payload: PostConnectionCustomData = {
		body: config,
		url: "/connection/custom",
	};
	const customURL = `${API_URL}${payload.url}`;
	const requestOptions: RequestInit = {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		credentials: "include",
		body: JSON.stringify(payload.body),
	};

	let response: Response;
	try {
		response = await fetch(customURL, requestOptions);
	} catch {
		throw new APIError(0);
	}

	if (!response.ok) {
		const error: PostConnectionCustomError = await response
			.json()
			.catch(() => null);
		throw new APIError(response.status, error?.detail);
	}

	const success: APIResponse<PostConnectionCustomResponse> =
		await response.json();
	return success.data;
}

export async function checkConnStatus(): Promise<GetConnectionStatusResponse> {
	const payload: GetConnectionStatusData = {
		url: "/connection/status",
	};
	const connStatusURL = `${API_URL}${payload.url}`;
	const requestOptions: RequestInit = {
		method: "GET",
		headers: { "Content-Type": "application/json" },
		credentials: "include",
	};

	let response: Response;
	try {
		response = await fetch(connStatusURL, requestOptions);
	} catch {
		throw new APIError(0);
	}

	if (!response.ok) {
		const error: GetConnectionStatusError = await response
			.json()
			.catch(() => null);
		throw new APIError(response.status, error?.detail);
	}

	const success: APIResponse<GetConnectionStatusResponse> =
		await response.json();
	return success.data;
}
