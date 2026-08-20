from .arr_client import ArrClient
import requests
import time

class SonarrClient(ArrClient):
    @property
    def headers(self):
        return {"X-Api-Key": self.cfg["sonarr_api_key"]}

    @property
    def base_url(self):
        return self.cfg["sonarr_url"].rstrip("/")

    def _already_unmonitored(self, item):
        return not item.get("monitored", False) and not self.cfg["unmonitor_sonarr_seasons"]

    def _apply_unmonitor(self, item):
        item["monitored"] = False
        if self.cfg["unmonitor_sonarr_seasons"]:
            for season in item.get("seasons", []):
                season["monitored"] = False
        return item

    def _lookup_endpoint(self):
        return "series"
    
    def _id_param(self):
        return "tvdbId"