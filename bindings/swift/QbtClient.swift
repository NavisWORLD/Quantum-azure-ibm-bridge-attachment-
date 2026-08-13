import Foundation

struct QbtClient {
    let baseURL: URL
    let token: String?

    init(baseURL: String = "http://127.0.0.1:8766", token: String? = nil) throws {
        guard let url = URL(string: baseURL.trimmingCharacters(in: CharacterSet(charactersIn: "/"))) else {
            throw URLError(.badURL)
        }
        self.baseURL = url
        self.token = token
    }

    func health() async throws -> [String: Any] {
        try await request(path: "/health", method: "GET", body: nil)
    }

    func sample(provider: String = "simulator", shots: Int = 1024, seed: Int = 42) async throws -> [String: Any] {
        try await request(
            path: "/v1/sample",
            method: "POST",
            body: ["provider": provider, "shots": shots, "seed": seed]
        )
    }

    func normalize(_ payload: [String: Any]) async throws -> [String: Any] {
        try await request(path: "/v1/normalize", method: "POST", body: payload)
    }

    private func request(path: String, method: String, body: [String: Any]?) async throws -> [String: Any] {
        guard let url = URL(string: path, relativeTo: baseURL) else {
            throw URLError(.badURL)
        }
        var request = URLRequest(url: url)
        request.httpMethod = method
        request.setValue("application/json", forHTTPHeaderField: "Accept")
        if let token, !token.isEmpty {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        if let body {
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")
            request.httpBody = try JSONSerialization.data(withJSONObject: body)
        }

        let (data, response) = try await URLSession.shared.data(for: request)
        guard let http = response as? HTTPURLResponse, (200..<300).contains(http.statusCode) else {
            let text = String(data: data, encoding: .utf8) ?? ""
            throw NSError(domain: "QBT", code: 1, userInfo: [NSLocalizedDescriptionKey: text])
        }
        guard let value = try JSONSerialization.jsonObject(with: data) as? [String: Any] else {
            throw NSError(domain: "QBT", code: 2, userInfo: [NSLocalizedDescriptionKey: "non-object JSON"])
        }
        return value
    }
}
