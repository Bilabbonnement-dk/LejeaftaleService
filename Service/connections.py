import json
import sqlite3
import os
import datetime
from flask import jsonify


############   Database connection function   ##########


def get_db_connection():
    conn = sqlite3.connect('database/lejeaftale.db')
    conn.row_factory = sqlite3.Row  # Possible fetching rows 
    return conn

script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, '../database/lejeaftale.db')

def get_lejeaftale():
    conn = get_db_connection()
    lejeaftale_data = conn.execute("SELECT BilID, PrisPrMåned, KundeID FROM Lejeaftale").fetchall()
    conn.close()
    lejeaftale_list = [{"BilID": row["BilID"], "PrisPrMåned": row["PrisPrMåned"], "KundeID": row["KundeID"]} for row in lejeaftale_data]
    return jsonify(lejeaftale_list), 200

#bil_id fra bildatabase og ikke lejeaftale database
def get_status(bil_id):
    conn = get_db_connection()
    status_data = conn.execute("SELECT Status FROM Lejeaftale WHERE BilID = ?", (bil_id,)).fetchone()
    conn.close()
    return jsonify({"status": status_data["Status"] if status_data else "Unknown"}), 200




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