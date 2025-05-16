from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:pryhazosc@localhost/hotel"
app.config["SQLALCHEMY_ECHO"] = True
db = SQLAlchemy(app)

class User(db.Model):
    __table
    id = db.Column(db.Integer, primary_key=True, autoincriment=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    

@app.route("/users", methods=["POST"])
def create_user():
    data = request.json
    print("trying!")
    user = User(username=data["username"])
    db.session.add(user)
    db.session.commit()
    return jsonify({"id": user.id}), 201

@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({"username": user.username})

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run()