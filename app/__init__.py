from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
import os

# Инициализация расширений
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    # Конфигурация
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # База данных
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///time_tracker.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Инициализация расширений
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # Настройка Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    from app.routes.auth_routes import auth_bp
    from app.routes.main_routes import main_bp
    from app.routes.api_routes import api_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
    
    # Создание таблиц при первом запуске
    with app.app_context():
        from app import models
        db.create_all()
        
        # Создаем администратора по умолчанию (для демонстрации)
        from app.models import User
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', telegram_id='000000')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("✅ Created default admin user")
    
    return app
