from app import app, db, Admin

with app.app_context():
    admin = Admin(username='admin', password='admin123')  # В продакшене используйте сложный пароль!
    db.session.add(admin)
    db.session.commit()
    print("Администратор создан")