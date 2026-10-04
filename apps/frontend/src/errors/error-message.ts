import { APIError } from "@/errors/api-error";

const DEFAULTS: Record<number, string> = {
	0: "Network failure. Please check your connection.",
	400: "Bad request. Please check your input and try again.",
	401: "Unauthorized access. Your session may have expired. Please log in again.",
	429: "Too many attempts. Please wait a moment and try again.",
};

export function errorMessage(
	error: unknown,
	overrides: Record<number, string> = {},
): string {
	if (error instanceof APIError) {
		const msg = overrides[error.status] ?? DEFAULTS[error.status];
		if (msg) return msg;
		if (error.status >= 500)
			return "There was a problem within PersV. Please try again later.";
	}
	return "An unexpected error occured. Please try again later.";
}
