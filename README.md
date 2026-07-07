# OpenClaw Gateway — Setup & WhatsApp Integration

A lightweight local AI gateway powered by [OpenClaw](https://docs.openclaw.ai), running an OpenAI-compatible LLM endpoint with full WhatsApp channel integration and mobile device pairing.

---

## Table of Contents

1. [Environment Configuration](#1-environment-configuration)
2. [How to Setup Gateway](#2-how-to-setup-gateway)
   - [Initial Onboarding](#initial-onboarding)
   - [Running the Gateway](#running-the-gateway)
   - [Mobile Pairing & Remote Access (ngrok)](#mobile-pairing--remote-access-ngrok)
3. [How to Connect WhatsApp Channel](#3-how-to-connect-whatsapp-channel)
   - [Linking WhatsApp Account](#linking-whatsapp-account)
   - [Configuring Allowlist](#configuring-allowlist)
   - [Verifying Channel Status](#verifying-channel-status)
4. [How to Run Test Cases](#4-how-to-run-test-cases)
   - [Running the Automated Tests](#running-the-automated-tests)
   - [Test Suite Breakdown](#test-suite-breakdown)

---

## 1. Environment Configuration

All sensitive values (API keys, phone numbers) are loaded from a local `.env` file. 

1. Copy the example environment template:
   ```bash
   cp .env.example .env
   ```
2. Configure your specific values in `.env`:
   ```bash
   # .env
   VLLM_BASE_URL=https://your-endpoint.example.com/v1
   VLLM_API_KEY=your_api_key_here
   VLLM_MODEL_ID=your-model-id

   WHATSAPP_TARGET=91XXXXXXXXXX       # Target number without leading +
   WHATSAPP_TARGET_E164=+91XXXXXXXXXX # Target number with leading + (E.164 format)
   ```

---

## 2. How to Setup Gateway

### Initial Onboarding

Run the interactive OpenClaw setup wizard once to generate your initial workspace, authentication tokens, and default configuration (`~/.openclaw/openclaw.json`):

```bash
openclaw onboard
```

### Running the Gateway

You can run the gateway service in the foreground or persist it as a daemon in the background:

- **Foreground (Interactive / Development)**:
  ```bash
  openclaw gateway run --force
  ```
  *(Press `Ctrl+C` to stop)*

- **Background (Persistent Daemon)**:
  ```bash
  nohup openclaw gateway run --force > /tmp/openclaw-gateway.log 2>&1 &
  echo "Gateway PID: $!"
  ```

- **Check Gateway Health & Status**:
  ```bash
  openclaw health
  openclaw status
  ```

### Mobile Pairing & Remote Access (ngrok)

To bridge your local gateway with the OpenClaw mobile application over the internet :

2. **Remote Access via ngrok Tunnel**:
   If connecting over different networks (e.g., mobile data vs. Wi-Fi), expose your local port (`18789`) via ngrok and generate a secure WebSockets (`wss://`) pairing code:
   ```bash
   # Generate pairing QR / setup code using your ngrok WSS tunnel URL
   openclaw qr --url wss://your-domain.ngrok-free.app
   ```
   Copy the generated **Setup Code** (or scan the QR code) directly into the OpenClaw mobile application.
3. **Approve Device Pairing**:
   Check pending device connection requests and approve them:
   ```bash
   openclaw devices list
   openclaw devices approve <device-id>
   ```

---

## 3. How to Connect WhatsApp Channel

### Linking WhatsApp Account

1. Start the interactive channel setup to link your WhatsApp account:
   ```bash
   openclaw channels add
   ```
2. Follow the on-screen prompts and scan the generated QR code using WhatsApp on your phone (**Linked Devices** → **Link a Device**).

### Configuring Allowlist

To ensure your agent only interacts with authorized phone numbers, update your WhatsApp allowlist using the target defined in your `.env`:

```bash
source .env
openclaw config set channels.whatsapp.allowFrom "[\"$WHATSAPP_TARGET\"]" --strict-json
```

### Verifying Channel Status

Check that the WhatsApp service is running, connected, and healthy:

```bash
openclaw channels status
```

*Expected status output:*
```text
- WhatsApp default: enabled, configured, linked, running, connected, health:healthy
```

---

## 4. How to Run Test Cases

The project includes an automated end-to-end integration test suite that verifies gateway health, channel connectivity, LLM inference, and message delivery.

### Running the Automated Tests

run the Python test suite, which uses standard library components and automatically discovers your Node/OpenClaw environment:

```bash
python3 test_whatsapp.py
```

*Alternatively, you can run the Bash test script:*
```bash
chmod +x test_whatsapp.sh
bash test_whatsapp.sh
```

### Test Suite Breakdown

The automated test suite executes **5 sequential verification checks**:

| # | Test Name | Description |
|---|---|---|
| **1** | **Gateway Health** | Verifies that the local OpenClaw gateway is reachable and auto-starts if offline. |
| **2** | **WhatsApp Channel** | Confirms that the WhatsApp channel session is active, authenticated, and healthy. |
| **3** | **Model Inference** | Tests communication with the LLM provider (`vLLM` / OpenAI-compatible endpoint) via a one-shot prompt. |
| **4** | **Direct Message Send** | Validates raw message delivery by sending a plain text ping directly to the target WhatsApp number. |
| **5** | **E2E Agent → WhatsApp** | Performs a full round-trip verification where the agent generates an AI response and delivers it to WhatsApp. |

