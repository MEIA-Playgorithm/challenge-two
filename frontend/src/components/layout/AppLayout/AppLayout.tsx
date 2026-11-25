import { Anchor, AppShell, Box, Breadcrumbs, Container, Group, Text } from "@mantine/core";
import { Link, Outlet } from "react-router";
import BackendStatus from "../../BackendStatus/BackendStatus";
import Footer from "../Footer/Footer";
import { getPage } from "../../../config/navigation";
import { useCurrentPage } from "../../../hooks/useCurrentPage";
import classes from "./AppLayout.module.css";

// Shell with sticky translucent header (breadcrumbs as navigation) and the routed page.
const AppLayout = () => {
    const home = getPage("/");
    const page = useCurrentPage();
    const current = page?.key === home.key ? undefined : (page?.label ?? "Not found");

    return (
        <AppShell
            header={{ height: 56 }}
            classNames={{ header: classes.header }}
        >
            <AppShell.Header>
                <Container h="100%">
                    <Group h="100%" justify="space-between" wrap="nowrap">
                        <Box component="nav" aria-label="Breadcrumb" miw={0}>
                            <Breadcrumbs className={classes.breadcrumbs}>
                                <Anchor component={Link} to={home.path} fw={600} size="lg" c="white" aria-current={current ? undefined : "page"}>Playgorithm</Anchor>
                                {current && <Text c="white" truncate aria-current="page">{current}</Text>}
                            </Breadcrumbs>
                        </Box>
                        <BackendStatus />
                    </Group>
                </Container>
            </AppShell.Header>
            <AppShell.Main display="flex" className={classes.main}>
                <Container py="xl" w="100%" className={classes.content}>
                    <Outlet />
                </Container>
                <Footer />
            </AppShell.Main>
        </AppShell>
    );
};

export default AppLayout;
