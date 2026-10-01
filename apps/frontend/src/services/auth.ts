import type {
	PostAuthLoginData,
	PostAuthLoginResponse,
	PostAuthOtpData,
	PostAuthOtpResponse,
} from "@/client";
import { API_URL } from "@/config";

interface APIResponse<T> {
	data: T;
	metadata: unknown | null;
}

export async function sendOTP(
	email: string,
): Promise<APIResponse<PostAuthOtpResponse>> {
	const payload: PostAuthOtpData = {
		body: {
			email: email,
		},
		url: "/auth/otp",
	};
	const loginURL = `${API_URL}${payload.url}`;
	const requestOptions: RequestInit = {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify(payload.body),
	};
	const response = await fetch(loginURL, requestOptions);
	return await response.json();
}

export async function login(
	email: string,
	otp: string,
): Promise<PostAuthLoginResponse> {
	const payload: PostAuthLoginData = {
		body: {
			email: email,
			code: otp,
		},
		url: "/auth/login",
	};
	const loginURL = `${API_URL}${payload.url}`;
	const requestOptions: RequestInit = {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify(payload.body),
	};
	const response = await fetch(loginURL, requestOptions);
	return await response.json();
}
