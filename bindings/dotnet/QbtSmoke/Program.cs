using System.Net.Http.Headers;
using System.Net.Http.Json;
using System.Text.Json;

public static class Program
{
    public static async Task Main(string[] args)
    {
        var baseUrl = args.Length > 0 ? args[0] : "http://127.0.0.1:8766";
        using var client = new QbtClient(baseUrl);

        using var health = await client.HealthAsync();
        if (health.RootElement.GetProperty("status").GetString() != "ok")
            throw new InvalidOperationException("QBT health contract failed");

        using var sample = await client.SampleAsync("simulator", 128, 7);
        if (sample.RootElement.GetProperty("packet").GetProperty("active_sources").GetInt32() != 1)
            throw new InvalidOperationException("QBT sample contract failed");

        using var normalized = await client.NormalizeAsync(new
        {
            provider = "dotnet",
            backend = "smoke",
            mode = "simulator",
            counts = new Dictionary<string, int> { ["0"] = 64, ["1"] = 64 },
            shots = 128,
        });
        var entropy = normalized.RootElement.GetProperty("state").GetProperty("entropy").GetDouble();
        if (Math.Abs(entropy - 1.0) > 1e-12)
            throw new InvalidOperationException("QBT normalize contract failed");

        Console.WriteLine("C#/.NET QBT smoke: OK");
    }
}

public sealed class QbtClient : IDisposable
{
    private readonly string _baseUrl;
    private readonly HttpClient _http = new();

    public QbtClient(string baseUrl, string? token = null)
    {
        _baseUrl = (string.IsNullOrWhiteSpace(baseUrl) ? "http://127.0.0.1:8766" : baseUrl).TrimEnd('/');
        if (!string.IsNullOrWhiteSpace(token))
            _http.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", token);
    }

    public Task<JsonDocument> HealthAsync() => SendAsync(HttpMethod.Get, "/health", null);

    public Task<JsonDocument> SampleAsync(string provider, int shots, int seed) =>
        SendAsync(HttpMethod.Post, "/v1/sample", new { provider, shots, seed });

    public Task<JsonDocument> NormalizeAsync(object payload) =>
        SendAsync(HttpMethod.Post, "/v1/normalize", payload);

    private async Task<JsonDocument> SendAsync(HttpMethod method, string path, object? body)
    {
        using var request = new HttpRequestMessage(method, _baseUrl + path);
        request.Headers.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
        if (body is not null)
            request.Content = JsonContent.Create(body);

        using var response = await _http.SendAsync(request);
        var text = await response.Content.ReadAsStringAsync();
        if (!response.IsSuccessStatusCode)
            throw new HttpRequestException($"QBT HTTP {(int)response.StatusCode}: {text}");
        return JsonDocument.Parse(text);
    }

    public void Dispose() => _http.Dispose();
}
