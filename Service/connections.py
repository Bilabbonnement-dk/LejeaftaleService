import json
import sqlite3
import os
import datetime
import requests
from flask import jsonify


############   Database connection function   ##########


def get_db_connection():
    conn = sqlite3.connect('database/lejeaftale.db')
    conn.row_factory = sqlite3.Row 
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

# get bil_id from car database and not lejeaftale database
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
        print("Connecting to the database...")

        conn = get_db_connection()
        conn.row_factory = sqlite3.Row 
        cursor = conn.cursor()

        # Query to fetch car id and monthly price data
        query = "SELECT BilID, PrisPrMåned FROM Lejeaftale"
        print("Executing query:", query)
        cursor.execute(query)


        results = cursor.fetchall()
        conn.close()

        # Debugging output
        print("Results fetched:", results)

        # Transform the results into a list of dictionaries
        if results:
            price_data = [
                {"bil_id": row["BilID"], "pris_pr_måned": row["PrisPrMåned"]}
                for row in results
            ]
            print("Price data:", price_data)
            return {"price_data": price_data}, 200
        else:
            print("No data found in the table.")
            return {"error": "No data found"}, 404

    except sqlite3.Error as e:
        print("Database error:", e)
        return {"error": f"Database error: {e}"}, 500
