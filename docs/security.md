# Security and responsible data processing

- Public aggregated data only; no individual data or eligibility inference.
- Private keys use Pydantic SecretStr and server-side SDK construction. Actual `.env` is ignored, excluded from Docker contexts and omitted from the source archive.
- Outbound data HTTP accepts HTTPS and an exact public-government hostname allowlist, refuses credentials, custom ports, fragments and redirects, and bounds time, retries and decompressed bytes. There is no arbitrary public URL-proxy endpoint.
- Tool input schemas forbid unknown fields, limit strings/lists and permit only the registered read-only actions. Request bodies and discovery rates are bounded. No downloaded scripts execute.
- Metadata is untrusted. HTML is reduced to text and React escapes rendered strings. Official-link helpers allow only known government HTTPS domains. Source descriptions cannot authorize tools, change scores or execute imports.
- AI outputs can select only known dataset/category evidence; user-facing evidence is assembled from the recorded deterministic report. Unknown model dataset IDs fail closed into the deterministic fallback.
- CLI-only approvals and imports use reviewed manifests and transactions. A changed fingerprint/checksum blocks ingestion. These commands are not exposed over HTTP.
- CORS allows only local frontend origins. Loopback-only Compose bindings support local development. The request limiter is single-process; production needs an edge limiter, HTTPS, deployment-specific origins and a durable audit/backup policy.
- Logs record public request host and error type; they do not include key values, database credentials or Census key query parameters.

Accessibility: semantic headings, labelled forms, native keyboard selectors, focus-visible styles, a skip link, native modal focus containment/Escape behavior, reduced-motion support and chart/table alternatives are implemented. Small-screen navigation and controls were reviewed. This is not a WCAG certification; a complete screen-reader, contrast, zoom and assistive-technology audit remains outstanding.
