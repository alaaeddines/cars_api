from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson import ObjectId

# Replace with your MongoDB connection details
client = MongoClient("mongodb://localhost:27017/")
db = client["database"]
car_collection = db["cars"]

class Car:
    def __init__(self, origin, model, kilometer_range, is_first_hand, production_year, additional_data=None):
        self.origin = origin
        self.model = model
        self.kilometer_range = kilometer_range
        self.is_first_hand = is_first_hand
        self.production_year = production_year

    def to_dict(self):
        return {
            "origin": self.origin,
            "model": self.model,
            "kilometer_range": self.kilometer_range,
            "is_first_hand": self.is_first_hand,
            "production_year": self.production_year,
        }

app = Flask(__name__)

#post car
@app.route('/cars', methods=['POST'])
def create_car():
    data = request.get_json()
    if not data or not all(field in data for field in ['origin', 'model', 'kilometer_range', 'is_first_hand', 'production_year']):
        return jsonify({'error': 'Missing required fields'}), 400

    new_car = Car(**data)
    car_collection.insert_one(new_car.to_dict())

    return jsonify({'message': 'Car created successfully'}), 201
#Get car
@app.route('/cars', methods=['GET'])
def get_all_cars():
    cars = car_collection.find()
    return jsonify([car for car in cars])
#Get by car_id
@app.route('/cars/<car_id>', methods=['GET'])
def get_car_by_id(car_id):
    car = car_collection.find_one({"_id": ObjectId(car_id)})
    if not car:
        return jsonify({'error': 'Car not found'}), 404
    return jsonify(car)
#Put by car_id
@app.route('/cars/<car_id>', methods=['PUT'])
def update_car(car_id):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Missing data'}), 400

    update_result = car_collection.update_one(
        {"_id": ObjectId(car_id)},
        {"$set": data}
    )

    if update_result.matched_count == 0:
        return jsonify({'error': 'Car not found'}), 404

    return jsonify({'message': 'Car updated successfully'}), 200

#Delete by car_id
@app.route('/cars/<car_id>', methods=['DELETE'])
def delete_car(car_id):
    delete_result = car_collection.delete_one({"_id": ObjectId(car_id)})
    if delete_result.deleted_count == 0:
        return jsonify({'error': 'Car not found'}), 404
    return jsonify({'message': 'Car deleted successfully'}), 204

#Get cars by production_year
@app.route('/cars/filter/production_year', methods=['GET'])
def filter_by_production_year():
    year = request.args.get('year')
    if not year:
        return jsonify({'error': 'Missing year parameter'}), 400

    try:
        year = int(year)
    except ValueError:
        return jsonify({'error': 'Invalid year format'}), 400

    cars = car_collection.find({'production_year': year})
    return jsonify([car for car in cars])

if __name__ == '__main__':
    app.run(debug=True)
