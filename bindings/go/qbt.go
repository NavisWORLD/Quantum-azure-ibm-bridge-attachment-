package qbt

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"strings"
)

type Quality struct {
	QualityClass string   `json:"quality_class"`
	Confidence   *float64 `json:"confidence"`
}

type QuantumState struct {
	QBTVersion       string         `json:"qbt_version"`
	Provider         string         `json:"provider"`
	Backend          string         `json:"backend"`
	ExecutionMode    string         `json:"execution_mode"`
	Timestamp        string         `json:"timestamp"`
	JobID            *string        `json:"job_id"`
	Shots            int            `json:"shots"`
	Entropy          float64        `json:"entropy"`
	NormalizedVector []float64      `json:"normalized_vector"`
	ResultDigest     string         `json:"result_digest"`
	Provenance       map[string]any `json:"provenance"`
	Quality          Quality        `json:"quality"`
}

type ControlPacket struct {
	QBTVersion     string            `json:"qbt_version"`
	ActiveSources  int               `json:"active_sources"`
	QuantumMix     float64           `json:"quantum_mix"`
	States         []QuantumState    `json:"states"`
	ProviderErrors map[string]string `json:"provider_errors"`
}

type SampleResponse struct {
	Connection map[string]any `json:"connection"`
	Packet     ControlPacket  `json:"packet"`
}

type NormalizeResponse struct {
	State QuantumState `json:"state"`
}

type Client struct {
	BaseURL    string
	Token      string
	HTTPClient *http.Client
}

func New(baseURL string) *Client {
	if baseURL == "" {
		baseURL = "http://127.0.0.1:8766"
	}
	return &Client{
		BaseURL:    strings.TrimRight(baseURL, "/"),
		HTTPClient: http.DefaultClient,
	}
}

func (c *Client) request(ctx context.Context, method, path string, body any, out any) error {
	var reader io.Reader
	if body != nil {
		data, err := json.Marshal(body)
		if err != nil {
			return err
		}
		reader = bytes.NewReader(data)
	}
	req, err := http.NewRequestWithContext(ctx, method, c.BaseURL+path, reader)
	if err != nil {
		return err
	}
	req.Header.Set("Accept", "application/json")
	if body != nil {
		req.Header.Set("Content-Type", "application/json")
	}
	if c.Token != "" {
		req.Header.Set("Authorization", "Bearer "+c.Token)
	}

	resp, err := c.HTTPClient.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	data, err := io.ReadAll(resp.Body)
	if err != nil {
		return err
	}
	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		return fmt.Errorf("QBT HTTP %d: %s", resp.StatusCode, string(data))
	}
	return json.Unmarshal(data, out)
}

func (c *Client) Health(ctx context.Context) (map[string]any, error) {
	var out map[string]any
	err := c.request(ctx, http.MethodGet, "/health", nil, &out)
	return out, err
}

func (c *Client) Status(ctx context.Context, provider string, seed int) (map[string]any, error) {
	var out map[string]any
	path := "/v1/status?provider=" + url.QueryEscape(provider) + fmt.Sprintf("&seed=%d", seed)
	err := c.request(ctx, http.MethodGet, path, nil, &out)
	return out, err
}

func (c *Client) Sample(ctx context.Context, provider string, shots, seed int) (SampleResponse, error) {
	var out SampleResponse
	body := map[string]any{"provider": provider, "shots": shots, "seed": seed}
	err := c.request(ctx, http.MethodPost, "/v1/sample", body, &out)
	return out, err
}

func (c *Client) Normalize(ctx context.Context, payload map[string]any) (NormalizeResponse, error) {
	var out NormalizeResponse
	err := c.request(ctx, http.MethodPost, "/v1/normalize", payload, &out)
	return out, err
}
