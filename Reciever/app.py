import connexion
from connexion import NoContent
import requests
import yaml
import logging
import logging.config
import uuid

#load yml files
with open('app_conf.yml', 'r') as file1:
    app_config = yaml.safe_load(file1.read())



with open('log_conf.yml', 'r') as file2:
    log_config = yaml.safe_load(file2.read())
    logging.config.dictConfig(log_config)
    
#create logger?
logger = logging.getLogger('basicLogger')
    
def update_event(event, data):
    headers = {'Content-Type': 'application/json'}
    response = requests.post(event, json=data, headers=headers)
    return NoContent, response.status_code

# Your functions here
def energy_usage(body):
    trace_id = str(uuid.uuid4())
    body['trace_id'] = trace_id
    if body:
        status_code = 201
        response = {'message': 'Event created successfully'}
        
        
        logger.info(f"Received event energy_usage request with a trace id of {body['trace_id']}")
        update_event(app_config['eventstore1']['url'], body)
        logger.info(f"Returned event energy_usage response (ID: {body['trace_id']}) with status {status_code}")
    else:
        status_code = 400
        response = {'message': 'Failed to create event'}
        logger.error(f"Failed to process event energy_usage with a trace id of {body['trace_id']}. status code: {status_code}")
        
    return response, status_code
    # return NoContent, 201

def temperature_change(body):
    trace_id = str(uuid.uuid4())
    body['trace_id'] = trace_id
    if body:
        status_code = 201
        response = {'message': 'Event created successfully'}
        
        
        logger.info(f"Received event temperature_change request with a trace id of {body['trace_id']}")
        update_event(app_config['eventstore2']['url'], body)
        logger.info(f"Returned event temperature_change response (ID: {body['trace_id']}) with status {status_code}")
    else:
        status_code = 400
        response = {'message': 'Failed to create event'}
        logger.error(f"Failed to process event temperature_change with a trace id of {body['trace_id']}. status code: {status_code}")
        
    return response, status_code


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api('openapi.yml', strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8080)  
