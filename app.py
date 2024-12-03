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
@app.route('/opretLejeAftale', methods=['POST'])
def opretLejeAftale():
    data = request.get_json()
    lejeaftale_id = data.get('lejeaftale_id')
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
    cursor.execute("INSERT INTO Lejeaftale (LejeaftaleID, KundeID, BilID, StartDato, SlutDate, Udleveringssted, AbonnementsVarighed, AftaleKM, PrisPrMåned, Status) "
                   "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                   (lejeaftale_id, kunde_id, bil_id, start_dato, slut_dato, udleveringssted, abonnements_varighed, aftale_km, pris_pr_måned, status))
    conn.commit()
    conn.close()
    return jsonify({"message": "Lejeaftale oprettet"}), 201


@app.route('/nyLejeAftale', methods=['POST'])
def nyLejeAftale():
    conn = sqlite3.connect('lejeaftale.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Lejeaftale WHERE status = 'ny'")
    rows = cursor.fetchall()
    conn.close()
    return rows

app.run(debug=True, host='0.0.0.0', port=5002)