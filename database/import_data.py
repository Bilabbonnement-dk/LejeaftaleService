# import_json.py

import csv
import sqlite3

# create connection to sqlite 
conn = sqlite3.connect('lejeaftale.db')
cursor = conn.cursor()
cursor.execute('DROP TABLE IF EXISTS Lejeaftale')

# Create lejeaftale table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS Lejeaftale (
    LejeaftaleID INTEGER PRIMARY KEY AUTOINCREMENT,
    KundeID INTEGER NULL,
    BilID INTEGER NULL,
    StartDato DATE, 
    SlutDate DATE,
    Udleveringssted TEXT,
    AbonnementsVarighed FLOAT NOT NULL,
    AftaleKM FLOAT NOT NULL,
    PrisPrMåned FLOAT,
    Status TEXT NOT NULL
)
''')

with open('Lejeaftale.csv', 'r', encoding='utf-8-sig') as files:
    csv_reader = csv.DictReader(files)
    
    csv_reader = csv.DictReader(files, delimiter=';')

    print("Headers:", csv_reader.fieldnames)  # Print the detected headers

    # Insert the data
    for lejeaftale in csv_reader:
        print(lejeaftale)
        cursor.execute('''
        INSERT INTO Lejeaftale (LejeaftaleID, KundeID, BilID, StartDato, SlutDate, Udleveringssted, AbonnementsVarighed, AftaleKM, PrisPrMåned, Status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            lejeaftale["LejeaftaleID"], 
            lejeaftale["KundeID"], 
            lejeaftale["BilID"], 
            lejeaftale["StartDato"], 
            lejeaftale["SlutDate"],
            lejeaftale["Udleveringssted"], 
            lejeaftale["AbonnementsVarighed"], 
            lejeaftale["AftaleKM"], 
            lejeaftale["PrisPrMåned"],
            lejeaftale["Status"]
            ))

conn.commit()
conn.close()
print("Data imported successfully.")