# Power User Guide: Sure-AIO Configs

Because `Sure-AIO` is a 1:1 wrapper around the actual `ghcr.io/we-promise/sure` image, every single upstream feature is supported. This guide explains how to use the "Advanced" fields in the Unraid Template.

## 1. Using an External Database (Bypassing AIO Internals)
If you already run a heavy-duty PostgreSQL container (like `postgres-shared` or `databasement`) and want Sure to use it instead of its own internal isolated database:

1. Create a database (e.g. `sure_app`) and user on your external Postgres container.
2. In the Sure-AIO template, toggle "Show more settings...".
3. Find the **[External DB]** block.
4. Input your `DB Host Override` (e.g. `192.168.1.50`, or the Unraid docker network hostname if you run them on a custom net).
5. Input the `DB User` and `DB Password`.
6. **Result:** The AIO container will still boot its internal Postgres/Redis silently, but the Rails UI and Sidekiq workers will ignore them entirely and connect to your external server. 

## 2. Using Local AI (Ollama) instead of OpenAI
Sure uses AI to auto-categorize your transactions and power the chatbot assistant. To do this locally for free, without sending your financial data to the cloud:

1. Find the **[AI]** block.
2. **OpenAI / Ollama Token:** Enter `ollama-local` (it just needs a dummy string to bypass validation checks).
3. **OpenAI URI Base:** Enter the IP of your Unraid Ollama container: `http://192.168.1.X:11434/v1`
4. **Model Name:** You MUST enter a model you have already pulled (e.g., `llama3.1:8b`).

## 3. External Agent Routing (OpenClaw / MCP Integration)
If you want to handle chat entirely inside an external agent (like OpenClaw) rather than the basic UI inside Sure, you can route the logic via the Model Context Protocol (MCP):

1. Find the **[Ext. AI]** block.
2. **Assistant Type:** Set this to `external`. *This forces all users to use the remote agent.*
3. **Assistant URL:** Give it your OpenClaw chat completions endpoint (e.g., `http://192.168.1.X:18789/v1/chat/completions`).
4. **Assistant Token:** Your OpenClaw Gateway Token.
5. **MCP API Token:** Create a random new password here. OpenClaw will use this to securely callback into Sure to read your transaction data.

## 4. Offloading Storage to S3 / Cloudflare R2
If you don't want PDF receipts taking up space on your Unraid cache drive, you can pipe them straight to cloud object storage.

1. Find the **[Storage]** block.
2. **Provider Strategy:** Change from blank to `amazon` or `cloudflare` depending on your host.
3. Fill out the `Access Key ID`, `Secret Access Key`, `Region`, and `Bucket Name` fields.

## 5. Free Exchange Rates (Default Override)
*Note:* Upstream requires a `twelve_data` API key to get stock and currency info. To make sure the app works out of the box, our Unraid Template hardcodes `yahoo_finance` invisibly. If you *want* to use Twelve Data, grab an API Key from their site and drop it into the `[API] Twelve Data Key` field to unseat the Yahoo default.
