import type { ReactElement } from "react";
import { MantineProvider } from "@mantine/core";
import { BrowserRouter, Route, Routes } from "react-router";
import AppLayout from "../components/layout/AppLayout/AppLayout";
import { pages, type PagePath } from "../config/navigation";
import HomePage from "../pages/HomePage/HomePage";
import NotFoundPage from "../pages/NotFoundPage/NotFoundPage";
import PlanningPage from "../pages/PlanningPage/PlanningPage";
import PredictionsPage from "../pages/PredictionsPage/PredictionsPage";
import theme, { cssVariablesResolver } from "../theme/theme";

// Page component for each path in navigation.ts.
const elements: Record<PagePath, ReactElement> = {
    "/": <HomePage />,
    "/predictions": <PredictionsPage />,
    "/planning": <PlanningPage />,
};

const App = () => (
    <MantineProvider theme={theme} cssVariablesResolver={cssVariablesResolver} forceColorScheme="dark">
        <BrowserRouter>
            <Routes>
                <Route element={<AppLayout />}>
                    {pages.map((page) => (
                        <Route key={page.path} path={page.path} element={elements[page.path]} />
                    ))}
                    <Route path="*" element={<NotFoundPage />} />
                </Route>
            </Routes>
        </BrowserRouter>
    </MantineProvider>
);

export default App;
