from app import app, db, Admin, Client, Room, Room_type, Booking


# with app.app_context():
#     admin = Admin(username='admin', password='admin123')  # В продакшене используйте сложный пароль!
#     db.session.add(admin)
#     db.session.commit()
#     print("Администратор создан")
name = input("Введите имя администратора: ")
password = input("Задайте пароль: ")
with app.app_context():
    db.drop_all()
    db.create_all()
    db.session.commit()
    # admin = Admin(username='admin', password='admin123')  # В продакшене используйте сложный пароль!
    # db.session.add(admin)
    # db.session.commit()
    print (len('scrypt:32768:8:1$TYRzuD3hWVcgerbE$7397809d0219c4c1edcf81ae8c82e2aafce7beb16942703948371c09cc2143cc967eceb77867408d1ad36489edd8cfe5de22b1c9e17999c1cd299142e6b22dfd'))
    new_admin = Admin(username=name)
    new_admin.password = password  # Здесь происходит хеширование
    db.session.add(new_admin)
    db.session.commit()
    print("Администратор создан")

    # Добавляем типы номеров
    room_types = [
        Room_type(type="Стандарт"),
        Room_type(type="Делюкс"),
        Room_type(type="Люкс"),
        Room_type(type="Президентский")
    ]
    db.session.add_all(room_types)
    db.session.commit()

    # Добавляем номера
    rooms = [
        Room(number="101", price=2500, capacity=2, room_type_id=1),
        Room(number="102", price=2500, capacity=2, room_type_id=1),
        Room(number="201", price=4000, capacity=2, room_type_id=2),
        Room(number="301", price=6500, capacity=3, room_type_id=3),
        Room(number="401", price=12000, capacity=4, room_type_id=4)
    ]
    db.session.add_all(rooms)
    db.session.commit()

    # Добавляем клиентов
    clients = [
        Client(name="Иванов Иван Иванович", phone="+79161234567", mail="ivanov@example.com", passport="1234567890"),
        Client(name="Петрова Мария Сергеевна", phone="+79031234567", mail="petrova@example.com", passport="0987654321"),
        Client(name="Сидоров Алексей Владимирович", phone="+79261234567", mail="sidorov@example.com", passport="4567890123")
    ]
    db.session.add_all(clients)
    db.session.commit()

    # Добавляем бронирования
    from datetime import datetime, timedelta
    bookings = [
        Booking(
            check_in=datetime.now().date(),
            check_out=(datetime.now() + timedelta(days=3)).date(),
            room_id=1,
            client_id=1
        ),
        Booking(
            check_in=datetime.now().date(),
            check_out=(datetime.now() + timedelta(days=5)).date(),
            room_id=3,
            client_id=2
        )
    ]
    db.session.add_all(bookings)
    db.session.commit()

    print("Тестовые данные успешно добавлены")