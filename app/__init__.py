from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from app.controllers.user_controller import user_bp
from app.controllers.word_set_controller import word_set_bp
from app.controllers.word_controller import word_bp
from app.controllers.video_controller import video_bp
from app.controllers.subtitle_controller import subtitle_bp
from app.controllers.sentence_pattern_controller import sentence_pattern_bp
from app.controllers.sentence_controller import sentence_bp

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
    app.register_blueprint(video_bp, url_prefix='/api/videos')
    app.register_blueprint(subtitle_bp, url_prefix='/api/subtitles')
    app.register_blueprint(sentence_pattern_bp, url_prefix='/api/sentence-patterns')
    app.register_blueprint(sentence_bp, url_prefix='/api/sentences')

    @app.route('/')
    def index():
        return {"message": "Potago Backend is running"}

    return app
