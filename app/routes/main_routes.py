from flask import Blueprint, render_template, jsonify
from app import db
from datetime import datetime

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Главная страница - работает без JavaScript"""
    try:
        from app.models import User
        user_count = User.query.count()
        db_status = "✅ Подключена"
    except:
        user_count = 0
        db_status = "❌ Ошибка"
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Time Tracker - База данных</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body style="padding: 20px; background: #f8f9fa;">
        <div class="container">
            <h1 class="mb-4">⏰ Time Tracker Database</h1>
            <div class="alert alert-success">
                <h4>✅ Сайт работает на Render!</h4>
                <p>Flask + PostgreSQL + SQLAlchemy</p>
            </div>
            
            <div class="row mb-4">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">Статус базы данных</div>
                        <div class="card-body">
                            <p><strong>Статус:</strong> {db_status}</p>
                            <p><strong>Пользователей:</strong> {user_count}</p>
                            <p><strong>Время сервера:</strong> {datetime.now().strftime('%H:%M:%S')}</p>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">Проверка API</div>
                        <div class="card-body">
                            <p>Проверьте эти ссылки:</p>
                            <ul>
                                <li><a href="/api/health" target="_blank">/api/health</a> - Проверка работы</li>
                                <li><a href="/api/test" target="_blank">/api/test</a> - Тестовый API</li>
                                <li><a href="/debug" target="_blank">/debug</a> - Отладка</li>
                            </ul>
                            <button onclick="location.reload()" class="btn btn-primary">Обновить страницу</button>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">Управление базой данных</div>
                <div class="card-body">
                    <h5>Создать тестовые данные:</h5>
                    <form action="/api/create-test" method="POST">
                        <button type="submit" class="btn btn-success">Создать тестового пользователя</button>
                    </form>
                    
                    <hr>
                    
                    <h5>Техническая информация:</h5>
                    <p><strong>Stack:</strong> Flask, PostgreSQL, SQLAlchemy</p>
                    <p><strong>Хостинг:</strong> Render.com</p>
                    <p><strong>Курсовая работа</strong> по дисциплине "Структура ПО и БД"</p>
                </div>
            </div>
            
            <footer class="mt-4 text-center text-muted">
                <p>База данных Time Tracker | {datetime.now().year}</p>
            </footer>
        </div>
    </body>
    </html>
    """

@bp.route('/debug')
def debug():
    """Отладочная информация"""
    import os
    return jsonify({
        'status': 'ok',
        'time': datetime.now().isoformat(),
        'cwd': os.getcwd(),
        'python': os.sys.version,
        'database_url': os.environ.get('DATABASE_URL', 'not set')[:50] + '...' if os.environ.get('DATABASE_URL') else 'not set'
    })

@bp.route('/api/health')
def health():
    """Проверка здоровья"""
    try:
        db.engine.execute('SELECT 1')
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e)
        }), 500

@bp.route('/api/test')
def test_api():
    """Тестовый API endpoint"""
    return jsonify({
        'message': 'API работает!',
        'endpoints': ['/api/health', '/debug', '/api/test', '/api/create-test'],
        'timestamp': datetime.now().isoformat()
    })

@bp.route('/api/create-test', methods=['POST'])
def create_test():
    """Создание тестового пользователя"""
    try:
        from app.models import User
        
        user = User(
            name=f'Тест {datetime.now().strftime("%H:%M:%S")}',
            telegram_id=str(int(datetime.now().timestamp()))
        )
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Пользователь создан! ID: {user.id}',
            'user': {'id': user.id, 'name': user.name}
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
