"""
    Lejeaftale Service:
    Håndterer oprettelse, registrering, og autentificering.
    Behandler oprettekse, fjernelse, brugerhåndtering og bil opdatering.
"""

from flask import Flask, jsonify, request, make_response
import requests
import sqlite3
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, 'database/lejeaftale.db')

app = Flask(__name__)

@app.route('/ledigeBiler', methods=['GET'])
def ledigeBiler():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT BilID, PrisPrMåned FROM Lejeaftale WHERE Status = 'ledig'")
    available_cars = cursor.fetchall()
    
    conn.close()
    
    # Format the result
    formatted_cars = [{"bil_id": car[0], "pris_pr_måned": car[1]} for car in available_cars]
    
    return jsonify({"available_cars": formatted_cars}), 201

@app.route('/nyLejeAftale', methods=['GET'])
def nyLejeAftale():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Lejeaftale WHERE status = 'ny'")
    nye_leje_aftaler = cursor.fetchall()
    conn.close()

    formatted_agreements = [{
        "lejeaftale_id": agreement[0],
        "kunde_id": agreement[1],
        "bil_id": agreement[2],
        "start_dato": agreement[3],
        "slut_dato": agreement[4],
        "udleveringssted": agreement[5],
        "abonnements_varighed": agreement[6],
        "aftale_km": agreement[7],
        "pris_pr_måned": agreement[8],
        "status": agreement[9]
    } for agreement in nye_leje_aftaler]
    
    return jsonify({"nye_leje_aftaler": formatted_agreements}), 200

@app.route('/opretLejeAftale', methods=['POST'])
def opretLejeAftale():
    data = request.get_json()
    kunde_id = data.get('kunde_id')
    bil_id = data.get('bil_id')
    start_dato = data.get('start_dato')
    slut_dato = data.get('slut_dato')
    udleveringssted = data.get('udleveringssted')
    abonnements_varighed = data.get('abonnements_varighed')
    aftale_km = data.get('aftale_km')
    pris_pr_måned = data.get('pris_pr_måned')
    status = data.get('status')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Lejeaftale (KundeID, BilID, StartDato, SlutDate, Udleveringssted, AbonnementsVarighed, AftaleKM, PrisPrMåned, Status) "
                   "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                   (kunde_id, bil_id, start_dato, slut_dato, udleveringssted, abonnements_varighed, aftale_km, pris_pr_måned, status))
    
    cursor.execute("SELECT BilID, PrisPrMåned FROM Lejeaftale WHERE Status = 'ledig'")
    available_cars = cursor.fetchall()
    
    car_costs = []
    for car in available_cars:
        car_id, pris_pr_måned = car
        total_cost = pris_pr_måned * abonnements_varighed
        car_costs.append({
            "bil_id": car_id,
            "pris_pr_måned": pris_pr_måned,
            "pris_i_alt": total_cost
        })
    conn.commit()
    conn.close()
    return jsonify({
        "message": "Lejeaftale oprettet",
        "available_cars": car_costs
    }), 201

@app.route('/statusOpdatering/lejeAftaleID', methods=['POST'])

@app.route('/lejeAftale/lejeAftaleID', methods=['DELETE'])

app.run(debug=True, host='0.0.0.0', port=5002)