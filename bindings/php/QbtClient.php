<?php

declare(strict_types=1);

final class QbtClient
{
    public function __construct(
        private string $baseUrl = 'http://127.0.0.1:8766',
        private string $token = ''
    ) {
        $this->baseUrl = rtrim($this->baseUrl, '/');
    }

    public function health(): array
    {
        return $this->request('GET', '/health');
    }

    public function sample(string $provider = 'simulator', int $shots = 1024, int $seed = 42): array
    {
        return $this->request('POST', '/v1/sample', compact('provider', 'shots', 'seed'));
    }

    public function normalize(array $payload): array
    {
        if (isset($payload['counts']) && is_array($payload['counts'])) {
            // PHP converts numeric-string keys like "0" and "1" to integer
            // array keys. Casting to object preserves a JSON object count map
            // instead of emitting a JSON array such as [64,64].
            $payload['counts'] = (object) $payload['counts'];
        }
        return $this->request('POST', '/v1/normalize', $payload);
    }

    private function request(string $method, string $path, ?array $payload = null): array
    {
        $headers = ['Accept: application/json'];
        $content = '';
        if ($payload !== null) {
            $headers[] = 'Content-Type: application/json';
            $content = json_encode($payload, JSON_THROW_ON_ERROR);
        }
        if ($this->token !== '') {
            $headers[] = 'Authorization: Bearer ' . $this->token;
        }

        $context = stream_context_create([
            'http' => [
                'method' => $method,
                'header' => implode("\r\n", $headers),
                'content' => $content,
                'ignore_errors' => true,
                'timeout' => 5,
            ],
        ]);
        $body = file_get_contents($this->baseUrl . $path, false, $context);
        if ($body === false) {
            throw new RuntimeException('QBT request failed');
        }
        $status = 0;
        if (isset($http_response_header[0]) && preg_match('/\s(\d{3})\s/', $http_response_header[0], $matches)) {
            $status = (int) $matches[1];
        }
        if ($status < 200 || $status >= 300) {
            throw new RuntimeException("QBT HTTP {$status}: {$body}");
        }
        return json_decode($body, true, 512, JSON_THROW_ON_ERROR);
    }
}
