"""
    Lejeaftale Service:
    Håndterer oprettelse, registrering, og autentificering.
    Behandler oprettekse, fjernelse, brugerhåndtering og bil opdatering.
"""

from flask import Flask, jsonify, request, make_response
from datetime import datetime
import requests
from flasgger import Swagger, swag_from
from swagger.config import swagger_config

from Service.lejeaftaler import fetch_agreements
from Service.lejeaftaler import fetch_available_cars
from Service.lejeaftaler import fetch_new_agreements
from Service.lejeaftaler import create_agreement
from Service.lejeaftaler import update_agreement_status
from Service.lejeaftaler import delete_agreement
from Service.lejeaftaler import fetch_customer_data
from Service.connections import get_kunde_data
from Service.connections import get_lejeaftale
from Service.connections import get_status
from Service.connections import send_data_to_skades_service
from Service.connections import get_price_data
from import_excel_to_sqlite import import_excel_to_sqlite
from Service.bildatabase import fetch_all_cars, fetch_car_by_id, delete_car, update_car_status


app = Flask(__name__)
swagger = Swagger(app, config=swagger_config)

@app.route('/')
@swag_from('swagger/home.yaml')
def home():
    return jsonify({
        "service": "API Gateway",
        "available_endpoints": [
            {
                "path": "/lejeaftaler",
                "method": "GET",
                "description": "Get all lejeaftaler"
            },
            {
                "path": "/ledigeBiler",
                "method": "GET",
                "description": "Get all available cars"
            },
            {
                "path": "/nyLejeAftale",
                "method": "GET",
                "description": "Get all new lejeaftaler"
            },
            {
                "path": "/opretLejeAftale",
                "method": "POST",
                "description": "Create a new lejeaftale"
            },
            {
                "path": "/statusOpdatering/<int:lejeAftaleID>",
                "method": "PUT",
                "description": "Update the status of a lejeaftale"
            },
            {
                "path": "/sletLejeAftale/<int:lejeAftaleID>",
                "method": "DELETE",
                "description": "Delete a lejeaftale"
            },
            {
                "path": "/kundeID/<int:kundeID>",
                "method": "GET",
                "description": "Get all lejeaftaler for a specific customer"
            },
            {
                "path": "/process-data",
                "method": "POST",
                "description": "Process data from Skades Service"
            },
            {
                "path": "/kunde/<int:bil_id>/biler",
                "method": "GET",
                "description": "Get customer data by car ID"
            },
            {
                "path": "/send-damage-data/new-damage",
                "method": "POST",
                "description": "Send damage data to Skades Service"
            },
            {
                "path": "/lejeaftale",
                "method": "GET",
                "description": "Get active lejeaftale"
            },
            {
                "path": "/status/<int:bil_id>",
                "method": "GET",
                "description": "Get car status"
            },
            {
                "path": "/process-pris-data",
                "method": "POST",
                "description": "Process price data to Skades Service"
            },
            {
                "path": "/opdater-database",
                "method": "POST",
                "description": "Update the database with data from Excel"
            },
            {
                "path": "/biler",
                "method": "GET",
                "description": "Get all cars"
            },
            {
                "path": "/biler/<int:bil_id>",
                "method": "GET",
                "description": "Get car by ID"
            },
            {
                "path": "/biler/<int:bil_id>",
                "method": "DELETE",
                "description": "Delete a car by ID"
            },
            {
                "path": "/biler/<int:bil_id>/status",
                "method": "PUT",
                "description": "Update car status"
            }
        ]
    })

@app.route('/lejeaftaler', methods=['GET'])
@swag_from('swagger/lejeaftaler.yaml')
def get_all_agreements():
    agreements = fetch_agreements()
    return jsonify(agreements)


@app.route('/ledigeBiler', methods=['GET'])
@swag_from('swagger/ledigeBiler.yaml')
def available_cars():
    availableCars = fetch_available_cars()
    return jsonify(availableCars)


@app.route('/nyLejeaftale', methods=['GET'])
@swag_from('swagger/nyLejeaftale.yaml')
def new_agreements():
    newAgreements = fetch_new_agreements()
    return jsonify(newAgreements)


@app.route('/opretLejeaftale', methods=['POST'])
@swag_from('swagger/opretLejeaftale.yaml')
def add_agreement():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid json data"}), 400
    
    result, status_code = create_agreement(data)
    return jsonify(result), status_code


@app.route('/statusOpdatering/<int:lejeAftaleID>', methods=['PUT'])
@swag_from('swagger/statusOpdatering.yaml')
def update_agreement_status(lejeAftaleID):
    # Parse JSON body
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid or missing JSON body"}), 400

    # Validate 'status' field in the body
    new_status = data.get('status')
    if not new_status:
        return jsonify({"error": "'status' field is required"}), 400

    # Call the update function with required data
    result, status_code = update_agreement_status({"lejeaftale_id": lejeAftaleID, "status": new_status})
    return jsonify(result), status_code


@app.route('/sletLejeaftale/<int:lejeAftaleID>', methods=['DELETE'])
@swag_from('swagger/sletLejeaftale.yaml')
def remove_agreement(lejeAftaleID):
    # Parse JSON body
    data = request.get_data

    if not data:
        return jsonify({"error": "Invalid or missing JSON body"}), 400

    # Call the update function with required data
    result, status_code = delete_agreement({"lejeaftale_id": lejeAftaleID})
    return jsonify(result), status_code


@app.route('/kundeID/<int:kundeID>', methods=['GET'])
@swag_from('swagger/kundeID.yaml')
def get_cutomer_data(kundeID):

    customerData = fetch_customer_data(kundeID)

     # Handle case where no data is found
    if not customerData:
        return jsonify({"error": f"No data found for customer with ID {kundeID}"}), 404

    # Call the update function with required data
    return jsonify(customerData), 200


########## Send and recieve data ##########

# Send data to Skades Service
@app.route('/process-data', methods=['POST'])
@swag_from('swagger/processData.yaml')
def process_data():
    # Retrieve JSON payload 
    data = request.json
    print(f"Received data: {data}")

    # Process data and return a response
    processed_data = {"message": "Data processed successfully", "received": data}
    return jsonify(processed_data), 200


# Preocess data to Skades Service
@app.route('/process-kunde-data', methods=['POST'])
@swag_from('swagger/processKundeData.yaml')
def process_kunde_data():

    # Retrieve json payload
    data = request.json
    lejeaftale_id = data.get("lejeaftale_id")

    # Validate input
    if not lejeaftale_id or not isinstance(lejeaftale_id, int):
        return jsonify({"error": "Invalid or missing field: 'lejeaftale_id'"}), 400

    # Call the service function to get data
    result, status_code = get_kunde_data(lejeaftale_id)
    
    return jsonify(result), status_code

# Send data to Lejeaftale Service
@app.route('/send-damage-data/new-damage', methods=['POST'])
@swag_from('swagger/sendDamageData.yaml')
def send_request():

    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid json data"}), 400
    
    result, status_code = send_data_to_skades_service(data)
    return jsonify(result), status_code


@app.route('/lejeaftale', methods=['GET'])
@swag_from('swagger/aktivLejeaftale.yaml')
def active_lejeaftale():
    active_lejeaftale = get_lejeaftale()
    return active_lejeaftale

@app.route('/status/<int:bil_id>', methods=['GET'])
@swag_from('swagger/status.yaml')
def get_car_status(bil_id):
    status = get_status(bil_id)
    return status

# Preocess price data to Skades Service
@app.route('/process-pris-data', methods=['POST'])
@swag_from('swagger/processPrisData.yaml')
def process_price_data():

    # Retrieve json payload
    data = request.json

    # Validate input
    if not data:
        return jsonify({"error": "No data found'"}), 400

    # Call the service function to get data
    result, status_code = get_price_data()
    
    return jsonify(result), status_code

####### Hent Data fra bilDatabase ########

# Opdater database
@app.route('/opdater-database', methods=['POST'])
@swag_from('swagger/opdaterDatabase.yaml')
def opdater_database():
    try:
        import_excel_to_sqlite()
        return jsonify({"message": "Databasen er opdateret med data fra Excel"}), 200
    except Exception as e:
        return jsonify({"message": "Fejl under opdatering af databasen", "error": str(e)}), 500

# Hent alle biler
@app.route('/biler', methods=['GET'])
@swag_from('swagger/biler.yaml')
def get_all_cars():
    cars = fetch_all_cars()
    return jsonify(cars), 200

# Hent en bil baseret på bil_id
@app.route('/biler/<int:bil_id>', methods=['GET'])
@swag_from('swagger/bilerByID.yaml')
def get_car(bil_id):
    car = fetch_car_by_id(bil_id)
    if car:
        return jsonify(car), 200
    return jsonify({"error": f"Bil med ID {bil_id} ikke fundet"}), 404

# Slet en bil
@app.route('/biler/<int:bil_id>', methods=['DELETE'])
@swag_from('swagger/sletBilByID.yaml')
def remove_car(bil_id):
    response = delete_car(bil_id)
    return jsonify(response), 200

# Endpoint: Opdater bilens status
@app.route('/biler/<int:bil_id>/status', methods=['PUT'])
@swag_from('swagger/opdaterBilStatus.yaml')
def change_car_status(bil_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid or missing JSON body"}), 400

    # Valider, at 'status' feltet er til stede
    new_status = data.get('status')
    if not new_status or new_status not in ["aktiv", "inaktiv"]:
        return jsonify({"error": "Ugyldig eller manglende værdi for 'status'. Tilladte værdier: 'aktiv', 'inaktiv'"}), 400

    # Opdater bilens status
    result = update_car_status(bil_id, new_status)
    if "error" in result:
        return jsonify(result), 404
    return jsonify(result), 200

#@app.route('/statusOpdatering/lejeAftaleID', methods=['POST'])

#@app.route('/lejeAftale/lejeAftaleID', methods=['DELETE'])

app.run(debug=True, host='0.0.0.0', port=5003)