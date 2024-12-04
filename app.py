"""
    Lejeaftale Service:
    Håndterer oprettelse, registrering, og autentificering.
    Behandler oprettekse, fjernelse, brugerhåndtering og bil opdatering.
"""

from flask import Flask, jsonify, request, make_response
import sqlite3
import os
from datetime import datetime

from Service.lejeaftaler import fetch_agreements
from Service.lejeaftaler import fetch_available_cars
from Service.lejeaftaler import fetch_new_agreements
from Service.lejeaftaler import create_agreement
from Service.lejeaftaler import update_agreement_status
from Service.lejeaftaler import delete_agreement
from Service.lejeaftaler import fetch_customer_data

script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, 'database/lejeaftale.db')

app = Flask(__name__)

@app.route('/lejeaftaler', methods=['GET'])
def get_all_agreements():
    agreements = fetch_agreements()
    return jsonify(agreements)


@app.route('/ledigeBiler', methods=['GET'])
def available_cars():
    availableCars = fetch_available_cars()
    return jsonify(availableCars)


@app.route('/nyLejeAftale', methods=['GET'])
def new_agreements():
    newAgreements = fetch_new_agreements()
    return jsonify(newAgreements)


@app.route('/opretLejeAftale', methods=['POST'])
def add_agreement():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid json data"}), 400
    
    result, status_code = create_agreement(data)
    return jsonify(result), status_code


@app.route('/statusOpdatering/<int:lejeAftaleID>', methods=['PUT'])
def update_status(lejeAftaleID):
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



@app.route('/sletLejeAftale/<int:lejeAftaleID>', methods=['DELETE'])
def remove_agreement(lejeAftaleID):
    # Parse JSON body
    data = request.get_data

    if not data:
        return jsonify({"error": "Invalid or missing JSON body"}), 400

    # Call the update function with required data
    result, status_code = delete_agreement({"lejeaftale_id": lejeAftaleID})
    return jsonify(result), status_code


@app.route('/kundeID/<int:kundeID>', methods=['GET'])
def get_cutomer_data(kundeID):

    customerData = fetch_customer_data(kundeID)

     # Handle case where no data is found
    if not customerData:
        return jsonify({"error": f"No data found for customer with ID {kundeID}"}), 404

    # Call the update function with required data
    return jsonify(customerData), 200


#@app.route('/statusOpdatering/lejeAftaleID', methods=['POST'])

#@app.route('/lejeAftale/lejeAftaleID', methods=['DELETE'])

app.run(debug=True, host='0.0.0.0', port=5002)