require 'json'
require 'net/http'
require 'uri'

class QbtClient
  def initialize(base_url = 'http://127.0.0.1:8766', token = nil)
    @base_url = base_url.sub(%r{/$}, '')
    @token = token
  end

  def health
    request('GET', '/health')
  end

  def sample(provider: 'simulator', shots: 1024, seed: 42)
    request('POST', '/v1/sample', provider: provider, shots: shots, seed: seed)
  end

  def normalize(payload)
    request('POST', '/v1/normalize', payload)
  end

  private

  def request(method, path, payload = nil)
    uri = URI(@base_url + path)
    request = method == 'POST' ? Net::HTTP::Post.new(uri) : Net::HTTP::Get.new(uri)
    request['Accept'] = 'application/json'
    request['Authorization'] = "Bearer #{@token}" if @token && !@token.empty?
    if payload
      request['Content-Type'] = 'application/json'
      request.body = JSON.generate(payload)
    end

    response = Net::HTTP.start(uri.hostname, uri.port, use_ssl: uri.scheme == 'https') do |http|
      http.request(request)
    end
    unless response.is_a?(Net::HTTPSuccess)
      raise "QBT HTTP #{response.code}: #{response.body}"
    end
    JSON.parse(response.body)
  end
end
