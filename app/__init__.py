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
from app.controllers.flashcard_controller import flashcard_bp
from app.controllers.item_controller import item_bp
from app.controllers.reward_controller import reward_bp

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
    app.register_blueprint(flashcard_bp, url_prefix='/api/flashcards')
    app.register_blueprint(item_bp, url_prefix='/api/users/items')
    app.register_blueprint(reward_bp, url_prefix='/api/rewards')

    @app.route('/')
    def index():
        return {"message": "Potago Backend is running"}

    return app
