import { Card, SimpleGrid, Stack, Text, Title } from "@mantine/core";
import { Link } from "react-router";
import { pages } from "../../config/navigation";
import classes from "./HomePage.module.css";

// Landing page: hero and one clickable card per other page.
const HomePage = () => (
    <Stack gap="xl">
        <Stack gap="xs" ta="center" py="xl">
            <Title order={1} className={classes.heroTitle}>Playgorithm</Title>
            <Text fz={{ base: "lg", sm: "xl" }} c="dimmed">A management system for basketball coaches.</Text>
        </Stack>
        <SimpleGrid cols={{ base: 1, sm: 2 }} spacing="lg">
            {pages.filter((page) => page.key !== "home").map((page) => (
                <Card key={page.path} component={Link} to={page.path}>
                    <Stack gap="xs">
                        <Title order={3}>{page.label}</Title>
                        <Text c="dimmed">{page.description}</Text>
                        <Text c="mint" mt="sm">Open ›</Text>
                    </Stack>
                </Card>
            ))}
        </SimpleGrid>
    </Stack>
);

export default HomePage;
