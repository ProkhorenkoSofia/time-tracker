from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    telegram_id = db.Column(db.String(100), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    categories = db.relationship('Category', backref='user', cascade='all, delete-orphan', lazy=True)
    events = db.relationship('Event', backref='user', cascade='all, delete-orphan', lazy=True)
    templates = db.relationship('Template', backref='user', cascade='all, delete-orphan', lazy=True)
    
    def __repr__(self):
        return f'<User {self.name}>'

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(7), default='#007bff')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    events = db.relationship('Event', backref='category', cascade='all, delete-orphan', lazy=True)
    
    def __repr__(self):
        return f'<Category {self.name}>'

class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    type = db.Column(db.String(10), nullable=False)  # "plan" или "fact"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.Index('idx_event_user', 'user_id'),
        db.Index('idx_event_time', 'start_time'),
        db.Index('idx_event_type', 'type'))
    
    def __repr__(self):
        return f'<Event {self.type} {self.start_time}>'

class Template(db.Model):
    __tablename__ = 'templates'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    data = db.Column(db.JSON)  # JSON-структура расписания
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Template {self.name}>'
