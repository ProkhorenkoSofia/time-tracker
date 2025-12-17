from flask import Blueprint, render_template, jsonify, request
from app import db
from app.models import User, Category, Event, Template
from datetime import datetime, timedelta
import json

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Главная страница с дашбордом БД"""
    return render_template('index.html')

@bp.route('/debug')
def debug():
    """Страница отладки"""
    import os
    return {
        'current_directory': os.getcwd(),
        'template_folder': bp.template_folder if hasattr(bp, 'template_folder') else 'not set',
        'templates_exists': os.path.exists('templates'),
        'database_uri': 'set' if db.engine else 'not set',
        'python_version': os.sys.version
    }

@bp.route('/api/stats')
def api_stats():
    """Статистика БД"""
    return jsonify({
        'users': User.query.count(),
        'categories': Category.query.count(),
        'events': Event.query.count(),
        'templates': Template.query.count()
    })

@bp.route('/api/users')
def api_users():
    """Все пользователи"""
    users = User.query.order_by(User.id.desc()).limit(20).all()
    return jsonify([{
        'id': u.id,
        'name': u.name,
        'telegram_id': u.telegram_id,
        'created_at': u.created_at.isoformat() if u.created_at else None
    } for u in users])

@bp.route('/api/events')
def api_events():
    """Все события"""
    events = Event.query.order_by(Event.start_time.desc()).limit(50).all()
    return jsonify([{
        'id': e.id,
        'user_id': e.user_id,
        'category_id': e.category_id,
        'start_time': e.start_time.isoformat() if e.start_time else None,
        'end_time': e.end_time.isoformat() if e.end_time else None,
        'type': e.type,
        'duration': int((e.end_time - e.start_time).total_seconds() / 60) if e.end_time and e.start_time else 0
    } for e in events])

@bp.route('/api/create-test-data', methods=['POST'])
def create_test_data():
    """Создание полного набора тестовых данных"""
    try:
        # Создаем пользователя
        user = User(
            name='Тестовый Пользователь',
            telegram_id='987654321'
        )
        db.session.add(user)
        db.session.flush()
        
        # Создаем категории
        categories = []
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
        names = ['Учеба', 'Работа', 'Спорт', 'Отдых', 'Хобби']
        
        for i, (name, color) in enumerate(zip(names, colors)):
            cat = Category(
                name=name,
                color=color,
                user_id=user.id
            )
            categories.append(cat)
        
        db.session.add_all(categories)
        db.session.flush()
        
        # Создаем события
        events = []
        now = datetime.utcnow()
        
        for i in range(10):
            start = now + timedelta(hours=i*2)
            end = start + timedelta(hours=1, minutes=30)
            
            event = Event(
                user_id=user.id,
                category_id=categories[i % len(categories)].id,
                start_time=start,
                end_time=end,
                type='plan' if i % 2 == 0 else 'fact'
            )
            events.append(event)
        
        db.session.add_all(events)
        
        # Создаем шаблон
        template_data = {
            "schedule": [
                {"day": "Понедельник", "tasks": ["Лекции", "Лабы"]},
                {"day": "Вторник", "tasks": ["Проект", "Тренировка"]}
            ]
        }
        
        template = Template(
            user_id=user.id,
            name='Мое расписание',
            data=json.dumps(template_data, ensure_ascii=False)
        )
        db.session.add(template)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Создано: 1 пользователь, {len(categories)} категорий, {len(events)} событий, 1 шаблон'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/api/clear-db', methods=['POST'])
def clear_database():
    """Очистка всех данных (только для теста!)"""
    try:
        # Удаляем в правильном порядке (из-за foreign keys)
        Event.query.delete()
        Category.query.delete()
        Template.query.delete()
        User.query.delete()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'База данных очищена'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/api/health')
def health_check():
    """Проверка работоспособности"""
    try:
        user_count = User.query.count()
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'users_count': user_count,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e)
        }), 500
