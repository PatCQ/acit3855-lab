from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql.functions import now
from base import Base
from datetime import datetime


class TemperatureChange(Base):
    """ Temperature change """

    __tablename__ = "temperature_change"

    id = Column(Integer, primary_key=True)
    device_id = Column(String(250), nullable=False)
    home_room = Column(String(250), nullable=False)
    temperature = Column(Integer, nullable=False)
    timestamp = Column(String(250), nullable=False)
    trace_id = Column(String(250), nullable=False)
    date_created = Column(DateTime, nullable=False)

    def __init__(self, device_id, home_room, temperature, timestamp, trace_id):
        """ Initializes a heart rate reading """
        self.device_id = device_id
        self.home_room = home_room
        self.temperature = temperature
        self.timestamp = timestamp
        self.trace_id = trace_id
        self.date_created = datetime.now() # Sets the date/time record is created

    def to_dict(self):
        """ Dictionary Representation of a heart rate reading """
        dict = {}
        dict['id'] = self.id
        dict['device_id'] = self.device_id
        dict['home_room'] = self.home_room
        dict['temperature'] = self.temperature
        dict['timestamp'] = self.timestamp
        dict['trace_id'] = self.trace_id
        dict['date_created'] = self.date_created

        return dict
