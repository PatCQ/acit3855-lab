import connexion
from connexion import NoContent
import requests
import yaml
import logging
import logging.config
import uuid
import os
import datetime
import json
from pykafka import KafkaClient

# ---------------------------------------------------------------------------- #
# Open yml files
# ---------------------------------------------------------------------------- #
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
    
# ------------------------------------------------------------------------------ #
# Logger
# ------------------------------------------------------------------------------ #
logger = logging.getLogger('basicLogger')

logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)

# ------------------------------------------------------------------------------ #
# Kafka
# ------------------------------------------------------------------------------ #
def kafka_connection():        
    client = KafkaClient(hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}")
    topic = client.topics[str.encode(app_config['events']['topic'])]
    producer = topic.get_sync_producer()
    return(producer)

producer = kafka_connection()
# ------------------------------------------------------------------------------------------------#
# Post Events
# ------------------------------------------------------------------------------------------------#
def update_event(event, data):
    headers = {'Content-Type': 'application/json'}
    response = requests.post(event, json=data, headers=headers)
    return NoContent, response.status_code

def energy_usage(body):
    trace_id = str(uuid.uuid4())
    body['trace_id'] = trace_id
    if body:
        status_code = 201
        response = {'message': 'Event created successfully'}
        
        
        logger.info(f"Received event energy_usage request with a trace id of {body['trace_id']}")
        #update_event(app_config['eventstore1']['url'], body)
        
        msg = { "type": "energy",
                "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                "payload": body }
        msg_str = json.dumps(msg)
        producer.produce(msg_str.encode('utf-8'))
        
        logger.info(f"Returned event energy_usage response (ID: {body['trace_id']}) with status {status_code}")
    else:
        status_code = 400
        response = {'message': 'Failed to create event'}
        logger.error(f"Failed to process event energy_usage with a trace id of {body['trace_id']}. status code: {status_code}")
        
    return response, status_code

def temperature_change(body):
    trace_id = str(uuid.uuid4())
    body['trace_id'] = trace_id
    if body:
        status_code = 201
        response = {'message': 'Event created successfully'}
        
        
        logger.info(f"Received event temperature_change request with a trace id of {body['trace_id']}")
        #update_event(app_config['eventstore2']['url'], body)
        
        msg = { "type": "temperature",
                "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                "payload": body }
        msg_str = json.dumps(msg)
        producer.produce(msg_str.encode('utf-8'))
        
        logger.info(f"Returned event temperature_change response (ID: {body['trace_id']}) with status {status_code}")
    else:
        status_code = 400
        response = {'message': 'Failed to create event'}
        logger.error(f"Failed to process event temperature_change with a trace id of {body['trace_id']}. status code: {status_code}")
        
    return response, status_code

# ------------------------------------------------------------------------------------------------ #
# Get Event
# ------------------------------------------------------------------------------------------------ #
def get_check():
    return "", 200

# ------------------------------------------------------------------------------------------------ #
# Application connection
# ------------------------------------------------------------------------------------------------
app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api('openapi.yml', base_path="/receiver", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8080, host="0.0.0.0")  
