import requests
from typing import Any, Dict, Optional, Union, List

class APIClient:
    def __init__(self, base_url: str = "http://127.0.0.1:5000"):
        self.base_url = base_url.rstrip("/")

    def health(self) -> Dict[str, Any]:
        r = requests.get(f"{self.base_url}/health", timeout=10)
        r.raise_for_status()
        return r.json()

    def ingest(self, payload: Union[Dict[str, Any], List[Dict[str, Any]]]) -> Dict[str, Any]:
        r = requests.post(f"{self.base_url}/ingest", json=payload, timeout=30)
        r.raise_for_status()
        return r.json()

    def list_events(self, params: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        r = requests.get(f"{self.base_url}/events", params=params or {}, timeout=30)
        r.raise_for_status()
        return r.json()

    def list_alerts(self, params: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        r = requests.get(f"{self.base_url}/alerts", params=params or {}, timeout=30)
        r.raise_for_status()
        return r.json()