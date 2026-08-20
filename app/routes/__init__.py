from .webhook import bp as webhook_bp
from .settings import bp as settings_bp
from .dashboard import bp as dashboard_bp

all_blueprints = [webhook_bp, settings_bp, dashboard_bp]

__all__ = [
    "webhook_bp", 
    "settings_bp", 
    "dashboard_bp"
    ]