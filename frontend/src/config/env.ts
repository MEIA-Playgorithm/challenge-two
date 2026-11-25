// Backend address. Vite reads VITE_API_URL at build time.
export const apiUrl: string = import.meta.env.VITE_API_URL || "http://localhost:8000";
