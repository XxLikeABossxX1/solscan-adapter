# Solscan Adapter

A production-hardened Python client for the [Solscan Pro API](https://solscan.io/apis), designed to plug into LangGraph agent workflows.

## Features

- Auto-retry with exponential backoff (handles rate limits + 5xx errors)
- Timeout protection — no hung processes
- API key loaded from `.env` — never hardcoded
- Consistent error contract — all failures return `{"error": ..., "status": ...}`
- LangGraph tool schema included and ready to wire in

## Quickstart

### 1. Get a Solscan Pro API key
Sign up at [solscan.io/apis](https://solscan.io/apis).

### 2. Clone & open in Codespaces
Hit the green **Code** button on this repo → **Codespaces** → **Create codespace on main**.  
Dependencies install automatically.

### 3. Configure your key
```bash
cp .env.example .env
# Edit .env and paste your key
```

### 4. Run the smoke test
```bash
python solscan_adapter.py
```

Expected output:
```
🔌 Connecting to Solscan Pro API...
✅ Account data received
✅ Error handling OK
🚀 All checks passed. Adapter is live.
```

## Endpoints

| Method | Description |
|---|---|
| `get_account(address)` | Account detail — balance, tokens, tx count |
| `get_account_transactions(address, limit)` | Recent transactions for an account |
| `get_transaction(tx_hash)` | Decoded transaction detail |
| `get_token(token_address)` | Token metadata — name, symbol, supply |
| `get_token_price(token_address)` | Current market price |
| `get_block(slot)` | Block detail by slot number |
| `call(endpoint, params)` | Raw call — hit any endpoint directly |

## Usage

```python
from solscan_adapter import SolscanAdapter

client = SolscanAdapter()  # reads SOLSCAN_API_KEY from .env

account = client.get_account("So1endDq2YkqhipRh3WViPa8hdiSpxWy6z3Z6tMCpAo")
tx = client.get_transaction("your_tx_hash_here")
token = client.get_token("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")  # USDC
```

## LangGraph Integration

`LANGGRAPH_TOOLS` and `dispatch_tool()` are exported from the module:

```python
from solscan_adapter import SolscanAdapter, LANGGRAPH_TOOLS, dispatch_tool

adapter = SolscanAdapter()

# In your graph node:
result = dispatch_tool(adapter, tool_call.name, tool_call.args)
```

## Project Structure

```
solscan-adapter/
├── .devcontainer/
│   └── devcontainer.json   # Codespaces config — auto-installs deps
├── .env.example            # Template — safe to commit
├── .env                    # Your actual key — never commit this
├── .gitignore
├── requirements.txt
└── solscan_adapter.py
```

## Roadmap

- [ ] Async version (`httpx`-based) for parallel agent calls
- [ ] LangGraph graph scaffold wired to this adapter
- [ ] Helius Yellowstone gRPC fallback for raw SVM streams
- [ ] Eclipse + Fogo chain support via Solscan EaaS

## License
MIT
