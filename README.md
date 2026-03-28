<div align="center">

# Sure AIO (All-in-One) for Unraid 💸

[![Docker Image Size](https://img.shields.io/docker/image-size/jsonbored/sure-aio/latest?color=blue&label=Image%20Size)](https://github.com/JSONbored/sure-aio/pkgs/container/sure-aio)
[![GitHub License](https://img.shields.io/github/license/we-promise/sure?color=green)](https://github.com/we-promise/sure/blob/main/LICENSE)
[![Unraid Community Applications](https://img.shields.io/badge/Unraid-CA%20Template-orange)](https://unraid.net/community/apps)

An ultra-simplified, 100% self-contained deployment of [Sure](https://github.com/we-promise/sure) (the community fork of Maybe Finance) designed explicitly for Unraid homelabs.

</div>

---

Instead of configuring 4 different templates, managing custom Docker networks, and bootstrapping external PostgreSQL/Redis databases, this image handles the entire stack internals for you. It's designed to provide a "Binhex-style" one-click installation experience for users who just want it to work.

## 📦 What's Inside the "Mega-Container"
This image uses `s6-overlay v3` to gracefully orchestrate the entire self-hosted finance ecosystem invisibly:
- 🌐 **The Web UI:** The core Ruby on Rails dashboard.
- ⚙️ **The Task Runner:** Sidekiq Background Job Worker (for scraping/syncs).
- 🗄️ **The Database:** **PostgreSQL** is auto-provisioned securely internally.
- ⚡ **The Cache:** **Redis** is auto-provisioned for rapid background queuing.

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

While designed for absolute beginners, this container does not neuter the upstream application. It supports **100%** of the features the Sure team has built.

If you click **"Show more settings..."** in the Unraid template, you can customize the system violently. 

Read the comprehensive [Power User Guide here](docs/power-user.md) for instructions on how to configure:
- **[Local AI / Ollama Integration](docs/power-user.md#2-artificial-intelligence-categorization--chat):** Replace OpenAI with your own LLM for categorization.
- **[External OpenClaw / MCP Agent Routing](docs/power-user.md#option-b-external-agent-routing-openclaw--mcp):** Bypass the built-in bot entirely.
- **[AWS S3 / Cloudflare R2 Storage](docs/power-user.md#4-offloading-storage-to-s3--cloudflare-r2--minio):** Offload receipt and statement uploads.
- **[External Database Overrides](docs/power-user.md#1-using-an-external-database-bypassing-aio-internals):** Don't want to use our internal Postgres? Wire it up to your dedicated DB server.
- **[Enterprise Auth & SMTP](docs/power-user.md#6-enterprise-setup-oidc--email):** Set up SSO and password recovery emails.

## 💾 Data Persistence
Even though the databases roar silently inside the container, their data is mapped physically to your Unraid cache drive. **You will not lose data when updating the container.**

- **File Uploads:** `/mnt/user/appdata/sure-aio/system`
- **Database:** `/mnt/user/appdata/sure-aio/postgres`
- **Cache Data:** `/mnt/user/appdata/sure-aio/redis`

Just make sure `/mnt/user/appdata/sure-aio` is covered by your standard Unraid Community Applications Backup schedule.

## ⚖️ License & Acknowledgements
- The underlying application code is maintained by the incredible [community at we-promise/sure](https://github.com/we-promise/sure). 
- The Sure codebase is licensed under **AGPLv3**.
- This specific Dockerfile deployment wrapper (the AIO architecture) is provided by JSONbored to ease deployment burdens on Unraid.

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=JSONbored/sure-aio&type=date&legend=top-left)](https://www.star-history.com/#JSONbored/sure-aio&type=date&legend=top-left)
---

## 👨‍💻 About the Creator

Built with 🖤 by **[JSONbored](https://github.com/JSONbored)**.

- 🌐 **Portfolio & Services:** [aethereal.dev](https://aethereal.dev)
- 📅 **Book a Call:** [cal.com/aethereal](https://cal.com/aethereal) 
- ☕ **Support my work:** [Sponsor on GitHub](https://github.com/sponsors/JSONbored)
