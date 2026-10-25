import { APIError, MalformedJSON } from "@/errors/error-type";

const ERROR_MESSAGES = {
  UNEXPECTED: "An unexpected error occurred. Please try again later.",
  INVALID_RESPONSE: "The server returned an invalid response.",
} as const;

const API_ERROR_DEFAULTS: Record<number, string> = {
  0: "Network failure. Please check your connection.",
  400: "Bad request. Please check your input and try again.",
  401: "Unauthorized access. Your session may have expired. Please log in again.",
  429: "Too many attempts. Please wait a moment and try again.",
};

export function errorMessage(error: unknown, overrides: Record<number, string> = {}): string {
  if (error instanceof APIError) {
    const message = overrides[error.status] ?? API_ERROR_DEFAULTS[error.status];

    if (message) return message;

    if (error.status >= 500) {
      return "Something went wrong on our end. Please try again later.";
    }
  }

  if (error instanceof MalformedJSON) {
    return ERROR_MESSAGES.INVALID_RESPONSE;
  }

  return ERROR_MESSAGES.UNEXPECTED;
}
