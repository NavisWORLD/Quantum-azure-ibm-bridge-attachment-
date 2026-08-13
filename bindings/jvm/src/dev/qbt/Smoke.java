package dev.qbt;

public final class Smoke {
    private Smoke() {}

    public static void main(String[] args) throws Exception {
        String baseUrl = args.length > 0 ? args[0] : "http://127.0.0.1:8766";
        QbtClient client = new QbtClient(baseUrl);

        String health = client.health();
        if (!health.contains("\"status\": \"ok\"") && !health.contains("\"status\":\"ok\"")) {
            throw new IllegalStateException("QBT health contract failed: " + health);
        }

        String sample = client.sample("simulator", 128, 7);
        if (!sample.contains("\"active_sources\": 1")
                && !sample.contains("\"active_sources\":1")) {
            throw new IllegalStateException("QBT sample contract failed: " + sample);
        }

        String normalized = client.normalize(
                "{\"provider\":\"java\",\"backend\":\"smoke\",\"mode\":\"simulator\","
                        + "\"counts\":{\"0\":64,\"1\":64},\"shots\":128}");
        if (!normalized.contains("\"entropy\": 1.0")
                && !normalized.contains("\"entropy\":1.0")) {
            throw new IllegalStateException("QBT normalize contract failed: " + normalized);
        }

        System.out.println("Java/Kotlin QBT smoke: OK");
    }
}
