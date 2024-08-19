This API provides a complete backend for an eCommerce application, including user authentication, product management, shopping cart operations, and order processing. It is built with Flask, uses SQLAlchemy for ORM, JWT for secure authentication, and integrates PayPal for payment processing.

Setup

    Install Dependencies:
    Ensure you have the necessary Python packages installed:

    bash

pip install flask flask_sqlalchemy flask_migrate flask_jwt_extended flask_cors python-dotenv werkzeug paypalrestsdk

Environment Variables:
Create a .env file in the root of your project with the following variables:

makefile

DATABASE_URI=your_database_uri
JWT_SECRET_KEY=your_jwt_secret_key
SECRET_KEY=your_secret_key


Database Migration:
Run the following commands to set up the database:

bash

flask db init
flask db migrate
flask db upgrade

Run the Application:
Start the Flask application with:

bash

python your_script_name.py