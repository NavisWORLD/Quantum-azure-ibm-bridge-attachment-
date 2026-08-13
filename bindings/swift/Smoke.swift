import Foundation

@main
struct Smoke {
    static func main() async throws {
        let baseURL = CommandLine.arguments.count > 1
            ? CommandLine.arguments[1]
            : "http://127.0.0.1:8766"
        let client = try QbtClient(baseURL: baseURL)

        let health = try await client.health()
        guard health["status"] as? String == "ok" else {
            fatalError("QBT health contract failed")
        }

        let sample = try await client.sample(provider: "simulator", shots: 128, seed: 7)
        guard
            let packet = sample["packet"] as? [String: Any],
            packet["active_sources"] as? Int == 1
        else {
            fatalError("QBT sample contract failed")
        }

        let normalized = try await client.normalize([
            "provider": "swift",
            "backend": "smoke",
            "mode": "simulator",
            "counts": ["0": 64, "1": 64],
            "shots": 128,
        ])
        guard
            let state = normalized["state"] as? [String: Any],
            let entropy = state["entropy"] as? Double,
            abs(entropy - 1.0) < 1e-12
        else {
            fatalError("QBT normalize contract failed")
        }

        print("Swift QBT smoke: OK")
    }
}
