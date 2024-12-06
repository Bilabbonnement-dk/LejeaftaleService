import json
import sqlite3
import os
import datetime


############   Database connection function   ##########


def get_db_connection():
    conn = sqlite3.connect('database/lejeaftale.db')
    conn.row_factory = sqlite3.Row  # Possible fetching rows 
    return conn

script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, '../database/lejeaftale.db')


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