<div align="center">

<img src="https://socialify.git.ci/jsonbored/sure-aio/image?custom_description=The+easiest+way+to+deploy+Sure+Finance+%28Maybe+Finance+fork%29+via+Unraid+CA.&custom_language=Dockerfile&description=1&font=KoHo&forks=1&language=1&logo=https%3A%2F%2Favatars.githubusercontent.com%2Fu%2F49853598%3Fv%3D4&name=1&owner=1&pattern=Signal&pulls=1&stargazers=1&theme=Dark" alt="sure-aio" width="640" height="320" />

</div>

---

An ultra-simplified, self-contained deployment of [Sure](https://github.com/we-promise/sure) designed explicitly for Unraid homelabs.

Instead of configuring 4 different templates, managing custom Docker networks, and bootstrapping external PostgreSQL/Redis databases, this image handles the entire stack internals for you. It's designed to provide a "Binhex-style" one-click installation experience for users who just want it to work.

## 📦 What's Inside the "Mega-Container"
This image uses `s6-overlay v3` to orchestrate the stack internally:
- The Web UI: the core Ruby on Rails dashboard.
- The Task Runner: Sidekiq background job worker.
- The Database: PostgreSQL auto-provisioned securely inside the container.
- The Cache: Redis auto-provisioned for background queuing.

## 🚀 Installation (For Beginners)

If you just want to track your finances and don't care about databases, this is for you.

1. Add this repository to your Unraid Template Repositories (or search it directly in CA): `https://github.com/JSONbored/awesome-unraid`
2. Search and Install **Sure-AIO**.
3. Open your Unraid Terminal (the `>_` icon top right).
4. Run this specific command to generate a highly secure random password: 
   ```bash
   openssl rand -hex 64
   ```
5. Copy the output, and paste it into the **Secret Key Base** field in the template.
6. Click **Apply**. 

*Wait about 30-60 seconds on the very first boot. The container is secretly building your databases, running migrations, and setting up the web server. Once the logs settle, open the WebUI on port 3000 over normal HTTP unless you deliberately put it behind your own reverse proxy.*

---

## 🛠️ Power User Configuration (Advanced Options)

While designed for absolute beginners, this container is intended to keep pace with upstream self-hosting features rather than stripping them out. The goal is straightforward: if upstream exposes a real self-hosting feature, the Unraid wrapper should either support it or document the gap plainly.

Some advanced Sure settings are intentionally managed as container environment variables in the Unraid template instead of only through Sure's web UI. When upstream sees one of those env vars, it may disable the matching control in the app and treat the template value as the source of truth. That is expected for this wrapper.
This wrapper also defaults `SKYLIGHT_ENABLED=false` at the image level (and exposes it in the template) so AIO users are not required to configure upstream Skylight APM.

If you click **"Show more settings..."** in the Unraid template, you can customize the system deeply.

Read the comprehensive [Power User Guide here](docs/power-user.md) for instructions on how to configure:
- **[Local AI / Ollama Integration](docs/power-user.md#2-artificial-intelligence-categorization--chat):** Replace OpenAI with your own LLM for categorization.
- **[External OpenClaw / MCP Agent Routing](docs/power-user.md#option-b-external-agent-routing-openclaw--mcp):** Bypass the built-in bot entirely.
- **[Local Vector Search / pgvector](docs/power-user.md#option-c-local-vector-search-pgvector--qdrant):** Keep document embeddings inside the bundled Postgres service.
- **[Dedicated pgvector behavior doc](docs/pgvector.md):** Exact internal-vs-external pgvector behavior, defaults, and limitations.
- **[AWS S3 / Cloudflare R2 Storage](docs/power-user.md#4-offloading-storage-to-s3--cloudflare-r2--minio):** Offload receipt and statement uploads.
- **[External Database Overrides](docs/power-user.md#1-using-an-external-database-bypassing-aio-internals):** Don't want to use our internal Postgres? Wire it up to your dedicated DB server.
- **[Enterprise Auth & SMTP](docs/power-user.md#6-enterprise-setup-oidc--email):** Set up SSO and password recovery emails.

## 💾 Data Persistence
Even though the databases roar silently inside the container, their data is mapped physically to your Unraid cache drive. **You will not lose data when updating the container.**

- **File Uploads:** `/mnt/user/appdata/sure-aio/system`
- **Database:** `/mnt/user/appdata/sure-aio/postgres`
- **Cache Data:** `/mnt/user/appdata/sure-aio/redis`

Just make sure `/mnt/user/appdata/sure-aio` is covered by your standard Unraid Community Applications Backup schedule.

## Versioning & Upstream

- `Sure-AIO` now pins a specific upstream Sure version instead of following the floating `stable` tag.
- The repo monitors stable upstream Sure tags and opens a PR when a newer stable version is released.
- Upstream image digest drift is tracked separately so digest-only refreshes do not masquerade as version-bump PRs.
- Every `main` package publish now ships the exact upstream version tag, an explicit AIO packaging line tag, `latest`, and `sha-<commit>`.
- Published images include explicit metadata labels for both layers:
  - upstream app: `io.jsonbored.upstream.version`, `io.jsonbored.upstream.digest`
  - wrapper identity: `io.jsonbored.wrapper.name`, `io.jsonbored.wrapper.type`, `io.jsonbored.wrapper.track`
- Formal wrapper releases follow the upstream version plus an AIO revision, such as `v0.6.8-aio.1`.
- See the release workflow details in [docs/releases.md](docs/releases.md).

## License & Acknowledgements
- The underlying application code is maintained by the incredible [community at we-promise/sure](https://github.com/we-promise/sure). 
- The Sure codebase is licensed under **AGPLv3**.
- This specific Dockerfile deployment wrapper (the AIO architecture) is provided by JSONbored to ease deployment burdens on Unraid.

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=JSONbored/sure-aio&type=date&legend=top-left)](https://www.star-history.com/#JSONbored/sure-aio&type=date&legend=top-left)
---
