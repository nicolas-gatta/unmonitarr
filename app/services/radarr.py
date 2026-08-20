from .arr_client import ArrClient

import requests
import time

class RadarrClient(ArrClient):
    @property
    def headers(self):
        return {"X-Api-Key": self.cfg["radarr_api_key"]}

    @property
    def base_url(self):
        return self.cfg["radarr_url"].rstrip("/")

    def _already_unmonitored(self, item):
        return not item.get("monitored", False)

    def _apply_unmonitor(self, item):
        item["monitored"] = False
        return item

    def _lookup_endpoint(self):
        return "movie"
    
    def _id_param(self):
        return "tmdbId"
        