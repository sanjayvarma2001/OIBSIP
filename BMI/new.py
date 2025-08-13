import sqlite3

conn = sqlite3.connect("bmi_history.db")
cursor = conn.cursor()

# Delete all records
cursor.execute("DELETE FROM bmi_records")

# Or delete by condition (example: id=3)
# cursor.execute("DELETE FROM bmi_records WHERE id = 3")

conn.commit()
conn.close()

print("Records deleted successfully.")
