import { Anchor, Text } from "@mantine/core";

const BLOG_URL = "https://playgorithm.blogspot.com";

const Footer = () => (
    <Text component="footer" size="xs" c="dimmed" ta="center" py="md">
        © 2026 Playgorithm · <Anchor href={BLOG_URL} target="_blank" rel="noopener noreferrer" inherit underline="hover">Blog</Anchor>
    </Text>
);

export default Footer;
