#!/usr/bin/env python3

from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.errorhandler(404)
def resource_not_found(e):
    return make_response(jsonify(error="Resource not found"), 404)

@app.errorhandler(400)
def bad_request(e):
    return make_response(jsonify(error="Bad request"), 400)

@app.errorhandler(500)
def internal_server_error(e):
    return make_response(jsonify(error="Internal server error"), 500)

@app.errorhandler(Exception)
def handle_exception(e):
    return make_response(jsonify(error=str(e)), 500)

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

@app.route('/restaurants', methods=['GET'])
def get_all_restaurants():
    restaurants = Restaurant.query.all()
    restaurants_list = []

    for restaurant in restaurants:
        restaurant_dict = {
            'id': restaurant.id,
            'name': restaurant.name,
            'address': restaurant.address
        }
        restaurants_list.append(restaurant_dict)

    return make_response(jsonify(restaurants_list), 200)
    
@app.route('/restaurants/<int:id>', methods=['GET','POST'])
def get_restaurants(id):
    restaurants = Restaurant.query.get_or_404(id)

    restaurant_dict = {
        'id': restaurants.id,
        'name': restaurants.name,
        'address': restaurants.address,
        'restaurant_pizzas': [
            {
                "id": rp.id,
                "pizza": {
                "id": rp.pizza.id,
                "name": rp.pizza.name,
                "ingredients": rp.pizza.ingredients
                },
                "pizza_id": rp.pizza_id,
                "price": rp.price,
                "restaurant_id": rp.restaurant_id
                } for rp in restaurants.restaurant_pizzas
            ]
        }

    return make_response(jsonify(restaurant_dict), 200)

@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)

    if not restaurant:
        return make_response(jsonify({"error": "Restaurant not found"}), 404)

    for restaurant_pizza in restaurant.restaurant_pizzas:
        db.session.delete(restaurant_pizza)

    db.session.delete(restaurant)
    db.session.commit()

    return make_response('', 204)


@app.route('/pizzas', methods=['GET'])
def pizzas():
    pizzas = Pizza.query.all()
    pizzas_list = []

    for pizza in pizzas:
        pizza_dict = {
            'id': pizza.id,
            'name': pizza.name,
            'ingredients': pizza.ingredients
        }
        pizzas_list.append(pizza_dict)

    return make_response(jsonify(pizzas_list), 200)

@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    data = request.get_json()
    
    if 'pizza_id' not in data or 'restaurant_id' not in data or 'price' not in data:
        return make_response(jsonify({"errors": ["Missing data"]}), 400)

    pizza = Pizza.query.get(data['pizza_id'])
    restaurant = Restaurant.query.get(data['restaurant_id'])

    if not pizza or not restaurant:
        return make_response(jsonify({"errors": ["Invalid pizza_id or restaurant_id"]}), 400)

    try:
        new_restaurant_pizza = RestaurantPizza(
            pizza_id=data['pizza_id'],
            restaurant_id=data['restaurant_id'],
            price=data['price']
        )
        db.session.add(new_restaurant_pizza)
        db.session.commit()
        return make_response(jsonify(new_restaurant_pizza.to_dict()), 201)
    except Exception as e:
        return make_response(jsonify({"errors": [str(e)]}), 400)


if __name__ == '__main__':
    app.run(port=5555, debug=True)