import { Anchor, Card, Stack, Text, Title } from "@mantine/core";
import { Link } from "react-router";

const NotFoundPage = () => (
    <Card>
        <Stack gap="xs">
            <Title order={3}>Page not found</Title>
            <Text c="dimmed">This page does not exist.</Text>
            <Anchor component={Link} to="/">Go home</Anchor>
        </Stack>
    </Card>
);

export default NotFoundPage;
