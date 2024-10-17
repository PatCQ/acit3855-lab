import connexion
from connexion import NoContent
import yaml
import logging
import logging.config
import datetime

from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from base import Base
from energy_usage import EnergyUsage
from temperature_change import TemperatureChange
# ---------------------------------------------------------------- #
# yml files
# ---------------------------------------------------------------- #
with open('app_conf.yml', 'r') as file1:
    app_config = yaml.safe_load(file1.read())
    
with open('log_conf.yml', 'r') as file2:
    log_config = yaml.safe_load(file2.read())
    logging.config.dictConfig(log_config)
    
#logger
logger = logging.getLogger('basicLogger')

DB_ENGINE = create_engine(f"mysql+pymysql://{app_config['datastore']['user']}:{app_config['datastore']['password']}@{app_config['datastore']['hostname']}:{app_config['datastore']['port']}/{app_config['datastore']['db']}")
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)
logger.info(f"Connecting to DB. Hostname {app_config['datastore']['hostname']}, Port:{app_config['datastore']['port']}")
# ---------------------------------------------------------------- #
# Database
# ---------------------------------------------------------------- #
def energy_usage(body):
    session = DB_SESSION()
    energy = EnergyUsage(body['device_id'],
                         body['home_room'],
                         body['energy_use'],
                         body['timestamp_start'],
                         body['timestamp_end'],
                         body['trace_id'])
    
    session.add(energy)
    session.commit()
    session.close()
    logger.debug(f"Stored event energy_usage request with a trace id of {body['trace_id']}")
    
    return NoContent, 201

def temperature_change(body):
    session = DB_SESSION()
    temp = TemperatureChange(body['device_id'],
                         body['home_room'],
                         body['temperature'],
                         body['timestamp'],
                         body['trace_id'])
    
    session.add(temp)
    session.commit()
    session.close()
    logger.debug(f"Stored event temperature_change request with a trace id of {body['trace_id']}")
    
    return NoContent, 201
# ---------------------------------------------------------------- #
# Get
# ---------------------------------------------------------------- #
def get_energy_usage_readings(start_timestamp, end_timestamp):
    """ Gets new energy usage readings between the start and end timestamps """
    session = DB_SESSION()
    
    start_timestamp_datetime = datetime.datetime.strptime(start_timestamp, "%Y-%m-%d %H:%M:%S.%f")
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%d %H:%M:%S.%f")
    logger.debug(f"{start_timestamp_datetime} energy")
    logger.debug(f"{end_timestamp_datetime} energy")
    results = session.query(EnergyUsage).filter(
        and_(
            EnergyUsage.date_created >= start_timestamp_datetime, 
            EnergyUsage.date_created < end_timestamp_datetime
            )
        )
    
    results_list = []
    
    for reading in results:
        results_list.append(reading.to_dict())
    
    session.close()
    logger.info("Query for energy usage readings after %s returns %d results" %
    (start_timestamp, len(results_list)))
    return results_list, 200

def get_temperature_change_readings(start_timestamp, end_timestamp):
    """ Gets new temperature change readings between the start and end timestamps """
    session = DB_SESSION()
    
    start_timestamp_datetime = datetime.datetime.strptime(start_timestamp, "%Y-%m-%d %H:%M:%S.%f")
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%d %H:%M:%S.%f")
    logger.debug(f"{start_timestamp_datetime} temp")
    logger.debug(f"{end_timestamp_datetime} temp")
    results = session.query(TemperatureChange).filter(
        and_(
            TemperatureChange.date_created >= start_timestamp_datetime, 
            TemperatureChange.date_created < end_timestamp_datetime
            )
        )
    
    results_list = []
    
    for reading in results:
        results_list.append(reading.to_dict())
    
    session.close()
    logger.info("Query for temperature change readings after %s returns %d results" %
    (start_timestamp, len(results_list)))
    return results_list, 200
# ---------------------------------------------------------------- #

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api('openapi.yaml', strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8090)  
