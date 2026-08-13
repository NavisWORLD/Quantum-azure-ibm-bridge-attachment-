package main

import (
	"context"
	"fmt"
	"math"
	"os"

	qbt "github.com/NavisWORLD/Quantum-azure-ibm-bridge-attachment-/bindings/go"
)

func main() {
	baseURL := "http://127.0.0.1:8766"
	if len(os.Args) > 1 {
		baseURL = os.Args[1]
	}
	client := qbt.New(baseURL)
	ctx := context.Background()

	health, err := client.Health(ctx)
	if err != nil || health["status"] != "ok" {
		panic(fmt.Sprintf("health failed: %v %#v", err, health))
	}

	sample, err := client.Sample(ctx, "simulator", 128, 7)
	if err != nil || sample.Packet.ActiveSources != 1 {
		panic(fmt.Sprintf("sample failed: %v %#v", err, sample))
	}

	normalized, err := client.Normalize(ctx, map[string]any{
		"provider": "go",
		"backend":  "smoke",
		"mode":     "simulator",
		"counts":   map[string]int{"0": 64, "1": 64},
		"shots":    128,
	})
	if err != nil || math.Abs(normalized.State.Entropy-1.0) > 1e-12 {
		panic(fmt.Sprintf("normalize failed: %v %#v", err, normalized))
	}

	fmt.Println("Go QBT smoke: OK")
}
