import mysql.connector

conn = mysql.connector.connect(host="localhost", user="user", password="password", database="events")

c = conn.cursor()
c.execute('''
          DROP TABLE energy_usage, temperature_change
          ''')

conn.commit()
conn.close()