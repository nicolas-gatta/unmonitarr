from flask import Blueprint, render_template, jsonify

from .. import stats as stats_module

bp = Blueprint("dashboard", __name__)


@bp.route("/", methods=["GET"])
def dashboard():
    return render_template("dashboard.html", stats=stats_module.get())

@bp.route("/api/stats", methods=["GET"])
def api_stats():
    """
    Plain JSON version of the dashboard stats, for external dashboards
    (Homepage, Homarr, Grafana, your own scripts) or the send_fake_webhook.py
    tool to verify a test event actually landed.
    """
    return jsonify(stats_module.get())