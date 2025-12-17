from app import create_app, db
from app.models import User, Category, Event, Template
from datetime import datetime, timedelta
import json

app = create_app()

with app.app_context():
    print("🧹 Очистка старых таблиц...")
    db.drop_all()
    
    print("🛠️ Создание таблиц...")
    db.create_all()
    
    print("👤 Создание тестового пользователя...")
    user = User(
        name="Прохоренко Софья",
        telegram_id="sofia_hope_007"
    )
    db.session.add(user)
    db.session.flush()  # Получаем ID без коммита
    
    print("🏷️ Создание категорий...")
    categories = [
        Category(name="Учеба", color="#FF6B6B", user_id=user.id),
        Category(name="Работа", color="#4ECDC4", user_id=user.id),
        Category(name="Спорт", color="#45B7D1", user_id=user.id),
        Category(name="Отдых", color="#96CEB4", user_id=user.id),
    ]
    db.session.add_all(categories)
    db.session.flush()
    
    print("📅 Создание событий (план/факт)...")
    now = datetime.utcnow()
    events = []
    
    for day in range(7):
        for hour in range(9, 18, 3):  # С 9:00 до 18:00
            start_time = now + timedelta(days=day, hours=hour)
            end_time = start_time + timedelta(hours=2)
            
            # План
            events.append(Event(
                user_id=user.id,
                category_id=categories[day % len(categories)].id,
                start_time=start_time,
                end_time=end_time,
                type="plan"
            ))
            
            # Факт
            fact_start = start_time + timedelta(minutes=15)
            fact_end = end_time - timedelta(minutes=10)
            events.append(Event(
                user_id=user.id,
                category_id=categories[day % len(categories)].id,
                start_time=fact_start,
                end_time=fact_end,
                type="fact"
            ))
    
    db.session.add_all(events)
    
    print("📋 Создание шаблона...")
    template_data = {
        "Понедельник": [
            {"category": "Учеба", "time": "09:00-11:00", "task": "Лекции по БД"},
            {"category": "Работа", "time": "14:00-18:00", "task": "Разработка API"}
        ],
        "Вторник": [
            {"category": "Спорт", "time": "19:00-20:00", "task": "Тренировка"}
        ]
    }
    
    template = Template(
        user_id=user.id,
        name="Мое учебное расписание",
        data=json.dumps(template_data, ensure_ascii=False)
    )
    db.session.add(template)
    
    # Фиксируем
    db.session.commit()
    
    print("✅ База данных успешно инициализирована!")
    print(f"   Создано: 1 пользователь, {len(categories)} категорий, {len(events)} событий, 1 шаблон")
