from flask import Flask, render_template, request, redirect, url_for, flash
import os
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, current_user, login_user
from datetime import datetime
from sqlalchemy import or_, and_, not_, cast, String, func, Integer  # Основные функции
from sqlalchemy.exc import IntegrityError  # Для обработки ошибок БД
from flask import session  # Добавьте в импорты

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:pryhazosc@localhost/hotel'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'ваш_секретный_ключ'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'admin_login'

# Модели БД
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

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))



@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        admin = Admin.query.filter_by(username=username).first()
        
        if admin and admin.password == password:  # В реальном приложении используйте хеширование!
            login_user(admin)
            return redirect(url_for('admin_dashboard'))
        flash('Неверные учетные данные', 'error')
    return render_template('admin/login.html')

@app.route('/admin')
@login_required
def admin_dashboard():
    rooms = Room.query.all()
    today = datetime.now().date()
    #bookings = Booking.query.order_by(Booking.id).all()
    bookings = Booking.query.filter(Booking.check_out >= today)\
                          .order_by(Booking.check_in.asc())\
                          .all()
    clients = Client.query.all()
    room_types = Room_type.query.all()
    past_bookings_count = Booking.query.filter(Booking.check_out < today).count()

    return render_template('admin/dashboard.html', 
                        rooms=rooms,
                        bookings=bookings, clients= clients, room_types =room_types,
                        today = today,
                        past_bookings_count = past_bookings_count)

@app.route('/admin/archive')
@login_required
def booking_archive():
    search_query = request.args.get('search', '').strip()
    today = datetime.now().date()
    
    # Базовый запрос для архивных бронирований
    bookings_query = Booking.query.filter(Booking.check_out < today)\
                                .join(Room)\
                                .join(Client)
    
    # Применяем поиск если есть запрос
    if search_query:
        bookings_query = bookings_query.filter(
            or_(
                Room.number.ilike(f'%{search_query}%'),
                Room_type.type.ilike(f'%{search_query}%'),
                Client.name.ilike(f'%{search_query}%'),
                Client.phone.ilike(f'%{search_query}%'),
                cast(Booking.id, String).ilike(f'%{search_query}%')
            )
        )
    
    bookings = bookings_query.order_by(Booking.check_out.desc()).all()
    
    return render_template('admin/archive.html',
                         bookings=bookings,
                         search_query=search_query,
                         today=today)

# Маршруты для работы с типами номеров
@app.route('/admin/room_type/add', methods=['POST'])
@login_required
def add_room_type():
    new_type = Room_type(
        type=request.form.get('type')
    )
    db.session.add(new_type)
    db.session.commit()
    flash('Тип номера успешно добавлен', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/room_type/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_room_type(id):
    room_type = Room_type.query.get_or_404(id)
    if request.method == 'POST':
        room_type.type = request.form.get('type')
        db.session.commit()
        flash('Тип номера обновлен', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/edit_room_type.html', room_type=room_type)

@app.route('/admin/room_type/delete/<int:id>')
@login_required
def delete_room_type(id):
    room_type = Room_type.query.get_or_404(id)
    db.session.delete(room_type)
    db.session.commit()
    flash('Тип номера удален', 'success')
    return redirect(url_for('admin_dashboard'))

# Маршруты для работы с номерами
@app.route('/admin/room/add', methods=['POST'])
@login_required
def add_room():
    new_room = Room(
        number=request.form.get('number'),
        type=request.form.get('type'),
        price=float(request.form.get('price')),
        capacity=int(request.form.get('capacity')),
        room_type_id=int(request.form.get('room_type_id'))
    )
    db.session.add(new_room)
    db.session.commit()
    flash('Номер успешно добавлен', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/booking/add', methods=['GET', 'POST'])
@login_required
def add_booking():
    if request.method == 'POST':
        try:
            new_booking = Booking(
                room_id=int(request.form['room_id']),
                client_id=int(request.form['client_id']),
                check_in=datetime.strptime(request.form['check_in'], '%Y-%m-%d').date(),
                check_out=datetime.strptime(request.form['check_out'], '%Y-%m-%d').date()
            )
            db.session.add(new_booking)
            db.session.commit()
            flash('Бронирование успешно добавлено', 'success')
            return redirect(url_for('admin_dashboard'))
        except ValueError as e:
            db.session.rollback()
            flash(f'Ошибка в данных: {str(e)}', 'error')
    
    # Получаем списки для выпадающих меню
    rooms = Room.query.order_by(Room.number).all()
    clients = Client.query.order_by(Client.name).all()
    
    return render_template('admin/add_booking.html',
                         rooms=rooms,
                         clients=clients,
                         today=datetime.now().date())

@app.route('/admin/room/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_room(id):
    room = Room.query.get_or_404(id)
    room_types = Room_type.query.all()
    
    if request.method == 'POST':
        new_number = request.form['number'].strip()
        
        # Проверяем уникальность номера
        if new_number != room.number:  # Если номер изменили
            existing_room = Room.query.filter_by(number=new_number).first()
            if existing_room:
                flash('Номер комнаты уже существует!', 'error')
                return render_template('admin/edit_room.html',
                                     room=room,
                                     room_types=room_types)
        
        # Обновляем данные
        room.number = new_number
        room.room_type_id = int(request.form['room_type_id'])
        room.price = float(request.form['price'])
        room.capacity = int(request.form['capacity'])
        
        # Обновляем название типа из связанной таблицы
        selected_type = Room_type.query.get(room.room_type_id)
        room.type = selected_type.type
        
        try:
            db.session.commit()
            flash('Номер успешно обновлен', 'success')
            return redirect(url_for('admin_dashboard'))
        except IntegrityError:
            db.session.rollback()
            flash('Произошла ошибка при сохранении', 'error')
    
    return render_template('admin/edit_room.html',
                         room=room,
                         room_types=room_types)

@app.route('/admin/room/delete/<int:id>')
@login_required
def delete_room(id):
    room = Room.query.get_or_404(id)
    db.session.delete(room)
    db.session.commit()
    flash('Номер удален', 'success')
    return redirect(url_for('admin_dashboard'))

# Маршруты для работы с клиентами
@app.route('/admin/client/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_client(id):
    client = Client.query.get_or_404(id)
    if request.method == 'POST':
        client.name = request.form.get('name')
        client.phone = request.form.get('phone')
        client.mail = request.form.get('mail')
        client.passport = request.form.get('passport')
        db.session.commit()
        flash('Данные клиента обновлены', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/edit_client.html', client=client)

@app.route('/admin/client/delete/<int:id>')
@login_required
def delete_client(id):
    client = Client.query.get_or_404(id)
    db.session.delete(client)
    db.session.commit()
    flash('Клиент удален', 'success')
    return redirect(url_for('admin_dashboard'))

# Маршруты для бронирований (только просмотр и удаление)
@app.route('/admin/booking/delete/<int:id>')
@login_required
def delete_booking(id):
    booking = Booking.query.get_or_404(id)
    db.session.delete(booking)
    db.session.commit()
    flash('Бронирование удалено', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/booking/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_booking(id):
    booking = Booking.query.get_or_404(id)
    rooms = Room.query.order_by(Room.number).all()
    clients = Client.query.order_by(Client.name).all()

    if request.method == 'POST':
        try:
            # Проверяем, изменились ли даты или номер
            new_room_id = int(request.form['room_id'])
            new_check_in = datetime.strptime(request.form['check_in'], '%Y-%m-%d').date()
            new_check_out = datetime.strptime(request.form['check_out'], '%Y-%m-%d').date()

            # Проверка доступности номера (исключая текущее бронирование)
            if (new_room_id != booking.room_id or 
                new_check_in != booking.check_in or 
                new_check_out != booking.check_out):
                
                overlapping = Booking.query.filter(
                    Booking.id != id,
                    Booking.room_id == new_room_id,
                    Booking.check_out > new_check_in,
                    Booking.check_in < new_check_out
                ).first()

                if overlapping:
                    flash('Номер уже занят в выбранные даты другим бронированием', 'error')
                    return redirect(url_for('edit_booking', id=id))

            # Обновляем данные
            booking.room_id = new_room_id
            booking.client_id = int(request.form['client_id'])
            booking.check_in = new_check_in
            booking.check_out = new_check_out

            db.session.commit()
            flash('Бронирование успешно обновлено', 'success')
            return redirect(url_for('admin_dashboard'))

        except ValueError as e:
            db.session.rollback()
            flash(f'Ошибка в данных: {str(e)}', 'error')

    return render_template('admin/edit_booking.html',
                         booking=booking,
                         rooms=rooms,
                         clients=clients,
                         today=datetime.now().date())


@app.route('/booking', methods=['GET', 'POST'])
def booking_start():
    if request.method == 'POST':
        # Сохраняем выбор пользователя (новый/существующий клиент)
        session['is_returning_client'] = request.form.get('client_type') == 'returning'
        return redirect(url_for('client_info'))
    
    return render_template('booking/step1_client_type.html')

# Маршрут для ввода информации о клиенте
@app.route('/booking/client-info', methods=['GET', 'POST'])
def client_info():
    if not session.get('is_returning_client') is not None:
        return redirect(url_for('booking_start'))
    
    if request.method == 'POST':
        if session['is_returning_client']:
            # Поиск существующего клиента
            search_query = request.form.get('search')
            clients = Client.query.filter(
                or_(
                    Client.name.ilike(f'%{search_query}%'),
                    Client.phone.ilike(f'%{search_query}%'),
                    Client.passport.ilike(f'%{search_query}%')
                )
            ).all()
            return render_template('booking/step2a_client_search.html', clients=clients)
        else:
            # Создание нового клиента
            new_client = Client(
                name=request.form.get('name'),
                phone=request.form.get('phone'),
                mail=request.form.get('email'),
                passport=request.form.get('passport')
            )
            db.session.add(new_client)
            db.session.commit()
            session['client_id'] = new_client.id
            return redirect(url_for('room_selection'))
    
    if session['is_returning_client']:
        return render_template('booking/step2a_client_search.html', clients=None)
    else:
        return render_template('booking/step2b_client_registration.html')

# Маршрут для выбора клиента из результатов поиска
@app.route('/booking/select-client/<int:client_id>')
def select_client(client_id):
    session['client_id'] = client_id
    return redirect(url_for('room_selection'))

# Маршрут для выбора номера
@app.route('/booking/select-room', methods=['GET', 'POST'])
def room_selection():
    if 'client_id' not in session:
        return redirect(url_for('booking_start'))
    
    if request.method == 'POST':
        # Сохраняем выбранные даты
        session['check_in'] = request.form.get('check_in')
        session['check_out'] = request.form.get('check_out')
    
    # Получаем доступные номера
    check_in = datetime.strptime(session.get('check_in'), '%Y-%m-%d').date() if session.get('check_in') else None
    check_out = datetime.strptime(session.get('check_out'), '%Y-%m-%d').date() if session.get('check_out') else None
    
    available_rooms = []
    if check_in and check_out:
        # Запрос для поиска свободных номеров
        booked_rooms = db.session.query(Booking.room_id).filter(
            Booking.check_out > check_in,
            Booking.check_in < check_out
        ).subquery()
        
        available_rooms = Room.query.filter(
            ~Room.id.in_(booked_rooms)
        ).all()
    
    return render_template('booking/step3_room_selection.html',
                         available_rooms=available_rooms,
                         check_in=session.get('check_in'),
                         check_out=session.get('check_out'))

# Маршрут для подтверждения бронирования
@app.route('/booking/confirm/<int:room_id>')
def confirm_booking(room_id):
    if 'client_id' not in session or not session.get('check_in') or not session.get('check_out'):
        return redirect(url_for('booking_start'))
    
    # Создаем бронирование
    new_booking = Booking(
        room_id=room_id,
        client_id=session['client_id'],
        check_in=datetime.strptime(session['check_in'], '%Y-%m-%d').date(),
        check_out=datetime.strptime(session['check_out'], '%Y-%m-%d').date()
    )
    
    db.session.add(new_booking)
    db.session.commit()
    
    # Очищаем сессию
    for key in ['is_returning_client', 'client_id', 'check_in', 'check_out']:
        session.pop(key, None)
    
    return render_template('booking/step4_confirmation.html', booking=new_booking)

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/booking/confirm')
def booking_confirm():
    if 'booking_data' not in session:
        return redirect(url_for('booking'))
    
    # Создаем бронирование
    booking = Booking(
        client_name=session['booking_data']['full_name'],
        client_passport=session['booking_data']['passport'],
        client_email=session['booking_data']['email'],
        client_phone=session['booking_data']['phone'],
        room_id=1,  # Здесь нужно добавить выбор номера
        check_in=datetime.now().date(),
        check_out=datetime.now().date() + timedelta(days=3)
    )
    
    db.session.add(booking)
    db.session.commit()
    
    booking_data = session.pop('booking_data', None)
    
    return render_template('booking/step3_confirm.html',
                         title='Подтверждение бронирования',
                         booking=booking_data)

# Главная страница
@app.route('/')
def index():
    return render_template('index.html', title='Главная')

# Страница "О нас"
@app.route('/about')
def about():
    return render_template('about.html', title='О нас')

@app.route('/gallery')
def gallery():
    images = os.listdir(os.path.join(app.static_folder, 'images','rooms'))
    context = {}
    context["images"] = []
    context["descriptions"] = []
    print(images)
    descriptions = [
        "test 1",
        "description",
        "description2",
        "description3",
        "description4",
        "description5",
        "description6",
        "description7",
        "description8"
    ]
    #images_with_descriptions = list(zip(images, descriptions))

    context = [
            {'image': f'images/rooms/{img}', 'description': desc} 
            for img, desc in zip(images, descriptions)
        ]
    
    return render_template('gallery.html', title='Галерея', context=context)

# API-эндпоинт
@app.route('/api/data')
def api_data():
    return {'data': [1, 2, 3, 4, 5]}

# Запуск приложения
if __name__ == '__main__':
    app.run(debug=True)