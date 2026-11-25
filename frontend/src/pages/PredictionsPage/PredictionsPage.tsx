import { Card, Stack, Text, Title } from "@mantine/core";
import { getPage } from "../../config/navigation";

// Placeholder page.
const PredictionsPage = () => {
    const page = getPage("/predictions");
    return (
        <Stack gap="lg">
            <Stack gap={4}>
                <Title order={1}>{page.label}</Title>
                <Text size="lg" c="dimmed">{page.description}</Text>
            </Stack>
            <Card>
                <Text c="dimmed">Coming soon. Forecasts will appear here.</Text>
            </Card>
        </Stack>
    );
};

export default PredictionsPage;
