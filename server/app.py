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


@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

@app.route('/restaurants')
def restaurants():
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
    
@app.route('/restaurants/<int:id>')
def get_restaurants(id):
    restaurants = Restaurant.query.get_or_404(id)
    
    restaurant_dict = {
        'id': restaurants.id,
        'name': restaurants.name,
        'address': restaurants.address,
        'pizzas': [
            {
                'id': pizza.id,
                'name': pizza.name,
                'ingredients': pizza.ingredients,
                'price': restaurant_pizza.price
            }
            for restaurant_pizza in restaurants.restaurant_pizzas
            for pizza in Pizza.query.filter_by(id=restaurant_pizza.pizza_id)
        ]
    }

    return make_response(jsonify(restaurant_dict), 200)


if __name__ == '__main__':
    app.run(port=5555, debug=True)


class Restaurant(db.Model, SerializerMixin):
    __tablename__ = 'restaurants'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String)

    # add relationship
    restaurant_pizzas = db.relationship('RestaurantPizza', backref='restaurant', cascade="all, delete-orphan")

    # add serialization rules

    def __repr__(self):
        return f'<Restaurant {self.name}>'

