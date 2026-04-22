"""Cloud and API probing helpers focused on latency and response consistency."""

from __future__ import annotations

import hashlib
import time
from statistics import mean

try:
    import requests
except ImportError:  # pragma: no cover - optional dependency
    requests = None


def probe(url: str, timeout: float = 5.0, session=None):
    if session is None and requests is None:  # pragma: no cover - depends on optional dependency
        raise RuntimeError("requests is required for live HTTP probes")

    client = session or requests.Session()
    started_at = time.perf_counter()

    try:
        response = client.get(url, timeout=timeout)
        latency = time.perf_counter() - started_at
        return {
            "ok": True,
            "status": response.status_code,
            "latency": latency,
            "size": len(response.content),
            "fingerprint": hashlib.sha256(response.content).hexdigest()[:16],
        }
    except Exception as exc:
        latency = time.perf_counter() - started_at
        return {
            "ok": False,
            "status": None,
            "latency": latency,
            "size": 0,
            "fingerprint": None,
            "error": str(exc),
        }


def probe_consistency(
    url: str,
    attempts: int = 3,
    timeout: float = 5.0,
    session=None,
):
    results = [probe(url=url, timeout=timeout, session=session) for _ in range(attempts)]
    successful = [result for result in results if result["ok"]]
    fingerprints = sorted(
        {result["fingerprint"] for result in successful if result["fingerprint"]}
    )

    return {
        "url": url,
        "attempts": attempts,
        "success_rate": (len(successful) / attempts) if attempts else 0.0,
        "average_latency": mean([result["latency"] for result in results]) if results else 0.0,
        "status_codes": sorted({result["status"] for result in successful if result["status"] is not None}),
        "unique_fingerprints": fingerprints,
        "consistent_payload": len(fingerprints) <= 1,
        "results": results,
    }
