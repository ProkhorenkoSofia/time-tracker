from flask import Blueprint, render_template, jsonify
from app import db
from app.models import User, Category, Event, Template
from datetime import datetime, timedelta

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Главная страница с информацией о БД"""
    return render_template('index.html')

@bp.route('/test-db')
def test_db():
    """Проверка работы базы данных"""
    try:
        user_count = User.query.count()
        category_count = Category.query.count()
        event_count = Event.query.count()
        template_count = Template.query.count()
        
        return jsonify({
            'status': 'success',
            'message': 'База данных работает',
            'data': {
                'users': user_count,
                'categories': category_count,
                'events': event_count,
                'templates': template_count
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@bp.route('/api/stats')
def api_stats():
    """API для получения статистики"""
    return jsonify({
        'users': User.query.count(),
        'categories': Category.query.count(),
        'events': Event.query.count(),
        'templates': Template.query.count()
    })

@bp.route('/api/users')
def api_users():
    """API для получения пользователей"""
    users = User.query.all()
    return jsonify([{
        'id': u.id,
        'name': u.name,
        'telegram_id': u.telegram_id,
        'created_at': u.created_at.isoformat() if u.created_at else None
    } for u in users])

@bp.route('/api/events')
def api_events():
    """API для получения событий"""
    events = Event.query.order_by(Event.start_time.desc()).limit(20).all()
    return jsonify([{
        'id': e.id,
        'type': e.type,
        'start_time': e.start_time.isoformat(),
        'end_time': e.end_time.isoformat(),
        'duration': int((e.end_time - e.start_time).total_seconds() / 60),
        'user_id': e.user_id,
        'category_id': e.category_id
    } for e in events])

@bp.route('/api/recent-events')
def api_recent_events():
    """API для получения последних 5 событий"""
    events = Event.query.order_by(Event.start_time.desc()).limit(5).all()
    return jsonify([{
        'type': e.type,
        'start_time': e.start_time.isoformat(),
        'end_time': e.end_time.isoformat(),
        'duration': int((e.end_time - e.start_time).total_seconds() / 60)
    } for e in events])

@bp.route('/api/create-test-user', methods=['POST'])
def api_create_test_user():
    """API для создания тестового пользователя"""
    try:
        user = User(
            name=f"Test User {datetime.now().strftime('%H:%M:%S')}",
            telegram_id=str(int(datetime.now().timestamp()))
        )
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'Пользователь создан (ID: {user.id})'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@bp.route('/api/create-test-event', methods=['POST'])
def api_create_test_event():
    """API для создания тестового события"""
    try:
        # Находим первого пользователя
        user = User.query.first()
        if not user:
            return jsonify({'status': 'error', 'message': 'Нет пользователей'}), 400
        
        # Находим первую категорию
        category = Category.query.filter_by(user_id=user.id).first()
        if not category:
            return jsonify({'status': 'error', 'message': 'Нет категорий'}), 400
        
        # Создаем событие
        now = datetime.utcnow()
        event = Event(
            user_id=user.id,
            category_id=category.id,
            start_time=now,
            end_time=now + timedelta(hours=2),
            type='plan'
        )
        db.session.add(event)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'Событие создано (ID: {event.id})'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500
