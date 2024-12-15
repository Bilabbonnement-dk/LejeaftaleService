import json
import sqlite3
import os
import datetime
import requests
from flask import jsonify


############   Database connection function   ##########


def get_db_connection():
    conn = sqlite3.connect('database/lejeaftale.db')
    conn.row_factory = sqlite3.Row  # Possible fetching rows 
    return conn

script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, '../database/lejeaftale.db')


######### url for Skades Service #########
SKADES_SERVICE_URL = "http://localhost:5002"


def get_lejeaftale():
    conn = get_db_connection()
    lejeaftale_data = conn.execute("SELECT BilID, PrisPrMåned, KundeID, AbonnementsVarighed FROM Lejeaftale").fetchall()
    conn.close()
    lejeaftale_list = [{"BilID": row["BilID"], "PrisPrMåned": row["PrisPrMåned"], "KundeID": row["KundeID"], "AbonnementsVarighed": row["AbonnementsVarighed"]} for row in lejeaftale_data]
    return jsonify(lejeaftale_list), 200

#bil_id fra bildatabase og ikke lejeaftale database
def get_status(bil_id):
    conn = get_db_connection()
    status_data = conn.execute("SELECT Status FROM Lejeaftale WHERE BilID = ?", (bil_id,)).fetchone()
    conn.close()
    return jsonify({"status": status_data["Status"] if status_data else "Unknown"}), 200


############   Functionallity behind sending KundeID to skades service    ##########

# Function to fetch KundeID and related data for a given LejeaftaleID
def get_kunde_data(lejeaftale_id):

    try:
        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Query to fetch data for the provided LejeaftaleID
        query = "SELECT LejeaftaleID, KundeID, BilID, Status FROM Lejeaftale WHERE LejeaftaleID = ?"

        cursor.execute(query, (lejeaftale_id,))
        result = cursor.fetchone()
        conn.close()

        # Return the result
        if result:
            return {
                "lejeaftale_id": result["LejeaftaleID"],
                "kunde_id": result["KundeID"],
                "bil_id": result["BilID"],
                "status": result["Status"]
            }, 200
        else:
            return {"error": f"No data found for LejeaftaleID {lejeaftale_id}"}, 404

    except sqlite3.Error as e:
        return {"error": f"Database error: {e}"}, 500
    
    
############   Functionallity behind sending damage to skades service    ##########


def send_data_to_skades_service(data):
    try:
        # Send the POST request to SkadesService
        response = requests.post(f"{SKADES_SERVICE_URL}/process-damage-data", json=data)

        # Handle response from SkadesService
        if response.status_code == 200 or 201:
            return response.json(), 200
        elif response.status_code == 404:
            return {"error": "Resource not found on SkadesService"}, 404
        else:
            return {"error": f"Unexpected response from SkadesService: {response.text}"}, response.status_code
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to connect to SkadesService: {str(e)}"}, 500
    

############ Function to fetch BilID and monthly rent related data for a given LejeaftaleID ##########

def get_price_data():

    try:
        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Query to fetch data for the provided LejeaftaleID
        query = "SELECT BilID, PrisPrMåned FROM Lejeaftale "

        cursor.execute(query, )
        result = cursor.fetchone()
        conn.close()

        # Return the result
        if result:
            return {
                "bil_id": result["BilID"],
                "pris_pr_måned": result["PrisPrMåned"]
            }, 200
        else:
            return {"error": f"No data found"}, 404

    except sqlite3.Error as e:
        return {"error": f"Database error: {e}"}, 500
