import { API_URL } from "@/config";
import { APIError, MalformedJSON } from "@/errors/error-type";

type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";

// The body is typed from the generated request type: endpoints that declare a `body` require it,
// and endpoints that don't declare one reject it.
type RequestOptions<TRequest> = TRequest extends { body: infer B } ? { body: B } : { body?: never };

// The backend wraps every successful response as { data: ... }
interface APIResponse<TResponse> {
  data: TResponse;
}

// A body that contains a file must be sent as multipart/form-data, not JSON
function isMultipart(body: unknown): body is Record<string, unknown> {
  return (
    typeof body === "object" &&
    body !== null &&
    Object.values(body).some((value) => value instanceof Blob)
  );
}

function toFormData(body: Record<string, unknown>): FormData {
  const formData = new FormData();
  for (const [key, value] of Object.entries(body)) {
    if (value instanceof Blob) formData.append(key, value);
    else if (typeof value === "string") formData.append(key, value);
    else if (value != null) formData.append(key, JSON.stringify(value)); // numbers, booleans, objects
  }
  return formData;
}

// Decides how to send the body and which headers go with it:
// - no body: nothing to send, so no Content-Type
// - contains a file: send FormData and let the browser set the Content-Type header, because it
//   has to include a boundary string that we can't know in advance
// - everything else: send JSON
function encodeBody(body: unknown): { payload?: BodyInit; headers: Record<string, string> } {
  if (body === undefined) return { headers: {} };
  if (isMultipart(body)) return { payload: toFormData(body), headers: {} };
  return { payload: JSON.stringify(body), headers: { "Content-Type": "application/json" } };
}

/**
 * Typed wrapper around fetch for the backend API.
 *
 * TRequest is the generated request type for an endpoint and drives two checks: `path` must match
 * the endpoint's URL, and the options argument is required only when the endpoint takes a body.
 * TResponse is the type of the unwrapped `data` field that gets returned.
 *
 * Failures are converted to typed errors: APIError for network and HTTP failures (status 0 means
 * the request never reached the server), and MalformedJSON for an unparseable success response.
 */
export async function fetchAPI<TRequest extends { url: string }, TResponse>(
  method: HttpMethod,
  path: TRequest["url"],
  // Rest-tuple trick: this makes the whole options argument required or optional depending on
  // whether TRequest declares a body
  ...args: TRequest extends { body: unknown }
    ? [options: RequestOptions<TRequest>]
    : [options?: RequestOptions<TRequest>]
): Promise<TResponse> {
  // The cast is needed because TypeScript can't prove the `{}` fallback matches the conditional type
  const options = (args[0] ?? {}) as RequestOptions<TRequest>;
  const { payload, headers } = encodeBody("body" in options ? options.body : undefined);

  let response: Response;

  try {
    response = await fetch(`${API_URL}${path}`, {
      method,
      headers,
      body: payload,
      credentials: "include", // send the session cookie on cross-origin requests
    });
  } catch {
    throw new APIError(0); // Usually network error
  }

  if (!response.ok) {
    // The error body may not be JSON (e.g. an HTML page from a proxy), so parsing is allowed to fail
    const error: unknown = await response.json().catch(() => null);
    const detail =
      typeof error === "object" && error !== null && "detail" in error ? error.detail : undefined;
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
