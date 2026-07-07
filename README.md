# OpenClaw Gateway — Setup & WhatsApp Integration

A local AI gateway powered by [OpenClaw](https://docs.openclaw.ai), running a **Qwen3** model served over an OpenAI-compatible endpoint. Supports WhatsApp as a chat channel with full agent inference.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Environment Configuration](#environment-configuration)
4. [OpenClaw Configuration](#openclaw-configuration)
   - [LLM Provider (vLLM / OpenAI-compatible)](#llm-provider-vllm--openai-compatible)
   - [WhatsApp Channel](#whatsapp-channel)
5. [Running the Gateway](#running-the-gateway)
6. [Running the WhatsApp Test](#running-the-whatsapp-test)
   - [Python test (recommended)](#python-test-recommended)
   - [Shell test](#shell-test)
7. [Project Structure](#project-structure)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

| Requirement | Minimum Version | Notes |
|---|---|---|
| **Node.js** | v22.19.0+ | Managed via nvm |
| **nvm** | any | Used to install the right Node version |
| **Python** | 3.10+ | For `test_whatsapp.py` and `config.py` |
| **npm** | 10+ | Comes with nvm Node |

---

## Installation

### 1 — Install nvm (if not already installed)

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash
source ~/.bashrc   # or ~/.zshrc
```

### 2 — Install Node.js ≥ 22.19

```bash
nvm install 22
nvm use 22
nvm alias default 22
node --version     # should print v22.23.x or higher
```

### 3 — Install OpenClaw globally

```bash
npm install -g openclaw@latest
openclaw --version
```

---

## Environment Configuration

All sensitive values (API keys, phone numbers) are stored in a local `.env` file that is **never committed to version control**.

### Step 1 — Copy the template

```bash
cp .env.example .env
```

### Step 2 — Fill in your values

```bash
# .env
VLLM_BASE_URL=https://your-endpoint.example.com/v1
VLLM_API_KEY=your_api_key_here
VLLM_MODEL_ID=your-model-id

WHATSAPP_TARGET=91XXXXXXXXXX       # no leading +
WHATSAPP_TARGET_E164=+91XXXXXXXXXX # with leading +
```

> **Note:** `AGENT_TIMEOUT` (default: `120` seconds) is optional and can be added to `.env` to override.

### How config is loaded

- **Python scripts** — `config.py` parses `.env` using stdlib only (no third-party deps) and exposes a `cfg` object.
- **Shell script** — `test_whatsapp.sh` uses `source .env` to export variables.

---

## OpenClaw Configuration

### Initial Setup (Interactive)

Run the guided onboarding wizard once:

```bash
openclaw onboard
```

This creates `~/.openclaw/openclaw.json` with gateway, auth, and workspace defaults.

---

### LLM Provider (vLLM / OpenAI-compatible)

The gateway connects to any OpenAI-compatible `/v1` endpoint.

#### Step 1 — Register the provider

```bash
openclaw config set models.providers.vllm "{
  \"baseUrl\": \"$VLLM_BASE_URL\",
  \"apiKey\": \"$VLLM_API_KEY\",
  \"api\": \"openai-completions\",
  \"timeoutSeconds\": 300,
  \"models\": [{
    \"id\": \"$VLLM_MODEL_ID\",
    \"name\": \"My Model\",
    \"reasoning\": true,
    \"compat\": { \"thinkingFormat\": \"qwen-chat-template\" },
    \"input\": [\"text\"],
    \"cost\": { \"input\": 0, \"output\": 0, \"cacheRead\": 0, \"cacheWrite\": 0 },
    \"contextWindow\": 32768,
    \"maxTokens\": 8192
  }]
}" --strict-json --merge
```

> Source `.env` first so the shell variables are available:
> ```bash
> source .env && openclaw config set models.providers.vllm ...
> ```

#### Step 2 — Set as the default model

```bash
openclaw models set "vllm/$VLLM_MODEL_ID"
```

#### Step 3 — Verify

```bash
openclaw models list --provider vllm
openclaw models status
```

#### Step 4 — Quick inference test

```bash
source .env
VLLM_API_KEY=$VLLM_API_KEY openclaw infer model run \
  --local \
  --model "vllm/$VLLM_MODEL_ID" \
  --thinking off \
  --prompt "Say hello and confirm your model name."
```

---

### WhatsApp Channel

WhatsApp is configured during `openclaw onboard`. The relevant section in `~/.openclaw/openclaw.json`:

```json
"channels": {
  "whatsapp": {
    "enabled": true,
    "selfChatMode": true,
    "dmPolicy": "allowlist",
    "allowFrom": ["91XXXXXXXXXX"]
  }
}
```

#### Check WhatsApp status

```bash
openclaw channels status
```

Expected output:
```
- WhatsApp default: enabled, configured, linked, running, connected, health:healthy
```

#### Update the allowlisted number

```bash
source .env
openclaw config set channels.whatsapp.allowFrom "[\"$WHATSAPP_TARGET\"]" --strict-json
```

---

## Running the Gateway

### Foreground (development / manual testing)

```bash
openclaw gateway run --force
```

Press `Ctrl+C` to stop.

### Background (persistent)

```bash
nohup openclaw gateway run --force > /tmp/openclaw-gateway.log 2>&1 &
echo "Gateway PID: $!"
```

### Check health

```bash
openclaw health
openclaw status
```

### Tail logs

```bash
tail -f /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log
```

---

## Running the WhatsApp Test

Both test scripts run **5 tests** end-to-end. They read all config from `.env` — no credentials are hardcoded.

| # | Test | What it checks |
|---|---|---|
| 1 | **Gateway Health** | Gateway is reachable (auto-starts if needed) |
| 2 | **WhatsApp Channel** | Channel is connected and healthy |
| 3 | **Model Inference** | Model responds to a one-shot prompt |
| 4 | **Direct Message Send** | Sends a plain text message (no AI) to WhatsApp |
| 5 | **E2E Agent → WhatsApp** | Full round-trip: model generates a reply, delivered to WhatsApp |

---

### Python test (recommended)

```bash
python3 test_whatsapp.py
```

- **No extra packages required** — uses stdlib only.
- Auto-discovers the correct nvm Node binary (semver-aware scan of `~/.nvm/versions/node/`).
- Reads config from `.env` via `config.py`.

**Example output:**

```
══════════════════════════════════════
  OpenClaw WhatsApp Integration Test
══════════════════════════════════════
[07:02:48] Model   : vllm/qwen3-6-35b-a3b
[07:02:48] Target  : +91XXXXXXXXXX

✅ PASS — Gateway is reachable
✅ PASS — WhatsApp channel is connected and healthy
✅ PASS — Model responded correctly
✅ PASS — Direct message delivered — Message ID: 3EB0...
✅ PASS — Agent reply delivered to WhatsApp — Sent message 3EB0...

  Tests run  : 5   Passed: 5   Warnings: 0   Failed: 0

All tests passed! ✅
```

---

### Shell test

```bash
chmod +x test_whatsapp.sh
bash test_whatsapp.sh
```

- Reads config via `source .env`.
- Requires bash 4+ and nvm in `~/.nvm`.

---

## Project Structure

```
openclaw_gateway/
├── .env                 ← Your local secrets (gitignored, never commit)
├── .env.example         ← Template — copy to .env and fill in values
├── .gitignore           ← Ignores .env and Python cache
├── config.py            ← Loads .env, exposes cfg object (Python)
├── test_whatsapp.py     ← Python integration test (recommended)
├── test_whatsapp.sh     ← Bash integration test
└── README.md            ← This file
```

**Key OpenClaw config files** (managed by openclaw, outside this repo):

```
~/.openclaw/
├── openclaw.json              ← Main config (gateway, channels, models, plugins)
├── openclaw.json.bak          ← Auto-backup before each config change
├── agents/main/agent/
│   ├── models.json            ← Provider/model definitions + API keys
│   └── openclaw-agent.sqlite  ← Agent session + auth store
├── credentials/whatsapp/      ← WhatsApp session credentials
└── workspace/                 ← Agent workspace files
```

---

## Troubleshooting

### `openclaw: Node.js v22.19+ is required`

Your shell's `node` is an older nvm version:

```bash
nvm use 22
nvm alias default 22
```

The Python test handles this automatically by scanning `~/.nvm/versions/node/` for a compatible binary — no manual `nvm use` needed.

---

### `CLI transcript compaction failed: Already compacted`

This is a **cosmetic bug** in openclaw on new sessions with nothing to compact. It does **not** affect message delivery — WhatsApp messages are sent successfully before this error appears.

---

### Gateway won't start (port conflict)

```bash
openclaw gateway run --force   # --force kills the existing process on port 18789
```

---

### WhatsApp channel shows `disconnected`

The WhatsApp Web session may have expired. Re-pair:

```bash
openclaw channels add    # Guided re-pairing with QR code
```

---

### Model returns no response / timeout

1. Verify the endpoint is reachable:
   ```bash
   source .env
   curl -s -o /dev/null -w "%{http_code}" \
     "$VLLM_BASE_URL/models" \
     -H "Authorization: Bearer $VLLM_API_KEY"
   # Should return 200
   ```
2. Increase `timeoutSeconds` in the vLLM provider config.
3. Tail gateway logs for errors:
   ```bash
   tail -f /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log | grep -i "error\|fail\|warn"
   ```
