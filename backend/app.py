from flask import Flask
from backend.config import Config
from backend.routes.health_routes import health_bp
from backend.routes.predict_routes import predict_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.register_blueprint(health_bp)
    app.register_blueprint(predict_bp)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
