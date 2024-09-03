from flask_sqlalchemy import SQLAlchemy
import uuid
from sqlalchemy.dialects.postgresql import UUID
db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(20))
    created_at = db.Column(db.DateTime(), default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime(), default=db.func.current_timestamp(
    ), onupdate=db.func.current_timestamp())
    cart = db.relationship('Cart', backref='user', uselist=False, lazy=True)

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email
        }

    def save(self):
        db.session.add(self)
        db.session.commit()


class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    avatar = db.Column(db.String(255))
    stock_quantity = db.Column(db.Integer, nullable=False)
    brand = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(), default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime(), default=db.func.current_timestamp())


    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "avatar": self.avatar,
            "stock_quantity": self.stock_quantity

        }

    def save(self):
        db.session.add(self)
        db.session.commit()



class Cart(db.Model):
    __tablename__ = 'carts'
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(UUID(as_uuid=True), default=uuid.uuid4, nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime(), default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime(), default=db.func.current_timestamp())


    def serialize(self):
        return {
            "id": self.id,
            "cart_id": self.cart_id,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "product": self.product.serialize()
        }

    def save(self):
        db.session.add(self)
        db.session.commit()

class CartItem(db.Model):
    __tablename__ = 'cart_items'
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    product = db.relationship('Product', backref='cart_items')
       
    def serialize(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'product_name': self.product.name,
            'product_avatar': self.product.avatar,
            'price': self.product.price
            
            
        }
        

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(UUID(as_uuid=True), default=uuid.uuid4, nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_price = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='Pending')
    created_at = db.Column(db.DateTime(), default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime(), default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    user = db.relationship('User', backref='orders')
    items = db.relationship('OrderItem', backref='order', lazy=True)

    def serialize(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "user_id": self.user_id,
            "total_price": self.total_price,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "items": [item.serialize() for item in self.items]
        }

    def save(self):
        db.session.add(self)
        db.session.commit()


class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    product = db.relationship('Product', backref='order_items')

    def serialize(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "product_name": self.product.name,
            "product_avatar": self.product.avatar,
            "price": self.product.price
        }

    def save(self):
        db.session.add(self)
        db.session.commit()

class PaymentDetails(db.Model):
    __tablename__ = 'payment_details'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    paypal_transaction_id = db.Column(db.String(255), nullable=False, unique=True)
    payer_name = db.Column(db.String(255), nullable=False)
    payment_time = db.Column(db.DateTime(), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), nullable=False)  # USD, EUR, etc.
    created_at = db.Column(db.DateTime(), default=db.func.current_timestamp())

    order = db.relationship('Order', backref='payment_details')

    def serialize(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "paypal_transaction_id": self.paypal_transaction_id,
            "payer_name": self.payer_name,
            "payment_time": self.payment_time,
            "amount": self.amount,
            "currency": self.currency,
            "created_at": self.created_at
        }

    def save(self):
        db.session.add(self)
        db.session.commit()