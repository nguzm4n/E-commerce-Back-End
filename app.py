import os
import datetime
from random import randint
from flask import Flask, jsonify, request, json
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv  # Para leer el archivo .env
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Product

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


@app.route('/additem', methods=['POST'])
def add_item():
    item_data = request.json
    if not item_data:
        return jsonify({"msg": "No JSON data received"}), 400

    item_name = item_data.get('name')
    item_description = item_data.get('description')
    item_price = item_data.get('price')
    item_avatar = item_data.get('avatar')
    item_stock = item_data.get('stock_quantity')
    item_brand = item_data.get('brand')

    if not item_name:
        return jsonify({"msg": "item_name is required"}), 400
    elif item_name == "":
        return jsonify({"msg": "item_name is required"}), 400
    if not item_description:
        return jsonify({"msg": "item_description is required"}), 400
    elif item_description == "":
        return jsonify({"msg": "item_description is required"}), 400
    if not item_price:
        return jsonify({"msg": "item_price is required"}), 400
    elif item_price == "":
        return jsonify({"msg": "item_price is required"}), 400
    if not item_avatar:
        return jsonify({"msg": "item_avatar is required"}), 400
    elif item_avatar == "":
        return jsonify({"msg": "item_avatar is required"}), 400
    if not item_stock:
        return jsonify({"msg": "item_stock is required"}), 400
    elif item_stock == "":
        return jsonify({"msg": "item_stock is required"}), 400
    if not item_brand:
        return jsonify({"msg": "item_brand is required"}), 400
    elif item_brand == "":
        return jsonify({"msg": "item_brand is required"}), 400

    product = Product(
        name=item_name,
        description=item_description,
        price=item_price,
        avatar=item_avatar,
        stock_quantity=item_stock,
        brand=item_brand

    )

    product.save()

    if product:
        datos = {
            "product": product.serialize()
        }

    return jsonify({"success": "Item added successfully", "datos": datos}), 201


@app.route('/getprs', methods=['GET'])
def get_prs():
    prs_guitars = Product.query.filter_by(brand='prs').all()
    serialized_guitars = [guitar.serialize() for guitar in prs_guitars]

    return jsonify({"success": "PRS guitars gathered successfully", "guitars": serialized_guitars}), 200


@app.route('/getchapman', methods=['GET'])
def get_chapman():
    chapman_guitars = Product.query.filter_by(brand='chapman').all()
    serialized_guitars = [guitar.serialize() for guitar in chapman_guitars]

    return jsonify({"success": "Chapman guitars gathered successfully", "guitars": serialized_guitars}), 200


@app.route('/getsolar', methods=['GET'])
def get_solar():
    solar_guitars = Product.query.filter_by(brand='solar').all()
    serialized_guitars = [guitar.serialize() for guitar in solar_guitars]

    return jsonify({"success": "Solar guitars gathered successfully", "guitars": serialized_guitars}), 200


@app.route('/getguitarid/<int:id>', methods=['GET'])
def get_guitar_id(id):
    guitar_id = Product.query.get(id)
    if not guitar_id:
        return jsonify({"msg": "Guitar Not Found"}), 404
    return jsonify(guitar_id.serialize()), 200

@app.route('/getallguitars', methods=['GET'])
def get_all_guitars():
    all_guitars = Product.query.all()
    all_guitars = list(map(lambda guitar: guitar.serialize(), all_guitars))
    return jsonify(all_guitars), 200




with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run()
