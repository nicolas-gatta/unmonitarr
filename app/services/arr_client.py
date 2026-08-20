from abc import ABC, abstractmethod

import requests
import logging
import time

log = logging.getLogger(__name__)


class ArrClient(ABC):
    
    def __init__(self, cfg):
        self.cfg = cfg
    
    @abstractmethod
    def _lookup_endpoint(self): 
        pass    # "movie" or "series"
    
    @abstractmethod
    def _id_param(self): 
        pass   
    
    @abstractmethod
    def base_url(self) -> str:
        pass 
    
    @abstractmethod 
    def _apply_unmonitor(self, item):
        pass 
    
    @abstractmethod    
    def _already_unmonitored(self, item):
        pass 
    
    def _find_match(self, candidates):
        return candidates[0] if candidates else None
        
    def test_connection(self) -> bool:
        """Generic health check - same shape for both apps."""
        try:
            resp = requests.get(f"{self.base_url}/api/v3/system/status",
                                    headers=self.headers, timeout=10)
            if resp.status_code == 401:
                return {"ok": False, "error": "Unauthorized - check the API key."}
            resp.raise_for_status()
            data = resp.json()
            return {"ok": True, "version": data.get("version", "unknown")}
        except requests.RequestException as e:
            return {"ok": False, "error": str(e)}
        
    def unmonitor(self, external_id, on_success):
        """external_id = tmdb_id for Radarr, tvdb_id for Sonarr."""
    
        for attempt in range(1, self.cfg["retry_attempts"] + 1):
            try:
                resp = requests.get(
                    f"{self.base_url}/api/v3/{self._lookup_endpoint()}",
                    params={self._id_param(): external_id},
                    headers=self.headers,
                    timeout=10,
                )
                resp.raise_for_status()
                items = resp.json()
            except requests.RequestException as e:
                log.warning("Lookup failed (attempt %s/%s): %s", attempt, self.cfg["retry_attempts"], e)
                time.sleep(self.cfg["retry_delay_seconds"])
                continue
    
            if items:
                match = self._find_match(items)
                if match:
                    if self._already_unmonitored(match):
                        log.info("%s '%s' (%s=%s) already unmonitored.", self._lookup_endpoint().title(), self._id_param(), match.get("title"), external_id)
                        return
    
                match = self._apply_unmonitor(match)
                put_resp = requests.put(
                    f"{self.base_url}/api/v3/{self._lookup_endpoint()}/{match['id']}",
                    json=match,
                    headers=self.headers,
                    timeout=10,
                )
                
                if put_resp.ok:
                    title = match.get("title", str(external_id))
                    log.info("Unmonitored '%s' (%s=%s).", self._id_param(), title, external_id)
                    on_success(f"{self._lookup_endpoint()}", title)
                else:
                    log.error("Failed to update %s %s arr: %s %s",
                                self._lookup_endpoint(), match.get("id"), put_resp.status_code, put_resp.text)
                return
    
            log.info("%s %s=%s not in  yet (attempt %s/%s), retrying...",
                        self._lookup_endpoint().title(), self._id_param(),external_id, attempt, self.cfg["retry_attempts"])
            time.sleep(self.cfg["retry_delay_seconds"])