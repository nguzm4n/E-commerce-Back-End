import os
import datetime
from random import randint
from flask import Flask, jsonify, request, json
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv  # Para leer el archivo .env
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

load_dotenv()

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

db.init_app(app)
jwt = JWTManager(app)
Migrate(app, db)
CORS(app)  # Se evita que se bloqueen las peticiones


@app.route('/token', methods=['GET'])
def token():
    data = {
        "access token": create_access_token(identity="test@email.com")
    }

    return jsonify(data), 200


@app.route('/login', methods=['POST'])
def login():

    password = request.json.get('password')
    email = request.json.get('email')

    print(request.json)
    if not email:
        return jsonify({"msg": "Email is required."}), 400
    if email == "":
        return jsonify({"msg": "Email is required."}), 400
    if not password:
        return jsonify({"msg": "Password is required."}), 400
    elif password == "":
        return jsonify({"msg": "Password is required."}), 400

    user_found = User.query.filter_by(email=email).first()

    if not user_found:
        return jsonify({"msg": "Email or password is not correct."}), 401

    if not check_password_hash(user_found.password, password):
        return jsonify({"msg": "Email or password is not correct."}), 401

    expires = datetime.timedelta(hours=10)
    access_token = create_access_token(
        identity=user_found.id, expires_delta=expires)
    datos = {
        "access_token": access_token,
        "user": user_found.serialize()
    }
    return jsonify(datos), 201


@app.route('/signup', methods=['POST'])
def sign_up():

    user_data = request.json
    if not user_data:
        return jsonify({"msg": "No JSON data received"}), 400

    username = user_data.get('username')
    password = user_data.get('password')
    email = user_data.get('email')
    name = user_data.get('name')

    if not username:
        return jsonify({"msg": "username is required"}), 400
    elif username == "":
        return jsonify({"msg": "username is required"}), 400
    elif not password:
        return jsonify({"msg": "password is required"}), 400
    elif password == "":
        return jsonify({"msg": "password is required"}), 400
    elif not email:
        return jsonify({"msg": "email is required"}), 400
    elif email == "":
        return jsonify({"msg": "email is required"}), 400
    elif not name:
        return jsonify({"msg": "name is required"}), 400
    elif name == "":
        return jsonify({"msg": "name is required"}), 400

    user_found = User.query.filter_by(email=email).first()
    if user_found:
        return jsonify({"msg": "Email is already in use"}), 400

    user_found = User.query.filter_by(username=username).first()
    if user_found:
        return jsonify({"msg": "Username is already in use"}), 400

    user = User(
        username=username,
        password=generate_password_hash(password),
        email=email,
        name=name
    )

    user.save()
    if user:
        expires = datetime.timedelta(hours=10)
        access_token = create_access_token(
            identity=user.id, expires_delta=expires)
        datos = {
            "access_token": access_token,
            "user": user.serialize()

        }
        return jsonify({"success": " Registration was Successful", "datos": datos}), 201


with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run()
