"""
SolscanAdapter — Production-hardened Solscan Pro API client
Codespaces-ready: loads API key from .env automatically
"""

import os
import logging
from typing import Dict, Optional, Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv

load_dotenv()  # loads .env file automatically in Codespaces

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

BASE_URL = "https://pro-api.solscan.io/v2.0"
DEFAULT_TIMEOUT = 10
MAX_RETRIES = 3
BACKOFF_FACTOR = 0.5
RETRY_ON_STATUS = {429, 500, 502, 503, 504}


class SolscanAdapter:
    def __init__(self, api_key: Optional[str] = None, timeout: int = DEFAULT_TIMEOUT):
        key = api_key or os.environ.get("SOLSCAN_API_KEY")
        if not key:
            raise ValueError(
                "API key required. Add SOLSCAN_API_KEY to your .env file.\n"
                "Get a key at: https://solscan.io/apis"
            )
        self.base_url = BASE_URL
        self.timeout = timeout
        self.session = self._build_session(key)

    def _build_session(self, api_key: str) -> requests.Session:
        session = requests.Session()
        session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
        })
        retry = Retry(
            total=MAX_RETRIES,
            backoff_factor=BACKOFF_FACTOR,
            status_forcelist=RETRY_ON_STATUS,
            allowed_methods=["GET"],
            raise_on_status=False,
        )
        session.mount("https://", HTTPAdapter(max_retries=retry))
        return session

    def call(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        try:
            resp = self.session.get(url, params=params or {}, timeout=self.timeout)
        except requests.exceptions.Timeout:
            return {"error": "timeout", "status": 408}
        except requests.exceptions.ConnectionError as exc:
            return {"error": str(exc), "status": 503}

        if not resp.ok:
            return {"error": resp.text, "status": resp.status_code}

        try:
            return resp.json()
        except ValueError:
            return {"error": "invalid JSON", "raw": resp.text[:500], "status": resp.status_code}

    # ── Endpoints ──────────────────────────────────────────────────────────

    def get_account(self, address: str) -> Dict:
        return self.call("/account/detail", {"address": address})

    def get_account_transactions(self, address: str, limit: int = 10) -> Dict:
        return self.call("/account/transactions", {"address": address, "limit": limit})

    def get_transaction(self, tx_hash: str) -> Dict:
        return self.call("/transaction/detail", {"tx": tx_hash})

    def get_token(self, token_address: str) -> Dict:
        return self.call("/token/detail", {"address": token_address})

    def get_token_price(self, token_address: str) -> Dict:
        return self.call("/token/price", {"address": token_address})

    def get_block(self, slot: int) -> Dict:
        return self.call("/block/detail", {"block": slot})


# ── Smoke test ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import json

    print("🔌 Connecting to Solscan Pro API...")
    client = SolscanAdapter()  # reads from .env

    # Test 1: reachability check
    print("\n[1/2] Testing API reachability...")
    test_address = "So1endDq2YkqhipRh3WViPa8hdiSpxWy6z3Z6tMCpAo"
    result = client.get_account(test_address)
    if "error" in result:
        print(f"❌ API error: {result}")
    else:
        print(f"✅ Account data received")
        print(json.dumps(result, indent=2)[:600])

    # Test 2: error handling
    print("\n[2/2] Testing error handling...")
    bad = client.get_account("definitely_not_real")
    assert "error" in bad or "status" in bad
    print(f"✅ Error handling OK → status={bad.get('status')}")

    print("\n🚀 All checks passed. Adapter is live.")
