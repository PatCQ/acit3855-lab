import connexion
from connexion import NoContent
import yaml
import logging
import logging.config
import json
import os
import requests
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from connexion.middleware import MiddlewarePosition
from starlette.middleware.cors import CORSMiddleware
# ---------------------------------------------------------------- #
# yml files & logger
# ---------------------------------------------------------------- #
if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"

with open(app_conf_file, 'r') as file1:
    app_config = yaml.safe_load(file1.read())

with open(log_conf_file, 'r') as file2:
    log_config = yaml.safe_load(file2.read())
    logging.config.dictConfig(log_config)
    
logger = logging.getLogger('basicLogger')

logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)

# ---------------------------------------------------------------- #
# Get
# ---------------------------------------------------------------- #
def get_stats():
    logger.info("Get request has started")
    current_time = datetime.now()
    try:
        with open(app_config['datastore']['filename'], 'r') as data:
            stats = json.load(data)
            logger.debug(f"Stats: \n{stats}")
            logger.info("Get request has finished")
            code = 200
        logger.info("successfully opened data.json")
    except FileNotFoundError:
        with open(app_config['datastore']['filename'], 'w') as data:
            default = {
            "num_ec_readings": 0,
            "min_ec_reading": 1000000000,
            "max_ec_reading": 0,
            "num_temp_readings": 0,
            "min_temp_reading": 1000000000,
            "max_temp_reading": 0,
            "last_updated": datetime.strftime(current_time, "%Y-%m-%d %H:%M:%S.%f")
            }
            json.dump(default, data, indent=4)
            stats = default
            code = 201
        logger.info("successfully created data.json")
    return stats, code
# ---------------------------------------------------------------- #
# Periodic Processing
# ---------------------------------------------------------------- #
def populate_stats():
    logger.info("Start Periodic Processing")
    current_time = datetime.now()
    try:
        with open(app_config['datastore']['filename'], 'r') as data:
            stats = json.load(data)
        logger.info("successfully opened data.json")
    except FileNotFoundError:
        with open(app_config['datastore']['filename'], 'w') as data:
            default = {
            "num_ec_readings": 0,
            "min_ec_reading": 1000000000,
            "max_ec_reading": 0,
            "num_temp_readings": 0,
            "min_temp_reading": 1000000000,
            "max_temp_reading": 0,
            "last_updated": datetime.strftime(current_time, "%Y-%m-%d %H:%M:%S.%f")
            }
            json.dump(default, data, indent=4)
            stats = default
        logger.info("successfully created data.json")
    query = {'start_timestamp': stats['last_updated'], 'end_timestamp': current_time}

    energy_list = requests.get(app_config['eventstore_energy']['url'], params=query)
    temp_list = requests.get(app_config['eventstore_temperature']['url'], params=query)
    
    energy_stats = energy_list.json()
    temp_stats = temp_list.json()
    logger.info(f"Received {len(energy_stats) + len(temp_stats)} events.") 
    
    if (energy_stats):
        stats["num_ec_readings"] += len(energy_stats)
        for i in energy_stats:
            if i['energy_use'] < stats["min_ec_reading"]:
                stats["min_ec_reading"] = i['energy_use']
            if i['energy_use'] > stats["max_ec_reading"]:
                stats["max_ec_reading"] = i['energy_use']
    if (temp_stats):
        stats["num_temp_readings"] += len(temp_stats)
        for i in temp_stats:
            if i['temperature'] < stats["min_temp_reading"]:
                stats["min_temp_reading"] = i['temperature']
            if i['temperature'] > stats["max_temp_reading"]:
                stats["max_temp_reading"] = i['temperature']
    else: 
        logger.error(f"Failed to retrieve events")       
    stats["last_updated"] = datetime.strftime(current_time, "%Y-%m-%d %H:%M:%S.%f")

    with open(app_config['datastore']['filename'], 'w') as data:
        json.dump(stats, data, indent=4)

        logger.debug('written events')
        
    logger.debug(f"Updated statistics: {stats}")
    logger.debug(f"{stats}")
    logger.info(f"Periodic processing has completed")
            
    return
# ---------------------------------------------------------------- #
# Scheduler
# ---------------------------------------------------------------- #
def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats,
        'interval',
        seconds=app_config['scheduler']['period_sec'])
    sched.start()
# ---------------------------------------------------------------- #
app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api('openapi.yaml', base_path="/processing", strict_validation=True, validate_responses=True)

if "TARGET_ENV" not in os.environ or os.environ["TARGET_ENV"] != "test":
    app.add_middleware(
        CORSMiddleware,
        position=MiddlewarePosition.BEFORE_EXCEPTION,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

if __name__ == "__main__":
    init_scheduler()
    app.run(port=8100, host="0.0.0.0")  
