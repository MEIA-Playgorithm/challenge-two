import { matchPath, useLocation } from "react-router";
import { pages } from "../config/navigation";

// The page that matches the current URL, or undefined for an unknown path.
export const useCurrentPage = () => {
    const { pathname } = useLocation();
    return pages.find((page) => matchPath(page.path, pathname));
};
