from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from app.controllers.user_controller import user_bp
from app.controllers.word_set_controller import word_set_bp
from app.controllers.word_controller import word_bp

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Configure Swagger
    app.config['SWAGGER'] = {
        'title': 'Potago API',
        'uiversion': 3,
        'specs_route': '/swagger/'
    }
    Swagger(app)

    # Register Blueprints
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(word_set_bp, url_prefix='/api/word-sets')
    app.register_blueprint(word_bp, url_prefix='/api/words')

    @app.route('/')
    def index():
        return {"message": "Potago Backend is running"}

    return app
