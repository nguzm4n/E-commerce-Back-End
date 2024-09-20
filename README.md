# E-commerce Backend Documentation
# Overview

### This project is a Flask-based backend for an e-commerce platform. It supports user authentication, product management, shopping cart, orders, and payments. The backend is built with Flask, uses SQLAlchemy for database interactions, and integrates with PayPal for payment processing.
Installation
Prerequisites

    Python 3.8+
    PostgreSQL
    Flask
    PayPal SDK

### Setup

    Clone the repository.

    Install dependencies:

    bash

pip install -r requirements.txt

Create a .env file with the following:

bash

DATABASE_URI=your_database_uri
JWT_SECRET_KEY=your_jwt_secret_key
PAYPAL_CLIENT_ID=your_paypal_client_id
PAYPAL_CLIENT_SECRET=your_paypal_client_secret

Initialize the database:

bash

flask db init
flask db migrate
flask db upgrade

Run the application:

bash

    flask run

### Endpoints
### Authentication

    POST /login
    Logs in the user, returning a JWT token.
        Request body: { email, password }
        Response: JWT token and user details.

    POST /signup
    Registers a new user.
        Request body: { username, email, password, name, address }
        Response: JWT token and user details.

### Products

    POST /additem
    Adds a new product.
        Request body: { name, description, price, avatar, stock_quantity, brand }
        Response: Product details.

    GET /getallguitars
    Retrieves all guitars.
        Response: List of serialized guitars.

    GET /getguitarid/{id}
    Retrieves a specific guitar by ID.
        Response: Guitar details.

### Shopping Cart

    POST /cart/add/{id}
    Adds a product to the user's cart.
        JWT required.
        Response: Updated cart.

    GET /cart
    Retrieves the user's current cart.
        JWT required.
        Response: Cart details.

    DELETE /cart/remove/{id}
    Removes a product from the cart.
        JWT required.
        Response: Updated cart.

    PUT /cart/update
    Updates the quantity of a product in the cart.
        JWT required.
        Request body: { product_id, quantity }
        Response: Success message.

### Orders

    POST /order
    Creates a new order from the user's cart.
        JWT required.
        Response: Order details.

    GET /order/{order_id}
    Retrieves a specific order.
        JWT required.
        Response: Order details.

    GET /userorders
    Retrieves all orders for the logged-in user.
        JWT required.
        Response: List of orders.

### Payment

    POST /payment
    Saves payment details for an order.
        JWT required.
        Request body: { order_id, paypal_transaction_id, payer_name, payment_time, amount, currency }
        Response: Payment details.

### Admin

    GET /admin/users
    Retrieves a list of all users. Requires admin privileges.
        JWT required.
        Response: List of users.

    DELETE /admin/order/{order_id}/{user_id}
    Deletes an order with 'Pending' or 'Frozen' status.
        JWT required.
        Response: Updated list of user orders.

### Models
### User

    id, username, email, password, name, address, phone_number, admin, active, created_at, updated_at

### Product

    id, name, description, price, avatar, stock_quantity, brand, created_at, updated_at

### Cart

    id, cart_id, user_id, created_at, updated_at

### CartItem

    id, cart_id, product_id, quantity

### Order

    id, order_id, user_id, total_price, status, created_at, updated_at

### OrderItem

    id, order_id, product_id, quantity

### PaymentDetails

    id, order_id, paypal_transaction_id, payer_name, payment_time, amount, currency, created_at

### Payment Integration

The backend integrates with PayPal to process payments. Use the sandbox mode for development.
