export class APIError extends Error {
	public readonly status: number;
	public readonly detail?: unknown;

	constructor(
		status: number, // 0 = network failure
		detail?: unknown, // raw backend detail, for logging/debugging
	) {
		super(`API request failed with status ${status}`);
		this.name = "APIError";
		this.status = status;
		this.detail = detail;
	}
}

export class MalformedJSON extends Error {
	constructor() {
		super("The server returned invalid JSON.");
		this.name = "MalformedJSON";
	}
}
