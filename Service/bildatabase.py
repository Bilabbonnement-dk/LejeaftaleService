import sqlite3

DATABASE = "bilDatabase.db"

# Get all cars
def fetch_all_cars():
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM bil")
    rows = cursor.fetchall()
    connection.close()

    # Konverting a list to dict
    columns = [col[0] for col in cursor.description]
    cars = [dict(zip(columns, row)) for row in rows]

    connection.close()
    return cars

# Get a specific car
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

# Delete a car
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


# Update a cars status
def update_car_status(bil_id, new_status):
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    # Update the status based on the car_id
    cursor.execute('''
        UPDATE bil
        SET status = ?
        WHERE bil_id = ?
    ''', (new_status, bil_id))

    # Save the changes made
    connection.commit()

    # Check if a row is not updated
    rows_updated = cursor.rowcount
    connection.close()

    if rows_updated > 0:
        return {"message": f"Status for bil med ID {bil_id} opdateret til '{new_status}'"}
    else:
        return {"error": f"Bil med ID {bil_id} ikke fundet"}
