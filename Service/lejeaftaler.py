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

############   Fetch the agreement data   ##########

def fetch_agreements():
    # Connect to the database and fetch agreement data
    conn = get_db_connection()
    cursor = conn.cursor()

     # Execute a query to fetch all records from the agreement table
    cursor.execute("SELECT * FROM Lejeaftale")
    rows = cursor.fetchall()
    conn.close()

    # Convert data to a list of dictionaries with required fields
    filtered_agreements = [
        {
        "lejeaftale_id": row["LejeaftaleID"],
        "kunde_id": row["KundeID"],
        "bil_id": row["BilID"],
        "start_dato": row["StartDato"],
        "slut_dato": row["SlutDate"],
        "udleveringssted": row["Udleveringssted"],
        "abonnements_varighed": row["AbonnementsVarighed"],
        "aftale_km": row["AftaleKM"],
        "pris_pr_måned": row["PrisPrMåned"],
        "status": row["Status"]
    } 
    for row in rows
    ]
    
    return filtered_agreements
    
# Fetch and print the filtered guest data
agreement_data = fetch_agreements()
#print(guests_data)

############   Fetch all available cars data   ##########

def fetch_available_cars():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT BilID, PrisPrMåned FROM Lejeaftale WHERE Status = 'ledig'")
    available_cars = cursor.fetchall()
    
    conn.close()
    
    # Format the result
    formatted_cars = [
        {
            "bil_id": car[0], 
            "pris_pr_måned": car[1]
        } 
        for car in available_cars
    ]

    return formatted_cars, 201

############   Fetch newly created agreements data   ##########

def fetch_new_agreements():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Lejeaftale WHERE status = 'ny'")
    rows = cursor.fetchall()
    conn.close()

    formatted_agreements = [
        {
        "lejeaftale_id": row[0],
        "kunde_id": row[1],
        "bil_id": row[2],
        "start_dato": row[3],
        "slut_date": row[4],
        "udleveringssted": row[5],
        "abonnements_varighed": row[6],
        "aftale_km": row[7],
        "pris_pr_måned": row[8],
        "status": row[9]
    } 
    for row in rows
    ]
    
    return formatted_agreements

############   Create new agreement data   ##########

def create_agreement(data):
    # Validate input
    required_fields = ['kunde_id', 'bil_id', 'start_dato', 'slut_date', 'udleveringssted', 'abonnements_varighed', 'status']
    if not all(field in data for field in required_fields):
        return {"error": "Missing required fields"}, 400

    kunde_id = data['kunde_id']
    bil_id = data['bil_id']
    start_dato = data['start_dato']
    slut_date = data['slut_date']
    udleveringssted = data['udleveringssted']
    abonnements_varighed = data['abonnements_varighed']
    pris_pr_måned = data.get('pris_pr_måned', 0)
    status = data['status']

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Insert new agreement
        cursor.execute(
            "INSERT INTO Lejeaftale (KundeID, BilID, StartDato, SlutDate, Udleveringssted, AbonnementsVarighed, AftaleKM, PrisPrMåned, Status) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (kunde_id, bil_id, start_dato, slut_date, udleveringssted, abonnements_varighed, 0, pris_pr_måned, status)
        )
        agreement_id = cursor.lastrowid

        # Fetch available cars
        available_cars = cursor.execute(
            "SELECT BilID, PrisPrMåned FROM Lejeaftale WHERE Status = 'ledig'"
        ).fetchall()

        car_costs = [
            {"bil_id": car[0], "pris_pr_måned": car[1], "pris_i_alt": car[1] * abonnements_varighed}
            for car in available_cars
        ]
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        return {"error": f"Database error: {e}"}, 500
    finally:
        conn.close()

    return {
        "message": "Agreement created successfully",
        "agreement_id": agreement_id,
        "available_cars": car_costs
    }, 201

############   Update new agreement status   ##########

def update_agreement_status(data):
    # Extract the required fields from the input dictionary
    lejeAftaleID = data.get('lejeaftale_id')
    new_status = data.get('status')

    # Validate input
    if not lejeAftaleID or not new_status:
        return {"error": "Missing required fields: 'lejeaftale_id' and/or 'status'"}, 400

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        # Perform the update
        cursor.execute(
            "UPDATE Lejeaftale SET Status = ? WHERE LejeaftaleID = ?", 
            (new_status, lejeAftaleID)
        )
        conn.commit()

        # Check if any row was updated
        if cursor.rowcount == 0:
            return {"error": "No agreement found with the given ID"}, 404

    return {"message": "Status updated successfully"}, 200


############   Get a cutomers agreement data   ##########
from datetime import datetime

def fetch_customer_data(kundeID):
    # Validate input
    if not kundeID:
        return {"error": "Missing required field: 'kunde_id'"}, 400

    # Connect to the database
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Access rows as dictionaries
    cursor = conn.cursor()

    # Fetch rental agreements for the given customer ID
    cursor.execute("SELECT * FROM Lejeaftale WHERE KundeID = ?", (kundeID,))
    rows = cursor.fetchall()
    conn.close()

    # Handle no data found
    if not rows:
        return {"error": f"No agreements found for customer with ID {kundeID}"}, 404

    # Process and format results
    formatted_lejeaftaler = []
    for row in rows:
        # Handle date parsing and calculate remaining time
        try:
            slut_dato = datetime.strptime(row["SlutDate"], '%Y-%m-%d')
            remaining_time = (slut_dato - datetime.now()).days
        except ValueError:
            remaining_time = None  # If date parsing fails

        formatted_lejeaftaler.append({
            "lejeaftale_id": row["LejeaftaleID"],
            "kunde_id": row["KundeID"],
            "bil_id": row["BilID"],
            "start_dato": row["StartDato"],
            "slut_dato": row["SlutDate"],
            "udleveringssted": row["Udleveringssted"],
            "abonnements_varighed": row["AbonnementsVarighed"],
            "aftale_km": row["AftaleKM"],
            "pris_pr_måned": row["PrisPrMåned"],
            "status": row["Status"],
            "remaining_time": remaining_time
        })

    return {"lejeaftaler": formatted_lejeaftaler}, 200



############   Delete agreement data   ##########

def delete_agreement(data):

    lejeAftaleID = data.get('lejeaftale_id')

    if not lejeAftaleID:
        return {"error": "Missing required fields: 'lejeaftale_id'"}, 400

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM Lejeaftale WHERE LejeaftaleID = ?", (lejeAftaleID,)
            )
        conn.commit()

         # Check if any row was updated
        if cursor.rowcount == 0:
            return {"error": "No agreement found with the given ID"}, 404

    return {"message": "Agreement succesfully deleted"}, 200

############   Send data to SkadesService  ##########

def get_customerID_by_CarID(bil_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Query to get all BilIDs associated with the given KundeID
    cursor.execute("SELECT KundeID FROM Lejeaftale WHERE BilID = ?", (bil_id,))
    rows = cursor.fetchall()
    conn.close()

    # Return a list of KundeIDs
    kunde_ids = [row["KundeID"] for row in rows]
    return {"bil_id": bil_id, "kunde_ids": kunde_ids}, 200