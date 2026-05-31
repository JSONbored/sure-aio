# Power User Guide: Sure-AIO Configs

`Sure-AIO` is a Unraid-first wrapper around upstream `ghcr.io/we-promise/sure`. The wrapper is expected to track upstream self-hosting features closely, but it still adds its own operational opinionation around internal Postgres, Redis, and Unraid-facing defaults. This guide explains how to use the Advanced template fields without pretending the wrapper is magic.

---

## 1. Using an External Database (Bypassing AIO Internals)

If you already run a heavy-duty PostgreSQL/Redis container (like `postgres-shared`) and want Sure to use it instead of its own internal isolated database:

1. Create a database (e.g. `sure_app`) and user on your external Postgres container.
2. In the Sure-AIO template, toggle **Show more settings...**.
3. Find the **[External DB]** block.
4. Input your `DB Host Override` (e.g. `192.168.1.50`, or the Unraid docker network hostname if you run them on a custom net).
5. Input the `DB User` and `DB Password` overrides.
6. Input the `Redis URL Override` (e.g. `redis://192.168.1.50:6379/1`).
7. **Result:** The AIO container will still boot its internal services silently, but the Rails UI, Sidekiq workers, and first-boot database preparation will honor your external overrides instead of the built-in defaults.

---

## 2. Artificial Intelligence (Categorization & Chat)

Sure uses AI to auto-categorize transactions and answer questions.

### Option A: Local LLM (Ollama) - _Recommended Privacy Focus_

To process your finances locally without sending data to the cloud:

1. Find the **[AI]** block.
2. **OpenAI / Ollama Token:** Enter `ollama-local` (bypasses validation).
3. **OpenAI URI Base:** Enter your Ollama IP: `http://192.168.1.X:11434/v1`
4. **Model Name:** Enter a local model you have pulled (e.g., `llama3.1:8b`).

### Option B: External Agent Routing (OpenClaw / MCP)

To handle chat entirely inside an external AI agent rather than the basic Sure UI:

1. Find the **[Ext. AI]** block.
2. **Assistant Type:** Set to `external` (forces all users to use the remote agent).
3. **Assistant URL:** e.g., `http://192.168.1.X:18789/v1/chat/completions` (OpenClaw completions endpoint).
4. **Assistant Token:** Your gateway token.
5. **Agent ID:** Optional if your provider exposes multiple agents.
6. **Session Key:** Leave blank for isolated per-chat remote state. Set it only if you intentionally want all routed chats to share the same remote agent session.
7. **Allowed Emails:** Optional comma-separated allowlist to restrict who can use the external assistant.
8. **MCP User Email:** The email of the Sure user the agent will act as.
9. **MCP API Token:** Create a secure password. The external agent uses this to securely callback into Sure to read transaction data.

### Option C: Local Vector Search (pgvector / Qdrant)

Sure allows chatting with uploaded financial PDFs and other indexed documents.
For the exact Sure-AIO pgvector behavior, including the default "installed but not enabled" model and the external PostgreSQL limitation, see [docs/pgvector.md](pgvector.md).

1. Find the **[AI] Vector Store Provider** field.
2. Set it to `pgvector` to keep vectors inside the bundled internal PostgreSQL service, or `qdrant` if you want an external Qdrant instance.
3. For `pgvector`, set:
   - `EMBEDDING_MODEL` such as `nomic-embed-text`
   - `EMBEDDING_DIMENSIONS` to match the model output, usually `1024`
   - `EMBEDDING_URI_BASE` if your embedding endpoint differs from `OPENAI_URI_BASE`
   - `EMBEDDING_ACCESS_TOKEN` if your embedding endpoint needs a different token than `OPENAI_ACCESS_TOKEN`
4. For `qdrant`, also provide `QDRANT_URL` and `QDRANT_API_KEY` if needed.
5. If you use Ollama for embeddings, make sure the embedding model is actually pulled and available. Exposing the vars is not enough if the model is missing.
6. If you want verbose AI troubleshooting in the container logs, set **[AI] Debug Logging** to `true`.
7. If your OpenAI-compatible endpoint does not support PDF or vision input, set **[AI] Enable PDF Processing** to `false` so Sure does not try to send PDF workloads to a provider that cannot handle them.
8. If you use a custom OpenAI-compatible provider, **[AI] Supports Responses API** can force Sure toward the Responses API (`true`) or chat completions (`false`). Leave it blank unless auto-detection is wrong for your provider.
9. For small-context local models, tune `LLM_CONTEXT_WINDOW`, `LLM_MAX_RESPONSE_TOKENS`, `LLM_MAX_HISTORY_TOKENS`, `LLM_SYSTEM_PROMPT_RESERVE`, and `LLM_MAX_ITEMS_PER_CALL` rather than relying on defaults intended for larger cloud models.

---

## 3. Telemetry & Observability (Langfuse / PostHog)

Track LLM inference costs and app usage.

1. Find the **[Telemetry]** block.
2. **PostHog:** Fill in your `POSTHOG_KEY` and `HOST` to track user analytics.
3. **Langfuse:** Fill in your `LANGFUSE_HOST`, `PUBLIC_KEY`, and `SECRET_KEY` to chart token usage, latency, and costs of your AI operations.
4. If you use hosted Langfuse and prefer a region shortcut instead of a full host URL, set `LANGFUSE_REGION` to `us` or `eu`. If `LANGFUSE_HOST` is set, it wins over the region shortcut.
5. **Skylight APM:** `SKYLIGHT_ENABLED` defaults to `false` in this AIO wrapper (image default + template field) so users do not need any extra external service for normal operation. If you explicitly want Skylight, set `SKYLIGHT_ENABLED=true` and provide `SKYLIGHT_AUTHENTICATION` from your Skylight app settings.

---

## 4. Offloading Storage to S3 / Cloudflare R2 / GCS / Minio

Avoid filling your Unraid cache drive by piping PDFs/receipts straight to object storage.

1. Find the **[Storage]** block.
2. **Provider Strategy:** Change from blank to `amazon`, `cloudflare`, `generic_s3`, or `google`.
3. Provide the matching provider credentials and bucket fields.
4. If using TrueNAS Minio or similar, provide the `Custom Endpoint` (Generic S3 only).
5. For Google Cloud Storage, set `GCS_PROJECT`, `GCS_BUCKET`, and either `GCS_KEYFILE_JSON` or `GCS_KEYFILE`. Inline `GCS_KEYFILE_JSON` is usually easier in Unraid because it does not require mounting a separate credentials file.

---

## 5. Free vs Paid External Data Providers

Sure relies on upstream providers for currency exchange rates and stock logos.

- **Free (Default):** If you leave provider overrides blank, upstream Sure defaults to `yahoo_finance` for first-boot friendliness.
- **Paid API Keys (Optional):** If you prefer Twelve Data, add your API key and change **[API] Exchange Rate Provider** and **[API] Securities Provider** to `twelve_data`.
- **Multi-provider securities:** Upstream v0.7.0 also supports `SECURITIES_PROVIDERS` as a comma-separated provider list. This takes precedence over the single `SECURITIES_PROVIDER` value when set.
- **Expanded provider keys:** The template exposes `TIINGO_API_KEY`, `EODHD_API_KEY`, and `ALPHA_VANTAGE_API_KEY` for the new v0.7.0 securities providers. Setting these env vars locks the matching in-app setting to the environment value.
- **Crypto and mutual funds:** `binance_public` and `mfapi` are available as upstream securities providers. The template exposes `BINANCE_PUBLIC_URL`, `BINANCE_EGRESS_IP`, and `MFAPI_URL` for advanced routing or allowlist display.
- **Logos:** Provide a **[API] Brandfetch Client ID** to automatically scrape high-res logos for your bank names and merchants.
- **High-res logos:** Set `BRAND_FETCH_HIGH_RES_LOGOS=true` if you want Sure to prefer larger Brandfetch logo assets where available.
- **Indexa token path:** If you use Indexa Capital and want a single global token fallback, set `INDEXA_API_TOKEN`.
- **Important override behavior:** Upstream only locks matching settings UI controls when the related env var is present. Leaving provider/logo env fields blank keeps the UI controls interactive.
- **Advanced provider tuning:** The template also exposes `TWELVE_DATA_URL`, `TWELVE_DATA_MIN_REQUEST_INTERVAL`, `TWELVE_DATA_MAX_REQUESTS_PER_MINUTE`, `TIINGO_URL`, `TIINGO_MAX_REQUESTS_PER_HOUR`, `EODHD_URL`, `EODHD_MAX_REQUESTS_PER_DAY`, `ALPHA_VANTAGE_URL`, `ALPHA_VANTAGE_MAX_REQUESTS_PER_DAY`, `YAHOO_FINANCE_URL`, `YAHOO_FINANCE_MAX_RETRIES`, `YAHOO_FINANCE_RETRY_INTERVAL`, and `YAHOO_FINANCE_MIN_REQUEST_INTERVAL` if you need proxying or rate-limit tuning.

---

## 6. Enterprise Setup (OIDC & Email)

### OpenID Connect (Authelia / Authentik)

To enable Single Sign-On (SSO):

1. Find the **[Auth]** block.
2. Provide your `OIDC Client ID`, `Client Secret`, `Issuer URL`, and the `Redirect URI` you configured in your Identity Provider.
3. If you want tighter onboarding control, set:
   - `AUTH_LOCAL_LOGIN_ENABLED=false` to make the instance SSO-first
   - `AUTH_LOCAL_ADMIN_OVERRIDE_ENABLED=true` if you still want a super-admin emergency login path
   - `AUTH_JIT_MODE=link_only` if SSO should only link to existing users rather than auto-create them
   - `ALLOWED_OIDC_DOMAINS` to restrict which email domains may auto-create accounts through JIT SSO
4. Optional button labels/icons are exposed too, along with dedicated Google and GitHub OAuth client fields if you want those providers separately.
5. The template now also exposes `AUTH_PROVIDERS_SOURCE` plus named multi-provider envs like `OIDC_KEYCLOAK_*` and `OIDC_AUTHENTIK_*` if you want upstream's YAML-based or database-backed multi-provider SSO model.
6. Upstream also uses `APP_URL` for advanced auth flows, especially absolute callback and issuer generation. If you are doing advanced auth beyond the normal generic OIDC path, set `APP_URL` to your full external base URL such as `https://finance.example.com`.

### SMTP Mail Relay (For Password Resets / Reports)

1. Find the **[Email]** block.
2. Fill out standard credentials: `SMTP Address`, `Port`, `Username`, `Password`.
3. Provide the `Sender Address` (e.g., `no-reply@finance.yourdomain.com`).
4. Leave `SMTP_TLS_SKIP_VERIFY=false` unless you are using a trusted private relay with broken certificates. Setting it to `true` disables SMTP certificate verification.

---

## 7. Advanced Database Encryption

By default, Sure derives your database encryption keys securely from your `Secret Key Base`.

If you are a cryptography purist who wants to separate these:

1. Find the **[DB Encryption]** block.
2. Manually define your `Primary Key`, `Deterministic Key`, and `Derivation Salt`.
   _(Warning: Losing these means permanently losing access to your encrypted data)._

---

## 8. Reverse Proxy and HTTPS

For a normal beginner install on your LAN, leave the SSL options at:

1. `RAILS_FORCE_SSL=false`
2. `RAILS_ASSUME_SSL=false`

If you later place Sure behind Nginx Proxy Manager, Traefik, Caddy, Cloudflare Tunnel, or another SSL-terminating reverse proxy:

1. Set `RAILS_ASSUME_SSL=true`
2. Set `RAILS_FORCE_SSL=true` only if you want plain HTTP requests redirected to HTTPS
3. Set `APP_DOMAIN` to the hostname you actually use for email links and callbacks
4. If advanced auth or metadata generation expects a full URL, also set `APP_URL` to the full external base URL
5. Keep `SURE_REFERRER_POLICY=strict-origin-when-cross-origin`
6. Leave `SURE_CSRF_ORIGIN_CHECK=true` unless your browser/proxy path still sends `Origin: null`

Rails rejects login POSTs when the browser sends `Origin: null`. The most common proxy-side cause is a response header such as `Referrer-Policy: no-referrer`. Sure-AIO now defaults the Rails response header to `strict-origin-when-cross-origin`, which keeps Rails origin checks working behind HTTPS proxies without exposing full cross-site paths.

For Traefik, make sure the host rule uses normal Traefik quoting and that no middleware overrides the referrer policy to `no-referrer`:

```text
traefik.enable=true
traefik.http.routers.sure-aio.entryPoints=https
traefik.http.routers.sure-aio.rule=Host(`sure.domain.com`)
traefik.http.routers.sure-aio.middlewares=sure-aio-headers
traefik.http.middlewares.sure-aio-headers.headers.customresponseheaders.Referrer-Policy=strict-origin-when-cross-origin
```

If you use Cloudflare in front of Traefik, also check Cloudflare Transform Rules, Workers, Zaraz, or security/privacy tooling for a `Referrer-Policy: no-referrer` override. The forwarded headers in a healthy HTTPS proxy path should include `X-Forwarded-Proto: https`; that part is separate from the browser `Origin` header Rails uses for CSRF origin checks.

If login still fails with `The change you wanted was rejected` and the Rails log still says the browser returned a `null` origin after the referrer policy is visible, set `SURE_CSRF_ORIGIN_CHECK=false`. This is an advanced compatibility escape hatch for proxy/privacy stacks that produce opaque browser origins. It disables Rails' origin comparison only; Rails still requires the normal authenticity token on form POSTs.

### Private CA / Self-Signed HTTPS Support

If your OIDC provider, MinIO endpoint, Qdrant node, or another upstream integration uses a private CA:

1. Use the optional **[SSL] Custom CA Certificate Mount** field to bind your CA PEM file into the container.
2. Set **[SSL] Custom CA File** to the in-container path, for example `/certs/custom-ca.pem`.
3. Leave **[SSL] Verify Remote Certificates** at `true` for normal operation.
4. Set **[SSL] Debug Logging** to `true` only while troubleshooting certificate trust issues.
5. Only set `SSL_VERIFY=false` as a temporary test. It weakens outbound TLS validation globally inside the app process.

This matters more than it sounds. Upstream applies this CA bundle globally so OIDC discovery, webhook callbacks, object storage, and other HTTPS clients all trust the same internal CA.

---

## 9. External Object Storage Variants

The template now exposes the real upstream storage split instead of pretending all S3-style providers use the same env names.

1. For Amazon S3, use the **[Storage:AWS]** fields.
2. For Cloudflare R2, use the **[Storage:R2]** fields, including `CLOUDFLARE_ACCOUNT_ID`.
3. For MinIO or other S3-compatible endpoints, use the **[Storage:Generic S3]** fields.
4. Only set **Force Path Style** to `true` when your provider actually requires path-style S3 requests.
5. For Google Cloud Storage, use the **[Storage:GCS]** fields and set **Provider Strategy** to `google`.

---

## 10. External Redis With Sentinel

For normal AIO installs, leave Redis internal. If you already run a real HA Redis stack:

1. Fill **[External Redis] Sentinel Hosts** with a comma-separated list like `redis-sentinel-1:26379,redis-sentinel-2:26379`.
2. Set **[External Redis] Sentinel Master** if your master name is not `mymaster`.
3. Add username/password only if your Sentinel deployment requires them.
4. Sentinel settings take precedence over `REDIS_URL` when both are present.

---

## 11. Logging And External Log Shipping

For most Unraid installs, plain container logs are enough. If you want centralized production logging:

1. Set **[Telemetry] Rails Log Level** to `debug` temporarily when troubleshooting application behavior.
2. Add **[Telemetry] Logtail API Key** and **[Telemetry] Logtail Ingest Host** if you want Sure logs forwarded to Better Stack Logtail.
3. Leave those fields blank for the normal beginner path. Shipping logs externally is optional and not part of the default AIO experience.

---

## 12. Sync, Plaid, and Runtime Tuning

The template now exposes the main upstream runtime toggles that were previously only obvious in docs or code:

1. **Sync scheduling**
   - `AUTO_SYNC_ENABLED`
   - `AUTO_SYNC_TIME`
   - `AUTO_SYNC_TIMEZONE`
2. **Pending transaction behavior**
   - `SIMPLEFIN_INCLUDE_PENDING`
   - `PLAID_INCLUDE_PENDING`
   - `LUNCHFLOW_INCLUDE_PENDING`
   - `SIMPLEFIN_DEBUG_RAW`
   - `LUNCHFLOW_DEBUG_RAW`
   - `SIMPLEFIN_CC_OVERPAYMENT_HEURISTIC`
   - Just like provider selection, these env overrides lock the matching Sync control in Sure's UI when set.
3. **Plaid credentials**
   - `PLAID_CLIENT_ID`
   - `PLAID_SECRET`
   - `PLAID_ENV`
   - `PLAID_EU_CLIENT_ID`
   - `PLAID_EU_SECRET`
   - `PLAID_EU_ENV`
4. **OpenAI compatibility tuning**
   - `OPENAI_REQUEST_TIMEOUT`
   - `OPENAI_SUPPORTS_RESPONSES_ENDPOINT`
   - `LLM_JSON_MODE`
   - `LLM_CONTEXT_WINDOW`
   - `LLM_MAX_RESPONSE_TOKENS`
   - `LLM_MAX_HISTORY_TOKENS`
   - `LLM_SYSTEM_PROMPT_RESERVE`
   - `LLM_MAX_ITEMS_PER_CALL`
   - `CATEGORIZATION_PROVIDER` / `CATEGORIZATION_MODEL`
   - `CHAT_PROVIDER` / `CHAT_MODEL`
5. **Auth and onboarding behavior**
   - `REQUIRE_EMAIL_CONFIRMATION`
   - `REQUIRE_INVITE_CODE`
   - `AUTH_PROVIDERS_SOURCE`
6. **Database and SSL edge cases**
   - `POSTGRES_DB`
   - `SSL_CERT_FILE`
   - `SMTP_TLS_SKIP_VERIFY`
   - `SELF_HOSTING_ENABLED` (legacy alias; keep `SELF_HOSTED=true` as the main switch)
7. **Runtime/process tuning**
   - `RAILS_MAX_THREADS`
   - `WEB_CONCURRENCY`
   - `SIDEKIQ_WEB_USERNAME`
   - `SIDEKIQ_WEB_PASSWORD`
8. **Advanced outbound networking**
   - `HTTPS_PROXY`
   - `HTTP_PROXY`
   - `NO_PROXY`

These are all legitimate upstream runtime knobs, but not all of them belong in a beginner walkthrough. They are here because `sure-aio` should expose the real self-hosting surface without forcing users to rebuild the image just to reach it.

---

## Trial / Subscription Note

Upstream `v0.7.0` still disables subscription and trial gating in self-hosted mode when `SELF_HOSTED=true`. The 45-day trial logic still exists in the codebase, but upstream guards it behind `app_mode != self_hosted`.

That means if you see a trial banner or upgrade flow on a self-hosted Sure-AIO install, the likely causes are:

1. The running container is not actually seeing `SELF_HOSTED=true`.
2. Existing app state was created before self-hosted mode was applied.
3. There is an upstream bug in a specific onboarding or UI path.

It is not caused by missing Stripe billing envs in this wrapper. Those Stripe envs exist upstream for managed billing flows, but upstream self-hosted mode is designed to bypass them.
