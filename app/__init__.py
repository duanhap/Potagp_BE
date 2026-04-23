from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from flask_apscheduler import APScheduler
from app.controllers.user_controller import user_bp
# ... (các imports BP khác)
from app.controllers.streak_controller import streak_bp

scheduler = APScheduler()

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Configure Scheduler
    app.config['SCHEDULER_API_ENABLED'] = True
    scheduler.init_app(app)
    scheduler.start()

    # Đăng ký Job kiểm tra streak lúc 0h00 hàng ngày (Giờ VN)
    # Vì Server Render đặt ở Singapore (GMT+8), ta chạy lúc 23:00 (GMT+7)
    @scheduler.task('cron', id='check_daily_streak', hour=23, minute=0)
    def daily_streak_job():
        with app.app_context():
            from app.tasks.streak_task import run_midnight_streak_check
            run_midnight_streak_check()

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
    app.register_blueprint(reward_bp, url_prefix='/api/rewards')
    app.register_blueprint(streak_bp, url_prefix='/api/streaks')

    @app.route('/')
    def index():
        return {"message": "Potago Backend is running"}

    return app
