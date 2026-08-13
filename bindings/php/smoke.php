<?php

declare(strict_types=1);

require __DIR__ . '/QbtClient.php';

$baseUrl = $argv[1] ?? 'http://127.0.0.1:8766';
$client = new QbtClient($baseUrl);

$health = $client->health();
if (($health['status'] ?? null) !== 'ok') {
    throw new RuntimeException('QBT health contract failed');
}

$sample = $client->sample('simulator', 128, 7);
if (($sample['packet']['active_sources'] ?? null) !== 1) {
    throw new RuntimeException('QBT sample contract failed');
}

$normalized = $client->normalize([
    'provider' => 'php',
    'backend' => 'smoke',
    'mode' => 'simulator',
    'counts' => ['0' => 64, '1' => 64],
    'shots' => 128,
]);
if (abs((float) ($normalized['state']['entropy'] ?? -1.0) - 1.0) > 1e-12) {
    throw new RuntimeException('QBT normalize contract failed');
}

echo "PHP QBT smoke: OK\n";
