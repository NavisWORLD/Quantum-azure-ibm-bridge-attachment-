import SwiftUI

struct ContentView: View {
    @AppStorage("endpoint") private var endpoint = "http://192.168.1.2:8766"
    @AppStorage("token") private var token = ""
    @State private var output = "Connect to your QBT sidecar, then run Health or Sample."
    @State private var working = false

    var body: some View {
        ZStack {
            LinearGradient(colors: [Color(red: 0.03, green: 0.07, blue: 0.12), Color(red: 0.05, green: 0.12, blue: 0.20)], startPoint: .topLeading, endPoint: .bottomTrailing)
                .ignoresSafeArea()
            ScrollView {
                VStack(alignment: .leading, spacing: 18) {
                    Text("Quantum Bridge Transformer")
                        .font(.system(size: 30, weight: .bold, design: .rounded))
                        .foregroundStyle(.white)
                    Text("Secure mobile control surface for your own QBT sidecar.")
                        .foregroundStyle(Color(red: 0.52, green: 0.70, blue: 0.90))

                    VStack(alignment: .leading, spacing: 12) {
                        Text("Connection").font(.headline).foregroundStyle(.white)
                        TextField("Sidecar URL", text: $endpoint)
                            .textInputAutocapitalization(.never)
                            .autocorrectionDisabled()
                            .padding(12)
                            .background(Color.white.opacity(0.08), in: RoundedRectangle(cornerRadius: 12))
                            .foregroundStyle(.white)
                        SecureField("Bearer token", text: $token)
                            .padding(12)
                            .background(Color.white.opacity(0.08), in: RoundedRectangle(cornerRadius: 12))
                            .foregroundStyle(.white)
                        HStack {
                            Button("Health") { run(path: "/health", body: nil) }
                                .buttonStyle(QBTButtonStyle())
                            Button("Sample") {
                                run(path: "/v1/sample", body: ["provider": "simulator", "shots": 1024, "seed": 42])
                            }
                            .buttonStyle(QBTButtonStyle())
                        }
                    }
                    .padding(18)
                    .background(Color.white.opacity(0.06), in: RoundedRectangle(cornerRadius: 20))

                    Text("Result").font(.headline).foregroundStyle(.white)
                    ScrollView(.horizontal) {
                        Text(output)
                            .font(.system(.footnote, design: .monospaced))
                            .foregroundStyle(Color(red: 0.86, green: 0.95, blue: 1.0))
                            .textSelection(.enabled)
                            .padding(16)
                    }
                    .frame(maxWidth: .infinity, minHeight: 220, alignment: .topLeading)
                    .background(Color.black.opacity(0.28), in: RoundedRectangle(cornerRadius: 16))

                    Text("BYOK: no IBM or Azure credentials are bundled. Protect non-loopback sidecars with QBT_SIDECAR_TOKEN and prefer HTTPS outside a trusted local network.")
                        .font(.footnote)
                        .foregroundStyle(Color(red: 0.52, green: 0.70, blue: 0.90))
                }
                .padding(22)
            }
            if working {
                ProgressView().tint(.white).scaleEffect(1.2)
            }
        }
    }

    private func run(path: String, body: [String: Any]?) {
        guard let url = URL(string: endpoint.trimmingCharacters(in: .whitespacesAndNewlines).trimmingCharacters(in: CharacterSet(charactersIn: "/")) + path) else {
            output = "Invalid sidecar URL"
            return
        }
        working = true
        Task {
            do {
                var request = URLRequest(url: url)
                request.httpMethod = body == nil ? "GET" : "POST"
                request.setValue("application/json", forHTTPHeaderField: "Accept")
                if !token.isEmpty { request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization") }
                if let body {
                    request.setValue("application/json", forHTTPHeaderField: "Content-Type")
                    request.httpBody = try JSONSerialization.data(withJSONObject: body)
                }
                let (data, response) = try await URLSession.shared.data(for: request)
                let code = (response as? HTTPURLResponse)?.statusCode ?? 0
                let object = try? JSONSerialization.jsonObject(with: data)
                if let object, let pretty = try? JSONSerialization.data(withJSONObject: object, options: [.prettyPrinted, .sortedKeys]), let text = String(data: pretty, encoding: .utf8) {
                    output = text
                } else {
                    output = "HTTP \(code)\n" + (String(data: data, encoding: .utf8) ?? "")
                }
            } catch {
                output = "Error: \(error.localizedDescription)"
            }
            working = false
        }
    }
}

private struct QBTButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .fontWeight(.semibold)
            .frame(maxWidth: .infinity)
            .padding(.vertical, 12)
            .foregroundStyle(.white)
            .background(Color(red: 0.16, green: 0.39, blue: 0.66).opacity(configuration.isPressed ? 0.65 : 1), in: RoundedRectangle(cornerRadius: 13))
    }
}
