from app import app, db, Admin, Client, Room, Room_type, Booking
name = input("Введите имя новго администратора: ")
password = input("Задайте пароль: ")
with app.app_context():
    new_admin = Admin(username=name)
    new_admin.password = password  # Здесь происходит хеширование
    db.session.add(new_admin)
    db.session.commit()
    print("Администратор добавлен")