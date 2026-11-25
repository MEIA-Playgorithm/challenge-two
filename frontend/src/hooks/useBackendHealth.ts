import { useEffect, useState } from "react";
import { getHealth } from "../api/health";

export type Status = { kind: "checking" } | { kind: "online"; version: string } | { kind: "offline" };

// Checks GET /health once and returns the backend status.
const useBackendHealth = (): Status => {
    const [status, setStatus] = useState<Status>({ kind: "checking" });

    useEffect(() => {
        const controller = new AbortController();
        getHealth(controller.signal)
            .then((health) => setStatus({ kind: "online", version: health.version }))
            .catch(() => {
                if (!controller.signal.aborted) setStatus({ kind: "offline" });
            });
        return () => controller.abort();
    }, []);

    return status;
};

export default useBackendHealth;
