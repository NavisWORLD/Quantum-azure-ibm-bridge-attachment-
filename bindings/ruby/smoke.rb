require_relative 'qbt_client'

base_url = ARGV[0] || 'http://127.0.0.1:8766'
client = QbtClient.new(base_url)

health = client.health
raise 'QBT health contract failed' unless health['status'] == 'ok'

sample = client.sample(provider: 'simulator', shots: 128, seed: 7)
raise 'QBT sample contract failed' unless sample.dig('packet', 'active_sources') == 1

normalized = client.normalize(
  provider: 'ruby',
  backend: 'smoke',
  mode: 'simulator',
  counts: { '0' => 64, '1' => 64 },
  shots: 128
)
raise 'QBT normalize contract failed' unless (normalized.dig('state', 'entropy') - 1.0).abs < 1e-12

puts 'Ruby QBT smoke: OK'
