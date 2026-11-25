import { Anchor, Breadcrumbs, Card, Container, createTheme, Title, type CSSVariablesResolver, type MantineColorsTuple } from "@mantine/core";

// Mint accent from the team blog (index 6 is the primary shade #2ef2b3, 7 is the darker #2ac79a).
const mint: MantineColorsTuple = [
    "#e6fff7",
    "#cfeee5",
    "#a6f7de",
    "#7af5d0",
    "#52f3c1",
    "#3df2b8",
    "#2ef2b3",
    "#2ac79a",
    "#1fa07c",
    "#167a5e",
];

// Dark scheme: 0 text, 2 dimmed text (#8fb3a9), 6 card surface, 7 page background.
const dark: MantineColorsTuple = [
    "#ffffff",
    "#cfeee5",
    "#8fb3a9",
    "#6b8c83",
    "#2f4a43",
    "#223a34",
    "#0f1e1b",
    "#061713",
    "#04100d",
    "#030b09",
];

// Extra design tokens, exposed as CSS variables by cssVariablesResolver below.
const other = {
    headerBackground: "rgba(5, 10, 12, 0.7)",
    mintBorder: "rgba(46, 242, 179, 0.22)",
    headerBlur: "saturate(180%) blur(20px)",
    heroTitleBase: "36px",
    heroTitleSm: "56px",
};

export const cssVariablesResolver: CSSVariablesResolver = (theme) => ({
    variables: {
        "--app-header-background": theme.other.headerBackground,
        "--app-header-blur": theme.other.headerBlur,
        "--app-mint-border": theme.other.mintBorder,
        "--app-hero-title-size-base": theme.other.heroTitleBase,
        "--app-hero-title-size-sm": theme.other.heroTitleSm,
    },
    light: {},
    dark: {},
});

const theme = createTheme({
    colors: { mint, dark },
    other,
    primaryColor: "mint",
    primaryShade: 6,
    autoContrast: true,
    black: "#061713",
    white: "#ffffff",
    fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, Helvetica, Arial, sans-serif',
    headings: {
        fontWeight: "600",
        sizes: {
            h1: { fontSize: "clamp(1.75rem, 1.2rem + 2vw, 2.5rem)", lineHeight: "1.15" },
        },
    },
    defaultRadius: "lg",
    radius: { lg: "18px" },
    components: {
        Anchor: Anchor.extend({
            styles: { root: { cursor: "pointer" } },
        }),
        Breadcrumbs: Breadcrumbs.extend({
            defaultProps: { separator: "›", separatorMargin: "xs", c: "dimmed" },
        }),
        Title: Title.extend({
            defaultProps: { lts: "-0.02em" },
        }),
        Card: Card.extend({
            defaultProps: { padding: "xl", radius: "lg", shadow: "sm", bd: "1px solid var(--app-mint-border)" },
        }),
        Container: Container.extend({
            defaultProps: { size: "lg" },
        }),
    },
});

export default theme;
