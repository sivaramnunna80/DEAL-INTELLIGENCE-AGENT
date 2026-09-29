import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from urllib import error, request


class Hindsight:
    """Simple memory client with an in-memory fallback for local development.

    The project expects a service at http://localhost:8888, but this implementation
    keeps working even when that service is not running by persisting data in a
    process-local dictionary. That makes the repo usable immediately for local
    experiments and tests.
    """

    _banks: Dict[str, List[Dict[str, Any]]] = {}

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: float = 1.0,
    ):
        self.base_url = (base_url or os.getenv("HINDSIGHT_URL", "http://localhost:8888")).rstrip("/")
        self.timeout = timeout
        self.remote_enabled = os.getenv("HINDSIGHT_ENABLED", "false").lower() in {"1", "true", "yes", "on"}

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def _bank_store(self, bank_id: str) -> List[Dict[str, Any]]:
        if bank_id not in self._banks:
            self._banks[bank_id] = []
        return self._banks[bank_id]

    def _call_http(self, method: str, path: str, payload: Optional[Dict[str, Any]] = None):
        url = f"{self.base_url}{path}"
        data = None
        headers = {"Content-Type": "application/json"}

        if payload is not None:
            data = json.dumps(payload).encode("utf-8")

        req = request.Request(url, data=data, headers=headers, method=method)

        try:
            with request.urlopen(req, timeout=self.timeout) as response:
                body = response.read()
                if not body:
                    return None
                return json.loads(body.decode("utf-8"))
        except (error.URLError, error.HTTPError, TimeoutError, ValueError):
            return None

    def retain(
        self,
        bank_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        payload = {
            "bank_id": bank_id,
            "content": content,
            "metadata": metadata or {},
            "timestamp": self._utc_now(),
        }

        response = self._call_http("POST", "/retain", payload) if self.remote_enabled else None
        if response is not None:
            return response

        store = self._bank_store(bank_id)
        entry = {
            "id": len(store),
            "content": content,
            "metadata": metadata or {},
            "timestamp": payload["timestamp"],
        }
        store.append(entry)
        return {"status": "stored", "bank_id": bank_id, "entry": entry}

    def recall(
        self,
        bank_id: str,
        query: str,
        top_k: int = 5,
        **kwargs,
    ):
        payload = {
            "bank_id": bank_id,
            "query": query,
            "top_k": top_k,
        }

        response = self._call_http("POST", "/recall", payload) if self.remote_enabled else None
        if response is not None:
            return response

        store = self._bank_store(bank_id)
        if not store:
            return []

        query_text = (query or "").lower().strip()
        scored_entries = []

        for entry in store:
            content = str(entry.get("content", ""))
            metadata = str(entry.get("metadata", ""))
            haystack = f"{content} {metadata}".lower()

            score = 0
            if query_text:
                if query_text in haystack:
                    score += 20
                for token in query_text.split():
                    if token and token in haystack:
                        score += 5

            if score > 0:
                scored_entries.append((score, entry))

        scored_entries.sort(key=lambda item: item[0], reverse=True)
        matches = [entry for _, entry in scored_entries[: max(1, top_k)]]
        return matches


# Backward-compatible alias for the project's original import pattern.
HindsightClient = Hindsight
