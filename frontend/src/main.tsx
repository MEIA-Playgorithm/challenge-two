import "@mantine/core/styles.css";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./app/App";
import { loadConfig } from "./config/config";

const root = createRoot(document.getElementById("root")!);

// The configuration (the backend URL) must load before the app starts.
loadConfig()
    .then(() =>
        root.render(
            <StrictMode>
                <App />
            </StrictMode>
        )
    )
    .catch((err: Error) => root.render(<p>{err.message}</p>));
