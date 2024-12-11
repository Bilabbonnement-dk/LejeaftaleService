import sqlite3

DATABASE = "bilDatabase.db"

# Hent alle biler
def fetch_all_cars():
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM bil")
    rows = cursor.fetchall()
    connection.close()

    # Konverter til liste af dictionaries
    columns = [col[0] for col in cursor.description]
    cars = [dict(zip(columns, row)) for row in rows]

    connection.close()
    return cars

# Hent en specifik bil
def fetch_car_by_id(bil_id):
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM bil WHERE bil_id = ?", (bil_id,))
    row = cursor.fetchone()

    if row:
        columns = [col[0] for col in cursor.description]
        car = dict(zip(columns, row))
    else:
        car = None
    
    connection.close()
    return car

# Slet en bil
def delete_car(bil_id):
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    cursor.execute("DELETE FROM bil WHERE bil_id = ?", (bil_id,))
    connection.commit()
    rows_deleted = cursor.rowcount
    connection.close()

    if rows_deleted > 0:
        return {"message": f"Bil med ID {bil_id} er slettet"}
    else:
        return {"error": f"Bil med ID {bil_id} ikke fundet"}


# Opdater bilens status
def update_car_status(bil_id, new_status):
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    # Opdater bilens status baseret på bil_id
    cursor.execute('''
        UPDATE bil
        SET status = ?
        WHERE bil_id = ?
    ''', (new_status, bil_id))

    # Gem ændringer
    connection.commit()

    # Tjek, om en række blev opdateret
    rows_updated = cursor.rowcount
    connection.close()

    if rows_updated > 0:
        return {"message": f"Status for bil med ID {bil_id} opdateret til '{new_status}'"}
    else:
        return {"error": f"Bil med ID {bil_id} ikke fundet"}
