export type Page = { key: string; path: string; label: string; description: string };

// Single source for the router, the breadcrumbs and the landing cards.
export const pages = [
    { key: "home", path: "/", label: "Home", description: "Overview of Playgorithm." },
    { key: "predictions", path: "/predictions", label: "Predictions", description: "Forecast player and team performance." },
    { key: "planning", path: "/planning", label: "Planning", description: "Plan lineups and training for your team." },
] as const satisfies readonly Page[];

export type PagePath = (typeof pages)[number]["path"];

export const getPage = <P extends PagePath>(path: P) =>
    pages.find((page) => page.path === path) as Extract<(typeof pages)[number], { path: P }>;
