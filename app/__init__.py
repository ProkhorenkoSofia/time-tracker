from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app():
    import os
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(base_dir)
    template_dir = os.path.join(project_root, 'templates')
    
    if not os.path.exists(template_dir):
        os.makedirs(template_dir)
    
    app = Flask(__name__, template_folder=template_dir)
    
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///time_tracker.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key')
    
    db.init_app(app)
    
    from app.routes.main_routes import bp as main_bp
    app.register_blueprint(main_bp)
    
    with app.app_context():
        try:
            from app.models import User, Category, Event, Template
            db.create_all()
            print("✅ Таблицы базы данных созданы/проверены")
        except Exception as e:
            print(f"⚠️ Ошибка при создании таблиц: {e}")
    
    return app
