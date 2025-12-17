from flask import Blueprint

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return "Time Tracker работает!"

from app import db
from app.models import User

@bp.route('/test-db')
def test_database():
    """Проверка работы базы данных"""
    try:
        # Попытка выполнить простой запрос
        user_count = User.query.count()
        return f"База данных работает! Пользователей: {user_count}"
    except Exception as e:
        return f"Ошибка базы данных: {str(e)}", 500

@bp.route('/create-test-user')
def create_test_user():
    """Создание тестового пользователя"""
    try:
        from app.models import User
        test_user = User(name="Test User", telegram_id="123456")
        db.session.add(test_user)
        db.session.commit()
        return "Тестовый пользователь создан!"
    except Exception as e:
        return f"Ошибка: {str(e)}", 500
