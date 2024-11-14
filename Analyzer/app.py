import connexion
import yaml
import logging
import logging.config
import json
from pykafka import KafkaClient
from connexion.middleware import MiddlewarePosition
from starlette.middleware.cors import CORSMiddleware
# -------------------------------------------------------------------------------- #
# yml
# -------------------------------------------------------------------------------- #
with open('app_conf.yml', 'r') as file1:
    app_config = yaml.safe_load(file1.read())

with open('log_conf.yml', 'r') as file2:
    log_config = yaml.safe_load(file2.read())
    logging.config.dictConfig(log_config)

# -------------------------------------------------------------------------------- #
# Logger
# -------------------------------------------------------------------------------- #
logger = logging.getLogger('basicLogger')

# -------------------------------------------------------------------------------- #
# Get
# -------------------------------------------------------------------------------- #
def get_energy_reading(index):
    hostname = "%s:%d" % (app_config["events"]["hostname"],
                          app_config["events"]["port"])
    client = KafkaClient(hosts=f"{hostname}")
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)
    
    logger.info("Retrieving energy at index %d" % index)
    
    try:
        search_index = 0
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            logger.debug(f"Got message: {msg}")
            if msg['type'] == 'energy':
                if search_index == index:
                    logger.debug(f"Found energy via index: {index}")
                    logger.info(f"Found Energy Reading at index {index}: {msg}")
                    event = msg['payload']
                    return event, 200
                search_index += 1
                
    except Exception as e:
        logger.debug(e)

    return { "message": "Not Found"}, 404

def get_temperature_change_reading(index):
    hostname = "%s:%d" % (app_config["events"]["hostname"],
                          app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)
    
    logger.info("Retrieving temperature at index %d" % index)
    
    try:
        search_index = 0
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            
            if msg['type'] == 'temperature':
                if search_index == index:
                    logger.info(f"Found Temperature Reading at index {index}: {msg}")
                    event = msg['payload']
                    return event, 200
                search_index += 1
                
    except Exception as e:
        logger.debug(e)

    return { "message": "Not Found"}, 404

def get_event_stats():
    hostname = "%s:%d" % (app_config["events"]["hostname"],
                          app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)
    
    stats = {"num_ec_readings": 0, "num_temp_readings": 0 }
    
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)

            if msg['type'] == 'energy':
                stats["num_ec_readings"] += 1
            elif msg['type'] == 'temperature':
                stats["num_temp_readings"] += 1
        return stats, 200
    except Exception as e:
        logger.debug(e)
        
    return {"message": "Not Found"}, 404
    
# -------------------------------------------------------------------------------- #
# Connexion
# -------------------------------------------------------------------------------- #
app = connexion.FlaskApp(__name__, specification_dir='./')
app.add_api('openapi.yml')

app.add_middleware(
    CORSMiddleware,
    position=MiddlewarePosition.BEFORE_EXCEPTION,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    app.run(port=8110)  