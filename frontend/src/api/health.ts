import { request } from "./request";
import { routes } from "./routes";

export type Health = {
    status: string;
    version: string;
};

export async function getHealth(signal?: AbortSignal): Promise<Health> {
    const response = await request(routes.health, { signal });
    return response.json();
}
