import requests
from requests.exceptions import Timeout, ConnectionError
import logging
import logging.config
import json
import os
import yaml
import connexion
from connexion import NoContent
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

RECEIVER_URL = app_config['service']['RECEIVER_URL']
STORAGE_URL = app_config['service']['STORAGE_URL']
PROCESSING_URL = app_config['service']['PROCESSING_URL']
ANALYZER_URL = app_config['service']['ANALYZER_URL']
TIMEOUT = app_config['params']['TIMEOUT']

# ---------------------------------------------------------------- #
# Periodic Function
# ---------------------------------------------------------------- #
def check_services():
    receiver_status = "Unavailable"
    try:
        response = requests.get(RECEIVER_URL, timeout=TIMEOUT)
        if response.status_code == 200:
            receiver_status = "Healthy"
            logger.info("Receiver is Healthy")
        else:
            logger.info("Receiver returning non-200 response")
    except(Timeout, ConnectionError):
        logger.info("Receiver is Not Available")
        
    try:
        response = requests.get(STORAGE_URL, timeout=TIMEOUT)
        if response.status_code == 200:
            storage_json = response.json()
            storage_status = f"Storage has {storage_json['num_ec_readings']} Energy Readings and {storage_json['num_temp_readings']} Temperature readings"
            logger.info("Storage is Healthy")
        else:
            logger.info("Storage returning non-200 response")
    except(Timeout, ConnectionError):
        logger.info("Storage is Not Available")
        
    try:
        response = requests.get(PROCESSING_URL, timeout=TIMEOUT)
        if response.status_code == 200:
            processing_json = response.json()
            processing_status = f"Processing has {processing_json['num_ec_readings']} Energy Readings and {processing_json['num_temp_readings']} Temperature readings"
            logger.info("Processing is Healthy")
        else:
            logger.info("Processing returning non-200 response")
    except(Timeout, ConnectionError):
        logger.info("Processing is Not Available")
        
    try:
        response = requests.get(ANALYZER_URL, timeout=TIMEOUT)
        if response.status_code == 200:
            analyzer_json = response.json()
            analyzer_status = f"Analyzer has {analyzer_json['num_ec_readings']} Energy Readings and {analyzer_json['num_temp_readings']} Temperature readings"
            logger.info("Analyzer is Healthy")
        else:
            logger.info("Analyzer returning non-200 response")
    except(Timeout, ConnectionError):
        logger.info("Analyzer is Not Available")
        
    response = {"receiver": receiver_status, "storage": storage_status, "processing": processing_status, "analyzer": analyzer_status}

    with open('status.json', 'w') as json_file:
        json.dump(response, json_file, indent=4)
    logger.debug(response)
    return

# ---------------------------------------------------------------- #
# Get
# ---------------------------------------------------------------- #
def get_checks():
    logger.info("Get request has started")
    try:
        with open('status.json', 'r') as data:
            stats = json.load(data)
            logger.debug(f"Stats: \n{stats}")
            code = 200
        logger.info("successfully opened data.json")
    except FileNotFoundError:
        logger.info("File not found")
        stats = {"Error": "File not found"}
        code = 404
    return stats, code

# ---------------------------------------------------------------- #
# Scheduler
# ---------------------------------------------------------------- #
def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(check_services,
        'interval',
        seconds=12)
    sched.start()

# ---------------------------------------------------------------- #
# App run
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
    app.run(port=8130, host="0.0.0.0")  