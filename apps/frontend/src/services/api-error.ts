export class APIError extends Error {
	public status: number;
	public detail?: unknown;

	constructor(
		status: number, // 0 = network failure
		detail?: unknown, // raw backend detail, for logging/debugging
	) {
		super(`API error ${status}`);
		this.status = status;
		this.detail = detail;
	}
}
