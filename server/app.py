#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from sqlalchemy.exc import IntegrityError
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)




class RestaurantList(Resource):
    def get(self):
        """GET /restaurants"""
        restaurants = Restaurant.query.all()
        data = [r.to_dict(only=('id', 'name', 'address')) for r in restaurants]
        return data, 200


class RestaurantDetail(Resource):
    def get(self, id):
        """GET /restaurants/<int:id>"""
        restaurant = Restaurant.query.filter_by(id=id).first()
        
        if not restaurant:
            return {'error': 'Restaurant not found'}, 404
        
        result = restaurant.to_dict(
            only=('id', 'name', 'address', 'restaurant_pizzas'),
            rules=(
                'restaurant_pizzas.id',
                'restaurant_pizzas.price',
                'restaurant_pizzas.pizza_id',
                'restaurant_pizzas.restaurant_id',
                'restaurant_pizzas.pizza.id',
                'restaurant_pizzas.pizza.name',
                'restaurant_pizzas.pizza.ingredients',
                '-restaurant_pizzas.restaurant',
            )
        )
        
        return result, 200
    
    def delete(self, id):
        """DELETE /restaurants/<int:id>"""
        restaurant = db.session.get(Restaurant, id)
        
        if not restaurant:
            return {"error": "Restaurant not found"}, 404
        
        db.session.delete(restaurant)
        db.session.commit()
        return '', 204




class PizzaList(Resource):
    def get(self):
        """GET /pizzas"""
        pizzas = Pizza.query.all()
        data = [p.to_dict(only=('id', 'name', 'ingredients')) for p in pizzas]
        return data, 200



class RestaurantPizzaCreate(Resource):
    def post(self):
        """POST /restaurant_pizzas"""
        try:
            data = request.get_json()
            
            # Créer le RestaurantPizza
            restaurant_pizza = RestaurantPizza(
                price=data.get('price'),
                pizza_id=data.get('pizza_id'),
                restaurant_id=data.get('restaurant_id')
            )
            
            db.session.add(restaurant_pizza)
            db.session.commit()
            
      
            result = restaurant_pizza.to_dict(
                only=(
                    'id',
                    'price',
                    'pizza_id',
                    'restaurant_id',
                    'pizza.id',
                    'pizza.name',
                    'pizza.ingredients',
                    'restaurant.id',
                    'restaurant.name',
                    'restaurant.address',
                )
            )
            
            return result, 201
            
        except ValueError as e:
            db.session.rollback()
            return {'errors': ['validation errors']}, 400
        except IntegrityError:
            db.session.rollback()
            return {'errors': ['validation errors']}, 400
        except Exception as e:
            db.session.rollback()
            return {'errors': ['validation errors']}, 400


api.add_resource(RestaurantList, '/restaurants')
api.add_resource(RestaurantDetail, '/restaurants/<int:id>')
api.add_resource(PizzaList, '/pizzas')
api.add_resource(RestaurantPizzaCreate, '/restaurant_pizzas')


if __name__ == "__main__":
    app.run(port=5555, debug=True)