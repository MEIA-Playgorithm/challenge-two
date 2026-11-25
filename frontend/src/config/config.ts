type Config = {
    apiUrl: string;
};

// Read from /config.json before the app starts (see main.tsx).
export let config: Config;

export async function loadConfig() {
    const response = await fetch("/config.json");
    if (!response.ok) throw new Error(`Could not load config.json (HTTP ${response.status})`);
    config = await response.json();
}
