import os
import datetime
from random import randint
from flask import Flask, jsonify, request, json, redirect, url_for
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv  # Para leer el archivo .env
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import paypalrestsdk
from models import db, User, Product, Cart, CartItem, Order, OrderItem
from config import paypalrestsdk
load_dotenv()

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['SESSION_TYPE'] = 'filesystem' 
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

paypalrestsdk.configure({
    "mode": "sandbox",  # Cambia a "live" para producción
    "client_id": os.getenv("PAYPAL_CLIENT_ID"),
    "client_secret": os.getenv("PAYPAL_CLIENT_SECRET")
})

db.init_app(app)
jwt = JWTManager(app)
Migrate(app, db)
CORS(app)  # Se evita que se bloqueen las peticiones



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

    expires = datetime.timedelta(hours=72)
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
    address = user_data.get('address')

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
        name=name,
        address=address
    )

    user.save()
    if user:
        expires = datetime.timedelta(hours=72)
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

@app.route('/cart/add/<int:id>', methods=['POST'])
@jwt_required()
def add_to_cart(id):
    current_user_id = get_jwt_identity()
    product = Product.query.get(id)
    cart = Cart.query.filter_by(user_id=current_user_id).first()

    if not product:
        return jsonify({"msg": "Product not found"}), 404

    # Verificar si hay suficiente stock
    if product.stock_quantity < 1:
        return jsonify({"msg": "Not enough stock available"}), 400

    cart = Cart.query.filter_by(user_id=current_user_id).first()
    if not cart:
        cart = Cart(user_id=current_user_id)
        db.session.add(cart)
        db.session.commit()

    cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product.id).first()

    if cart_item:
        if cart_item.quantity >= product.stock_quantity:
            return jsonify({"msg": "Not enough stock available"}), 400
        cart_item.quantity += 1
    else:
        if 1 > product.stock_quantity:
            return jsonify({"msg": "Not enough stock available"}), 400
        cart_item = CartItem(cart_id=cart.id, product_id=product.id, quantity=1)
        db.session.add(cart_item)

    cart_items = CartItem.query.filter_by(cart_id=cart.id).all()
    serialized_items = [item.serialize() for item in cart_items]
    db.session.commit()

    return jsonify({"success": "Product added to cart successfully", "cart": serialized_items }), 201


@app.route('/cart', methods=['GET'])
@jwt_required()
def view_cart():
    current_user_id = get_jwt_identity()
    cart = Cart.query.filter_by(user_id=current_user_id).first()

    if not cart:
        return jsonify({"msg": "Cart is empty"}), 200

    cart_items = CartItem.query.filter_by(cart_id=cart.id).all()
    serialized_items = [item.serialize() for item in cart_items]

    return jsonify({"success": "Cart Obtained", "cart": serialized_items}), 200

@app.route('/cart/update', methods=['PUT'])
@jwt_required()
def update_cart_item():
    current_user_id = get_jwt_identity()
    product_id = request.json.get('product_id')
    quantity = request.json.get('quantity')

    if not product_id or quantity is None:
        return jsonify({"msg": "Product ID and quantity are required"}), 400

    cart = Cart.query.filter_by(user_id=current_user_id).first()
    if not cart:
        return jsonify({"msg": "Cart not found"}), 404

    cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()
    if not cart_item:
        return jsonify({"msg": "Product not found in cart"}), 404

    cart_item.quantity = quantity
    db.session.commit()

    return jsonify({"msg": "Cart updated successfully"}), 200



@app.route('/cart/remove/<int:id>', methods=['DELETE'])
@jwt_required()
def remove_cart_item(id):
    current_user_id = get_jwt_identity()
    product = Product.query.get(id)
    cart = Cart.query.filter_by(user_id=current_user_id).first()

    if not product:
        return jsonify({"msg": "Product not found"}), 404

    cart = Cart.query.filter_by(user_id=current_user_id).first()
    if not cart:
        return jsonify({"msg": "Cart not found"}), 404

    cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product.id).first()
    if not cart_item:
        return jsonify({"msg": "Product not found in cart"}), 404



    db.session.delete(cart_item)
    db.session.commit()

    cart_items = CartItem.query.filter_by(cart_id=cart.id).all()
    serialized_items = [item.serialize() for item in cart_items]
    return jsonify({"success": "Product removed from cart successfully", "cart": serialized_items}), 200



@app.route('/cart/clear', methods=['DELETE'])
@jwt_required()
def clear_cart():
    current_user_id = get_jwt_identity()
    cart = Cart.query.filter_by(user_id=current_user_id).first()

    if not cart:
        return jsonify({"msg": "Cart not found"}), 404

    CartItem.query.filter_by(cart_id=cart.id).delete()
    db.session.commit()

    return jsonify({"success": "Cart cleared successfully"}), 200

@app.route('/cart/item/<int:id>/decrement', methods=['POST'])
@jwt_required()
def decrement_item_quantity(id):
    current_user_id = get_jwt_identity()


    cart = Cart.query.filter_by(user_id=current_user_id).first()

    if not cart:
        return jsonify({"msg": "Cart not found"}), 404

    
    cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=id).first()

    if not cart_item:
        return jsonify({"msg": "CartItem not found"}), 404

    # Verificar que la cantidad actual sea mayor que 1
    if cart_item.quantity <= 1:
        return jsonify({"msg": "Item quantity cannot be less than 1"}), 400

    # Decrementar la cantidad del ítem
    cart_item.quantity -= 1
    
    cart_items = CartItem.query.filter_by(cart_id=cart.id).all()
    serialized_items = [item.serialize() for item in cart_items]
    db.session.commit()
    
    

    return jsonify({"success": "Item decremented", "cart": serialized_items}), 200


@app.route('/order', methods=['POST'])
@jwt_required()
def create_order():
    current_user_id = get_jwt_identity()
    cart = Cart.query.filter_by(user_id=current_user_id).first()

    if not cart:
        return jsonify({"msg": "Cart is empty"}), 400

    cart_items = CartItem.query.filter_by(cart_id=cart.id).all()
    if not cart_items:
        return jsonify({"msg": "No items in cart"}), 400

    total_price = sum(item.product.price * item.quantity for item in cart_items)

    order = Order(
        user_id=current_user_id,
        total_price=total_price,
        status='Pending'
    )
    db.session.add(order)
    db.session.commit()

    for item in cart_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity
        )
        db.session.add(order_item)

        # Actualizar el stock del producto
        product = Product.query.get(item.product_id)
        product.stock_quantity -= item.quantity

    db.session.commit()

    # Limpiar el carrito después de crear la orden
    CartItem.query.filter_by(cart_id=cart.id).delete()
    db.session.commit()

    return jsonify({"success": "Order created successfully", "order": order.serialize()}), 201


@app.route('/order/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    current_user_id = get_jwt_identity()
    order = Order.query.filter_by(id=order_id, user_id=current_user_id).first()

    if not order:
        return jsonify({"msg": "Order not found"}), 404

    return jsonify({"order": order.serialize()}), 200








with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run()
