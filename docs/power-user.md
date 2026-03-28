# Power User Guide: Sure-AIO Configs

Because `Sure-AIO` is a 1:1 wrapper around the actual `ghcr.io/we-promise/sure` image, every single upstream feature is supported. This guide comprehensively explains how to use the "Advanced" fields in the Unraid Template to highly customize your instance.

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

### Option A: Local LLM (Ollama) - *Recommended Privacy Focus*
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
5. **MCP User Email:** The email of the Sure user the agent will act as.
6. **MCP API Token:** Create a secure password. The external agent uses this to securely callback into Sure to read transaction data.

### Option C: Local Vector Database (Document RAG)
Sure allows chatting with uploaded financial PDFs.
1. Find the **[AI] Vector Store Provider** field.
2. The default for OpenAI is `openai`. If you use local LLMs, change this to `pgvector` or `qdrant`. *(Note: Using `pgvector` requires you to override the database to a custom external Postgres container compiled with the pgvector extension).*

---

## 3. Telemetry & Observability (Langfuse / PostHog)
Track LLM inference costs and app usage.

1. Find the **[Telemetry]** block.
2. **PostHog:** Fill in your `POSTHOG_KEY` and `HOST` to track user analytics.
3. **Langfuse:** Fill in your `LANGFUSE_HOST`, `PUBLIC_KEY`, and `SECRET_KEY` to chart token usage, latency, and costs of your AI operations.

---

## 4. Offloading Storage to S3 / Cloudflare R2 / Minio
Avoid filling your Unraid cache drive by piping PDFs/receipts straight to object storage.

1. Find the **[Storage]** block.
2. **Provider Strategy:** Change from blank to `amazon`, `cloudflare`, or `generic_s3`.
3. Provide your `Access Key ID`, `Secret Access Key`, `Region`, and `Bucket Name`.
4. If using TrueNAS Minio or similar, provide the `Custom Endpoint` (Generic S3 only).

---

## 5. Free vs Paid External Data Providers
Sure relies on upstream providers for currency exchange rates and stock logos.

*   **Free (Default):** The template invisibly hardcodes `yahoo_finance` so you don't have to register for API keys.
*   **Paid API Keys (Optional):** If you prefer `twelve_data` and have an API key, drop it in the **[API] Twelve Data Key** field to unseat the Yahoo default.
*   **Logos:** Provide a **[API] Brandfetch Client ID** to automatically scrape high-res logos for your bank names and merchants.

---

## 6. Enterprise Setup (OIDC & Email)

### OpenID Connect (Authelia / Authentik)
To enable Single Sign-On (SSO):
1. Find the **[Auth]** block.
2. Provide your `OIDC Client ID`, `Client Secret`, `Issuer URL`, and the `Redirect URI` you configured in your Identity Provider.

### SMTP Mail Relay (For Password Resets / Reports)
1. Find the **[Email]** block.
2. Fill out standard credentials: `SMTP Address`, `Port`, `Username`, `Password`.
3. Provide the `Sender Address` (e.g., `no-reply@finance.yourdomain.com`).

---

## 7. Advanced Database Encryption
By default, Sure derives your database encryption keys securely from your `Secret Key Base`.

If you are a cryptography purist who wants to separate these:
1. Find the **[DB Encryption]** block.
2. Manually define your `Primary Key`, `Deterministic Key`, and `Derivation Salt`. 
*(Warning: Losing these means permanently losing access to your encrypted data).*

---

## 8. Reverse Proxy and HTTPS

For a normal beginner install on your LAN, leave the SSL options at:

1. `RAILS_FORCE_SSL=false`
2. `RAILS_ASSUME_SSL=false`

If you later place Sure behind Nginx Proxy Manager, Traefik, Caddy, Cloudflare Tunnel, or another SSL-terminating reverse proxy:

1. Set `RAILS_ASSUME_SSL=true`
2. Set `RAILS_FORCE_SSL=true` only if you want plain HTTP requests redirected to HTTPS
3. Set `APP_DOMAIN` to the hostname you actually use for email links and callbacks
