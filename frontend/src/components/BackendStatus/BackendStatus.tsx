import { Badge, Box, Text } from "@mantine/core";
import useBackendHealth from "../../hooks/useBackendHealth";
import classes from "./BackendStatus.module.css";

// Shows whether the backend answers GET /health. Short label on mobile, full label from sm.
const BackendStatus = () => {
    const status = useBackendHealth();
    const [color, short, full] =
        status.kind === "checking" ? ["gray", "Checking", "Backend: checking"]
        : status.kind === "offline" ? ["red", "Offline", "Backend: offline"]
        : ["mint", "Online", `Backend: online (v${status.version})`];

    return (
        <Badge
            variant="light"
            color={color}
            tt="none"
            fw={500}
            leftSection={<Box className={classes.dot} />}
        >
            <Text span inherit hiddenFrom="sm">{short}</Text>
            <Text span inherit visibleFrom="sm">{full}</Text>
        </Badge>
    );
};

export default BackendStatus;
