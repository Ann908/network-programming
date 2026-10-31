from flask import Flask, jsonify, abort, request, abort, make_response
from flask_httpauth import HTTPBasicAuth
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import inspect

app = Flask(__name__)
auth = HTTPBasicAuth()

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return self.username

class Products(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    cost  = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Integer, nullable=False)
    color = db.Column(db.String(200), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'cost': self.cost,
            'weight': self.weight,
            'color': self.color
        }

def initialized_db():
    with app.app_context():
        #Initial entries add just at first time, when was created the table
        first_run = not inspect(db.engine).has_table('products')
        db.create_all()

        if first_run:
            initials_users = {
                'Nick': 'python',
                'Tom': 'night',
                'John': 'king'
            }

            for username, password in initials_users.items():
                existing_user = db.session.execute(db.select(User).filter_by(username=username)).scalar_one_or_none()
                if existing_user is None:
                    db.session.add(User(username=username, password=generate_password_hash(password)))

        initials_products = [
            {
                'id': 1,
                'cost': 100,
                'weight': 70,
                'color': u'blue'
            },
            {
                'id': 2,
                'cost': 200,
                'weight': 90,
                'color': u'green'
            },
            {
                'id': 3,
                'cost': 50,
                'weight': 30,
                'color': u'black'
            }
        ]
        for data in initials_products:
            if db.session.get(Products, data['id']) is None:
                db.session.add(Products(**data))

        db.session.commit()

@auth.verify_password
def verify_password(username, password):
    user = db.session.execute(db.select(User).filter_by(username=username)).scalar_one_or_none()
    if user is not None and check_password_hash(user.password, password):
        return user
    return None

@auth.error_handler
def unauthorized(status):
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)
    # return 403 instead of 401 to prevent browsers from displaying the default auth dialog

@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify( { 'error': 'Bad request' } ), 400)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

def get_product():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        abort(400)

    required = ('cost', 'weight', 'color')
    if any(field not in data for field in required):
        abort(400)
    elif type(data['cost']) is not int or data['cost'] < 0:
        abort(400)
    elif type(data['weight']) is not int or data['weight'] < 0:
        abort(400)
    elif not isinstance(data['color'], str) or not data['color'].strip():
        abort(400)
    return data

@app.route('/items', methods=['GET', 'POST', 'PUT', 'DELETE'])
@auth.login_required
def task_products():

    if request.method == 'GET':
        products = db.session.execute(
            db.select(Products).order_by(Products.id)
        ).scalars().all()
        return jsonify({'products': [p.to_dict() for p in products]})

    if request.method == 'POST':
        data = get_product()
        product = Products(
            cost=data['cost'],
            weight=data['weight'],
            color=data['color'].strip()
        )
        db.session.add(product)
        db.session.commit()
        return jsonify({'product': product.to_dict()}), 201

    #For PUT and DELETE id were received from JSON
    data = request.get_json(silent=True)

    if not isinstance(data, dict) or type(data.get('id')) is not int:
        abort(400)

    product = db.session.get(Products, data['id'])

    if product is None:
        abort(404)

    if request.method == 'PUT':
        data = get_product()
        product.cost = data['cost']
        product.weight = data['weight']
        product.color = data['color'].strip()

        db.session.commit()
        return jsonify({'product': product.to_dict()}), 200

    if request.method == 'DELETE':
        db.session.delete(product)
        db.session.commit()
        return jsonify({'message': 'Product deleted'}), 200

@app.route('/items/<int:product_id>', methods=['GET', 'PUT', 'DELETE'])
@auth.login_required
def get_products(product_id):
    product = db.session.get(Products, product_id)
    if product is None:
        abort(404)

    if request.method == 'GET':
        return jsonify({'product': product.to_dict()})

    if request.method == 'PUT':
        data = get_product()
        product.cost = data['cost']
        product.weight = data['weight']
        product.color = data['color'].strip()
        db.session.commit()
        return jsonify({'product':product.to_dict()})

    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product is deleted'})

if __name__ == '__main__':
    initialized_db()
    app.run(debug=True)


