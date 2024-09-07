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
from models import db, User, Product, Cart, CartItem, Order, OrderItem, PaymentDetails
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
    "mode": "sandbox",  
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
    elif not address:
        return jsonify({"msg": "address is required"}), 400
    elif address == "":
        return jsonify({"msg": "address is required"}), 400
    

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


@app.route('/getstrat', methods=['GET'])
def get_prs():
    stratocaster_guitars = Product.query.filter_by(brand='stratocaster').all()
    serialized_guitars = [guitar.serialize() for guitar in stratocaster_guitars]

    return jsonify({"success": "PRS guitars gathered successfully", "guitars": serialized_guitars}), 200


@app.route('/gettelecaster', methods=['GET'])
def get_chapman():
    telecaster_guitars = Product.query.filter_by(brand='telecaster').all()
    serialized_guitars = [guitar.serialize() for guitar in telecaster_guitars]

    return jsonify({"success": "Chapman guitars gathered successfully", "guitars": serialized_guitars}), 200


@app.route('/getsg', methods=['GET'])
def get_solar():
    sg_guitars = Product.query.filter_by(brand='sg').all()
    serialized_guitars = [guitar.serialize() for guitar in sg_guitars]

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
        cart = Cart(user_id=current_user_id)
        db.session.add(cart)
        db.session.commit()
        return jsonify({"msg": "Cart created, and is empty"}), 201

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
    
        # Verificar si el usuario ya tiene una orden pendiente
    existing_order = Order.query.filter_by(user_id=current_user_id, status='Pending').first()
    if existing_order:
        return jsonify({"msg": "You already have a pending order"}), 400
    # Verificar orden Frozen
    Frozen_order = Order.query.filter_by(user_id=current_user_id, status='Frozen').first()
    if Frozen_order:
        return jsonify({"msg": "You haven a Frozen Order, Please Contact Support"}), 400
    #Obtener carrito del usuario
    cart = Cart.query.filter_by(user_id=current_user_id).first()

    frozen_order = Order.query.filter_by(user_id=current_user_id, status='Frozen').first()
    
    if frozen_order:
        return jsonify({"msg": "You have an incomplete order, please contact support to fix this situation"})
    
    
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



@app.route('/userorders', methods=['GET'])
@jwt_required()
def get_all_orders():
    current_user_id = get_jwt_identity()
    orders = Order.query.filter_by(user_id=current_user_id).all()

    if not orders:
        return jsonify({"msg": "User has no orders"}), 404

    # Serializar cada orden en la lista de órdenes
    serialized_orders = [order.serialize() for order in orders]

    return jsonify({"orders": serialized_orders}), 200



@app.route('/search', methods=['POST'])
def search_item():
    search_term = request.json.get('search_term')

    if not search_term:
        return jsonify({"msg": "Search term is required"}), 400
    
    # Hacer una búsqueda en los campos que quieras, por ejemplo, nombre y descripción del producto
    search_results = Product.query.filter(
        (Product.brand.ilike(f"%{search_term}%")) | 
        (Product.description.ilike(f"%{search_term}%"))
    ).all()

    if not search_results:
        return jsonify({"msg": "No items found"}), 404
    
    serialized_results = [product.serialize() for product in search_results]

    return jsonify({"success": "Items found", "guitars": serialized_results}), 200

@app.route('/payment', methods=['POST'])
@jwt_required()
def save_payment_details():
    data = request.get_json()

    # Extraer los datos necesarios de la solicitud
    order_id = data.get('order_id')
    paypal_transaction_id = data.get('paypal_transaction_id')
    payer_name = data.get('payer_name')
    payment_time = data.get('payment_time')
    amount = data.get('amount')
    currency = data.get('currency')

    # Verificar si la orden existe
    order = Order.query.filter_by(id=order_id).first()
    if not order:
        return jsonify({"msg": "Order not found"}), 404

    # Crear una nueva instancia de PaymentDetails
    payment_details = PaymentDetails(
        order_id=order_id,
        paypal_transaction_id=paypal_transaction_id,
        payer_name=payer_name,
        payment_time=payment_time,
        amount=amount,
        currency=currency
    )

    try:
        # Guardar la información del pago en la base de datos
        payment_details.save()
        return jsonify({"msg": "Payment details saved successfully", "payment": payment_details.serialize()}), 201
    except Exception as e:
        # Manejar errores como la violación de la unicidad de paypal_transaction_id
        return jsonify({"msg": f"Error saving payment details: {str(e)}"}), 400



@app.route('/order/<int:order_id>/status', methods=['PATCH'])
@jwt_required()
def update_order_status(order_id):
    current_user_id = get_jwt_identity()
    order = Order.query.filter_by(id=order_id, user_id=current_user_id).first()

    if not order:
        return jsonify({"msg": "Order not found"}), 404

    data = request.get_json()
    new_status = data.get('status')

    if new_status not in ["Paid", "Frozen"]:
        return jsonify({"msg": "Invalid status"}), 400

    order.status = new_status

    try:
        db.session.commit()
        return jsonify({"msg": f"Order status updated to {new_status}"}), 200
    except Exception as e:
        return jsonify({"msg": f"Error updating order status: {str(e)}"}), 400


@app.route('/admin/user_orders/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_orders(user_id):
    # Verificar si el usuario actual es administrador
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user or not current_user.admin:
        return jsonify({"msg": "Admin privileges required"}), 403

    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    
    orders = Order.query.filter_by(user_id=user.id).all()

    if not orders:
        return jsonify({"msg": "No orders found for this user"}), 404

    
    serialized_orders = [order.serialize() for order in orders]
    return jsonify({"orders": serialized_orders}), 200


@app.route('/delete/order/<int:order_id>', methods=['DELETE'])
@jwt_required()
def delete_order(order_id):
    current_user_id = get_jwt_identity()

    try:
        # Obtener la orden a eliminar
        order = Order.query.filter_by(user_id=current_user_id, id=order_id).first()
        
        # Verificar el estado de la orden
        if order.status == "Paid":
            return jsonify({"msg": "You cannot delete a Paid order"}), 403
        if order.status == "Frozen":
            return jsonify({"msg": "You cannot delete a Frozen order"}), 403
        
        if not order:
            return jsonify({"msg": "Order not found"}), 404

        # Eliminar los detalles de pago asociados
        payment_details = PaymentDetails.query.filter_by(order_id=order_id).first()
        if payment_details:
            db.session.delete(payment_details)

        # Eliminar los items asociados
        for item in order.items:
            # Actualizar el stock de productos
            product = Product.query.get(item.product_id)
            if product:
                product.stock_quantity += item.quantity
                db.session.commit()

            # Eliminar el item del carrito
            db.session.delete(item)
        # Eliminar la orden
        db.session.delete(order)
        db.session.commit()
        
        orders = Order.query.filter_by(user_id=current_user_id).all()
        serialized_orders = [order.serialize() for order in orders]
   
        return jsonify({"success": "Order deleted successfully", "orders": serialized_orders }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": str(e)}), 500


## Admin Actions
@app.route('/admin/users', methods=['GET'])
@jwt_required()
def get_all_users():
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user or not current_user.admin:
        return jsonify({"msg": "Admin privileges required"}), 403

    users = User.query.all()
    if not users:
        return jsonify({"msg": "No users found"}), 404

    serialized_users = [user.serialize() for user in users]
    return jsonify({"users": serialized_users}), 200

@app.route('/admin/search_user', methods=['POST'])
@jwt_required()
def search_user():
    # Verificar si el usuario actual es administrador
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user or not current_user.admin:
        return jsonify({"msg": "Admin privileges required"}), 403
    
    search_term = request.json.get('search_term', '')

    if not search_term:
        return jsonify({"msg": "Search term is required"}), 400

    # Buscar usuarios por nombre o email
    users = User.query.filter(
        (User.name.ilike(f"%{search_term}%")) | 
        (User.email.ilike(f"%{search_term}%"))
    ).all()

    if not users:
        return jsonify({"msg": "No users found"}), 404
    
    serialized_users = [user.serialize() for user in users]
    return jsonify({"users": serialized_users}), 200


@app.route('/admin/order/<int:order_id>/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_order_by_status(order_id, user_id):
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user or not current_user.admin:
        return jsonify({"msg": "Admin privileges required"}), 403
    
    
    order = Order.query.get(order_id)
    if not order:
        return jsonify({"msg": "Order not found"}), 404
    
    payment_details = PaymentDetails.query.filter_by(order_id=order_id).first()
    if payment_details:
        db.session.delete(payment_details)
    
    if order.status not in ['Pending', 'Frozen']:
        return jsonify({"msg": "Only orders with 'Pending' or 'Frozen' status can be deleted"}), 400
    
   
    OrderItem.query.filter_by(order_id=order.id).delete()
    db.session.delete(order)
    db.session.commit()
    
    orders = Order.query.filter_by(user_id=user_id).all()
    serialized_orders = [order.serialize() for order in orders]
    return jsonify({"msg": "Order deleted successfully", "orders": serialized_orders}), 200




with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run()
