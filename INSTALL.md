# OpenClaw Gateway — Installation Steps

Steps followed to install and configure OpenClaw gateway on Ubuntu.

---

## 1. Install Node.js (≥ 22.19) via nvm

```bash
nvm install 24 --latest-npm
nvm use 24
```

## 2. Install OpenClaw CLI

```bash
npm install -g openclaw@latest
```

## 3. Run Initial Onboarding

```bash
openclaw onboard
```

Generates `~/.openclaw/openclaw.json` and default agent config.

## 4. Configure LLM Provider (vLLM / OpenAI-compatible)

```bash
openclaw config set models.providers.vllm '{
  "baseUrl": "<VLLM_BASE_URL>/v1",
  "apiKey": "<VLLM_API_KEY>",
  "thinkingFormat": "qwen-chat-template",
  "contextWindow": 32768
}'

openclaw models set vllm/<MODEL_ID>
```

> Values come from `.env` — see `.env.example` for reference.

## 5. Run the Gateway

```bash
# Foreground
openclaw gateway run --force

# Background (persistent)
nohup openclaw gateway run --force > /tmp/openclaw-gateway.log 2>&1 &
```

## 6. Link WhatsApp Channel

```bash
openclaw channels add
```

Scan the QR code in WhatsApp → **Linked Devices** → **Link a Device**.

Then set the allowlist:
```bash
source .env
openclaw config set channels.whatsapp.allowFrom "[\"$WHATSAPP_TARGET\"]" --strict-json
```

Verify:
```bash
openclaw channels status
# Expected: enabled, configured, linked, running, connected, health:healthy
```

## 7. Mobile Pairing via ngrok

ngrok exposes the local gateway over the internet:

```
# Start ngrok tunnel (forward HTTPS traffic to local gateway)
ngrok http 18789
```

This will provide a public HTTPS URL (e.g., `https://<subdomain>.ngrok-free.app`)
that tunnels to `http://localhost:18789`.

Generate pairing code using the WSS URL (convert the ngrok HTTPS URL to WSS):
```bash
openclaw qr --url wss://<subdomain>.ngrok-free.app
```

Paste the printed setup code into the OpenClaw mobile app (**Enter Setup Code**), then approve:
```bash
openclaw devices list
openclaw devices approve <device-id>
```

---

## Key File Locations

| Path | Description |
|---|---|
| `~/.openclaw/openclaw.json` | Main OpenClaw config |
| `/tmp/openclaw/openclaw-<date>.log` | Gateway runtime logs |
| `.env` | Local secrets (gitignored) |
| `test_whatsapp.py` | End-to-end test suite |
