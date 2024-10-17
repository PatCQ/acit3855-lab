from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql.functions import now
from base import Base
from datetime import datetime


    
class EnergyUsage(Base):
    """ Energy usage """

    __tablename__ = "energy_usage"

    id = Column(Integer, primary_key=True)
    device_id = Column(String(250), nullable=False)
    home_room = Column(String(250), nullable=False)
    energy_use = Column(Integer, nullable=False)
    timestamp_start = Column(String(250), nullable=False)
    timestamp_end = Column(String(250), nullable=False)
    trace_id = Column(String(250), nullable=False)
    date_created = Column(DateTime, nullable=False)

    def __init__(self, device_id, home_room, energy_use, timestamp_start, timestamp_end, trace_id):
        """ Initializes a heart rate reading """
        self.device_id = device_id
        self.home_room = home_room
        self.energy_use = energy_use
        self.timestamp_start = timestamp_start
        self.timestamp_end = timestamp_end
        self.trace_id = trace_id
        self.date_created = datetime.now() # Sets the date/time record is created

    def to_dict(self):
        """ Dictionary Representation of a heart rate reading """
        dict = {}
        dict['id'] = self.id
        dict['device_id'] = self.device_id
        dict['home_room'] = self.home_room
        dict['energy_use'] = self.energy_use
        dict['timestamp_start'] = self.timestamp_start
        dict['timestamp_end'] = self.timestamp_end
        dict['trace_id'] = self.trace_id
        dict['date_created'] = self.date_created

        return dict
