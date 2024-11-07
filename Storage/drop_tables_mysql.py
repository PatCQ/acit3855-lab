import mysql.connector

conn = mysql.connector.connect(host="acit3855-kafka.eastus2.cloudapp.azure.com", user="user", password="password", database="events")

c = conn.cursor()
c.execute('''
          DROP TABLE energy_usage, temperature_change
          ''')

conn.commit()
conn.close()