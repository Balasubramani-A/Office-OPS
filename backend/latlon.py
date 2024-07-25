from flask import Flask, request, jsonify
from flask_cors import CORS
from haversine import haversine, Unit
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)

# Define coordinates to check against
target_location = (12.955462595858718, 77.57442160016858)

# MongoDB client setup
client = MongoClient('mongodb://localhost:27017/')  # Adjust the connection string as needed
db = client['leave_tracker']
leave_collection = db['leaves']
entry_collection = db['entries']
task_collection = db['tasks']
emp_collection = db['empentries']

def is_nearby(current_location, target_location, distance_threshold=0.5):
    distance = haversine(current_location, target_location, unit=Unit.KILOMETERS)
    print(f"Calculated distance: {distance} km")  # Debugging line
    return distance <= distance_threshold

@app.route('/location', methods=['POST'])
def receive_location():
    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    print(f"Received latitude: {latitude}, longitude: {longitude}")  # Debugging line

    if latitude is None or longitude is None:
        return jsonify({"status": "error", "message": "Latitude and longitude must be provided"}), 400

    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except ValueError:
        return jsonify({"status": "error", "message": "Latitude and longitude must be numbers"}), 400

    current_location = (latitude, longitude)

    # Check if the current location is within 500 meters of the target location
    if is_nearby(current_location, target_location):
        return jsonify({"status": "logged in"}), 200
    else:
        return jsonify({"status": "not logged in"}), 200

@app.route('/leave', methods=['POST'])
def receive_leave():
    data = request.get_json()
    leave_data = {
        "start_date": data.get('start_date'),
        "end_date": data.get('end_date'),
        "selected_days": data.get('selected_days'),
        "leave_type": data.get('leave_type'),
        "reason": data.get('reason')
    }
    print(f"Received leave data: {leave_data}")  # Debugging line
    # Insert leave data into MongoDB
    leave_collection.insert_one(leave_data)

    return jsonify({"status": "success"}), 200

@app.route('/entry', methods=['POST'])
def receive_entry():
    data = request.get_json()
    entry_data = {
        "start_date": data.get('start_date'),
        "end_date": data.get('end_date'),
        "totalProductiveTime": data.get('totalProductiveTime'),
        "data": data.get('data')
    }
    print(f"Received entry data: {entry_data}")  # Debugging line
    # Insert entry data into MongoDB
    entry_collection.insert_one(entry_data)

    return jsonify({"status": "success"}), 200

@app.route('/tasks', methods=['POST'])
def receive_task():
    data = request.get_json()
    task_data = {
        "task_name": data.get('task_name'),
        "task_time": data.get('task_time'),
        "task_importance": data.get('task_importance'),
        "task_deadline": data.get('task_deadline')
    }
    print(f"Received task data: {task_data}")  # Debugging line
    # Insert task data into MongoDB
    task_collection.insert_one(task_data)

    return jsonify({"status": "success"}), 200

@app.route('/api/employee-details', methods=['GET'])
def get_employee_details():
    # Retrieve data from MongoDB
    empentries = emp_collection.find()  # Adjust the query as needed
    employee_details = []
    for entry in empentries:
        employee_details.append({
            "key": str(entry.get("_id")),
            "name": entry.get("Name"),
            "eid": entry.get("e_id"),
            "absent": entry.get("absent"),
            "reason": entry.get("reason"),
            "description": entry.get("description")
        })
    print(f"Employee details: {employee_details}")  # Debugging line
    return jsonify(employee_details)

@app.route('/api/leave-applications', methods=['GET'])
def get_leave_applications():
    # Retrieve data from MongoDB
    leaves = leave_collection.find()  # Adjust the query as needed
    
    leave_applicataions = []
    for leave in leaves:
        leave_applications.append({
            "key": str(leave.get("_id")),
            "Name": leave.get("Name"),
            "e_id": leave.get("e_id"),
            "reason": leave.get("reason"),
            "description": leave.get("description")
        })
        print(f"Leave application: {leave}")  # Debugging line
    return jsonify(leave_applications)

if __name__ == '__main__':
    app.run(debug=True)

