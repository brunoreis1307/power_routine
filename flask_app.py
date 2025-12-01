flask_app.py
from flask import Flask, jsonify
from config import Config
from models import db
from routes.auth_routes import auth_bp
from routes.food_routes import food_bp
from routes.mealplan_routes import mp_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    # register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(food_bp)
    app.register_blueprint(mp_bp)

    @app.route("/")
    def index():
        return jsonify({"msg": "Power Routine API - Diet module (dev)"})

    return app

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0", port=5000)
