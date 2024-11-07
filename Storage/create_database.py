import sqlite3

conn = sqlite3.connect('readings.sqlite') #creates a connection to a sqlite database file. If it does not exist it will make it
c = conn.cursor() #cursor object used to execute SQL commands


#energy tbl
c.execute('''
          CREATE TABLE energy_usage
          (id INTEGER PRIMARY KEY ASC, 
          device_id VARCHAR(250) NOT NULL,
          home_room VARCHAR(250) NOT NULL,
          energy_use INTEGER NOT NULL,
          timestamp_start VARCHAR(250) NOT NULL,
          timestamp_end VARCHAR(250) NOT NULL,
          trace_id VARCHAR(250) NOT NULL,
          date_created VARCHAR(100) NOT NULL)
          ''')

#temperature tbl
c.execute('''
          CREATE TABLE temperature_change
          (id INTEGER PRIMARY KEY ASC, 
          device_id VARCHAR(250) NOT NULL,
          home_room VARCHAR(250) NOT NULL,
          temperature INTEGER NOT NULL,
          timestamp VARCHAR(250) NOT NULL,
          trace_id VARCHAR(250) NOT NULL,
          date_created VARCHAR(100) NOT NULL)
          ''')

conn.commit()
conn.close()