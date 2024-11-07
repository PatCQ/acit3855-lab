import mysql.connector

conn = mysql.connector.connect(host="acit3855-kafka.eastus2.cloudapp.azure.com", user="user", password="password", database="events")
c = conn.cursor()


#energy tbl
c.execute('''
          CREATE TABLE energy_usage
          (id INT NOT NULL AUTO_INCREMENT, 
          device_id VARCHAR(250) NOT NULL,
          home_room VARCHAR(250) NOT NULL,
          energy_use INTEGER NOT NULL,
          timestamp_start VARCHAR(250) NOT NULL,
          timestamp_end VARCHAR(250) NOT NULL,
          trace_id VARCHAR(250) NOT NULL,
          date_created VARCHAR(100) NOT NULL,
          CONSTRAINT energy_usage_pk PRIMARY KEY (id) )
          ''')

#temperature tbl
c.execute('''
          CREATE TABLE temperature_change
          (id INT NOT NULL AUTO_INCREMENT, 
          device_id VARCHAR(250) NOT NULL,
          home_room VARCHAR(250) NOT NULL,
          temperature INTEGER NOT NULL,
          timestamp VARCHAR(250) NOT NULL,
          trace_id VARCHAR(250) NOT NULL,
          date_created VARCHAR(100) NOT NULL,
          CONSTRAINT temperature_change_pk PRIMARY KEY (id) )
          ''')

conn.commit()
conn.close()