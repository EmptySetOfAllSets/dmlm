
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, and_, not_, cast, String, func, Integer  # Основные функции
from sqlalchemy.exc import IntegrityError  # Для обработки ошибок БД
from flask_login import LoginManager, UserMixin
from app import db

# db = SQLAlchemy(app)


class Room_type(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)
    rooms = db.relationship('Room', backref='room_type', lazy=True)

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(10), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    room_type_id = db.Column(db.Integer, db.ForeignKey('room_type.id'), nullable=False)
    bookings = db.relationship('Booking', backref='room', lazy=True)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    check_in = db.Column(db.Date)
    check_out = db.Column(db.Date)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)

class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(100))

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mail = db.Column(db.String(100), unique=False, nullable=True)
    phone = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(500), nullable=False)
    passport = db.Column(db.String(500), nullable=False)
    bookings = db.relationship('Booking', backref='client', lazy=True)