import pandas as pd
import sqlite3

# Indtast filnavn for din Excel-fil og database
EXCEL_FILE = "/Users/natazjadahl/Desktop/bildatabase.xlsx"
DATABASE = "bilDatabase.db"

def import_excel_to_sqlite():
    # Læs Excel-filen
    df = pd.read_excel(EXCEL_FILE)

    # Forbind til SQLite-databasen
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    # Opret bil-tabellen, hvis den ikke eksisterer
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bil (
            bil_id INTEGER PRIMARY KEY,
            city TEXT,
            dato_indkoebt TEXT,
            start_abonnement_dato TEXT,
            slut_dato_abonnement TEXT,
            bilmaerke TEXT,
            indkoebspris REAL NOT NULL,
            braendstoftype TEXT NOT NULL,
            koert_km_ved_abonnement_start REAL,
            abonnement_km_koert REAL,
            aftalt_kontrakt_abonnement_km REAL,
            abonnement_periode INTEGER,
            abonnement_pris_pr_maaned REAL,
            udleveringssted TEXT,
            abonnement_varighed_aar INTEGER,
            status TEXT,
            afskrivning_pr_km REAL
        )
    ''')

    # Indsæt data fra Excel-filen i SQLite-databasen
    df.to_sql('bil', connection, if_exists='replace', index=False)

    print("Data fra Excel-filen er importeret til SQLite-databasen.")
    connection.close()

if __name__ == "__main__":
    import_excel_to_sqlite()
