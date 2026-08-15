from flask import Flask, jsonify
from flask_cors import CORS

from config import Config
from extensions import db

from models.dumping_site import DumpingSite
from routes.dumping_sites import dumping_sites_bp
from routes.detections import detections_bp


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    CORS(app)

    db.init_app(app)

    # Existing dumping sites API
    app.register_blueprint(
        dumping_sites_bp,
        url_prefix="/api/dumping-sites"
    )

    # AI detection API
    app.register_blueprint(
        detections_bp
    )

    @app.get("/api/health")
    def health():
        return jsonify({
            "status": "ok",
            "service": "WasteGuard AI API"
        })

    with app.app_context():
        db.create_all()

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )