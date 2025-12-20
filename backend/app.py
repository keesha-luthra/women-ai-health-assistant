import os
from flask import Flask, send_from_directory
from backend.config import Config
from backend.routes.predict_routes import predict_bp
from backend.routes.health_routes import health_bp


def create_app():
    app = Flask(
        __name__,
        static_folder="static",
        static_url_path="/static"
    )

    app.config.from_object(Config)

    # ✅ ENSURE upload folder exists
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    app.register_blueprint(health_bp)
    app.register_blueprint(predict_bp)

    @app.route("/")
    def serve_frontend():
        return send_from_directory(app.static_folder, "index.html")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
