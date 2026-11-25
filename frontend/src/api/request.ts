import { apiUrl } from "../config/env";

// Sends a request to the backend. Returns the response if it is OK;
// otherwise throws an Error with the message from the API.
export async function request(path: string, init: RequestInit = {}) {
    let response: Response;
    try {
        response = await fetch(`${apiUrl}${path}`, init);
    } catch (err) {
        if (init.signal?.aborted) throw err;
        throw new Error("The backend is not reachable");
    }
    if (!response.ok) {
        const body = await response.json().catch(() => ({}));
        throw new Error(body.detail ?? `Backend: HTTP ${response.status}`);
    }
    return response;
}
