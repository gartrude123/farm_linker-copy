"""FARM_LINKER - Main Flask application"""

import os
import sys

# Ensure the project root is importable regardless of where the app is launched from
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from flask import Flask, render_template, redirect, url_for, session, flash
from config import Config
from services.db import get_db, close_db
from routes.auth import auth_bp, login_required
from routes.farmer import farmer_bp
from routes.buyer import buyer_bp
from routes.admin import admin_bp
from routes.orders import orders_bp


def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(Config)

    # Context processors
    @app.context_processor
    def inject_globals():
        return dict(csrf_token=lambda: session.get("_csrf_token", ""))

    @app.before_request
    def init_request():
        try:
            get_db()
        except Exception as e:
            print(f"[DB] Connection error: {e}")
        if "_csrf_token" not in session:
            import os
            session["_csrf_token"] = os.urandom(16).hex()

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(farmer_bp)
    app.register_blueprint(buyer_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(orders_bp)

    @app.teardown_appcontext
    def shutdown_db(exception=None):
        # Keep the client alive; don't close on every request
        pass

    @app.route("/")
    def index():
        if "user_id" in session:
            return redirect(url_for("auth.dashboard"))
        return redirect(url_for("auth.login"))

    @app.route("/health")
    def health():
        try:
            db = get_db()
            if db is None:
                return {"status": "unhealthy", "error": "Database not connected"}, 500
            db.command("ping")
            return {"status": "healthy", "database": "connected"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}, 500

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
