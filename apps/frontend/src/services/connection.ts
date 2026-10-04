import type {
	ConnectionConfig,
	DeleteConnectionData,
	GetConnectionStatusData,
	GetConnectionStatusResponse,
	PostConnectionCustomData,
	PostConnectionCustomResponse,
	PostConnectionDemoData,
	PostConnectionDemoResponse,
	PostConnectionQueryData,
	PostConnectionQueryResponse,
} from "@/client";
import { fetchAPI } from "./api";

export async function connectDemo(): Promise<PostConnectionDemoResponse> {
	return await fetchAPI<PostConnectionDemoData, PostConnectionDemoResponse>(
		"POST",
		"/connection/demo",
	);
}

export async function connectCustom(
	config: ConnectionConfig,
	accessToken?: string,
): Promise<PostConnectionCustomResponse> {
	return await fetchAPI<PostConnectionCustomData, PostConnectionCustomResponse>(
		"POST",
		"/connection/custom",
		{
			body: config,
			accessToken: accessToken,
		},
	);
}

export async function checkConnStatus(): Promise<GetConnectionStatusResponse> {
	return await fetchAPI<GetConnectionStatusData, GetConnectionStatusResponse>(
		"GET",
		"/connection/status",
	);
}

export async function disconnect(): Promise<void> {
	// API returns 204 No Content on successful disconnect
	await fetchAPI<DeleteConnectionData, void>("DELETE", "/connection");
}

export async function query(
	prompt: string,
): Promise<PostConnectionQueryResponse> {
	return await fetchAPI<PostConnectionQueryData, PostConnectionQueryResponse>(
		"POST",
		"/connection/query",
		{
			body: {
				prompt: prompt,
			},
		},
	);
}
