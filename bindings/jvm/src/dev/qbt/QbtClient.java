package dev.qbt;

import java.io.IOException;
import java.net.URI;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;

public final class QbtClient {
    private final String baseUrl;
    private final String token;
    private final HttpClient http;

    public QbtClient(String baseUrl) {
        this(baseUrl, "");
    }

    public QbtClient(String baseUrl, String token) {
        String value = (baseUrl == null || baseUrl.isBlank())
                ? "http://127.0.0.1:8766"
                : baseUrl;
        this.baseUrl = value.endsWith("/") ? value.substring(0, value.length() - 1) : value;
        this.token = token == null ? "" : token;
        this.http = HttpClient.newHttpClient();
    }

    public String health() throws IOException, InterruptedException {
        return request("GET", "/health", null);
    }

    public String status(String provider, int seed) throws IOException, InterruptedException {
        String path = "/v1/status?provider="
                + URLEncoder.encode(provider, StandardCharsets.UTF_8)
                + "&seed=" + seed;
        return request("GET", path, null);
    }

    public String sample(String provider, int shots, int seed)
            throws IOException, InterruptedException {
        String body = "{\"provider\":\"" + jsonEscape(provider)
                + "\",\"shots\":" + shots + ",\"seed\":" + seed + "}";
        return request("POST", "/v1/sample", body);
    }

    public String normalize(String jsonBody) throws IOException, InterruptedException {
        return request("POST", "/v1/normalize", jsonBody);
    }

    private String request(String method, String path, String body)
            throws IOException, InterruptedException {
        HttpRequest.Builder builder = HttpRequest.newBuilder(URI.create(baseUrl + path))
                .header("Accept", "application/json");
        if (!token.isBlank()) {
            builder.header("Authorization", "Bearer " + token);
        }
        if (body == null) {
            builder.GET();
        } else {
            builder.header("Content-Type", "application/json");
            builder.method(method, HttpRequest.BodyPublishers.ofString(body));
        }
        HttpResponse<String> response = http.send(
                builder.build(), HttpResponse.BodyHandlers.ofString(StandardCharsets.UTF_8));
        if (response.statusCode() < 200 || response.statusCode() >= 300) {
            throw new IOException("QBT HTTP " + response.statusCode() + ": " + response.body());
        }
        return response.body();
    }

    private static String jsonEscape(String value) {
        return value.replace("\\", "\\\\").replace("\"", "\\\"");
    }
}
