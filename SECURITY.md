# Security Policy

## Supported Versions

Security updates are provided for the latest minor release line.

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues, discussions, or pull requests.**

Report vulnerabilities privately via GitHub Security Advisories:

> https://github.com/alexisgarcia-dev/claude-mcp-server-template/security/advisories/new

When reporting, please include:

- A description of the issue and its potential impact.
- Steps to reproduce, ideally with a minimal proof-of-concept.
- Affected versions and configuration (transport, auth mode, deployment topology).
- Any suggested mitigations or patches.

## Disclosure Timeline

We aim to follow a coordinated disclosure model:

| Stage                      | Target           |
| -------------------------- | ---------------- |
| Initial response           | within 7 days    |
| Triage and severity rating | within 14 days   |
| Coordinated disclosure     | within 90 days   |

Timelines may be shortened for critical issues with active exploitation, or extended where upstream coordination is required. We will keep reporters informed throughout.

## Scope

### In scope

- Authentication bypass on the demo `StaticTokenVerifier`.
- Container escape from the provided Docker images.
- JSON-RPC injection or smuggling against the MCP transport layer.
- OpenTelemetry mask bypass leading to credentials, tokens, or secrets being leaked into spans, logs, or exported telemetry.
- Insecure defaults in `config.toml` / `.env.example` that expose secrets in typical deployments.

### Out of scope

- Vulnerabilities in upstream dependencies. Please report these directly to their maintainers:
  - `mcp` — https://github.com/modelcontextprotocol
  - `fastmcp` — https://github.com/jlowin/fastmcp
  - Jaeger — https://github.com/jaegertracing/jaeger
- Issues that require physical access to the host.
- Social engineering of maintainers or users.
- Self-inflicted misconfiguration that contradicts documented production guidance (see below).
- Denial-of-service via unbounded request volume against the demo mock API.

## Production Notes

This template ships with **demo-grade defaults**. Before deploying to production:

- **Replace `StaticTokenVerifier`** with OAuth 2.1 + PKCE against your IdP. Roadmap for first-party support is tracked in `ROADMAP.md`.
- **Do not pass secrets via plain environment variables** in production. Use Docker secrets, Kubernetes Secrets, or a dedicated secrets manager (HashiCorp Vault, AWS Secrets Manager, GCP Secret Manager).
- **Run behind a TLS terminator.** The MCP server is HTTP-only by design; terminate TLS with nginx, Caddy, Traefik, or a managed load balancer.
- **Restrict the bind host.** The default `MCP_HOST=127.0.0.1` mitigates DNS rebinding; only expose via a reverse proxy.
- **Audit OpenTelemetry exporters.** Verify masking hooks are active before pointing the OTLP endpoint at a shared collector.

Thank you for helping keep this project and its users safe.
