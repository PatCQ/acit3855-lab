import connexion
from connexion import NoContent
import requests
import yaml
import logging, logging.config
import uuid
import datetime
import json
from pykafka import KafkaClient 


with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

def get_item_listing_event(index):
    hostname = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)

    logger.info("Retrieving ITEM at index %d" % index)
    try:
        current_index = 0
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            # logger.debug(f"(QUEUE TESTING {msg.offset}, {msg.value}")
            # Find the event at the index you want and
            # return code 200
            # i.e., return event, 200
            if msg['type'] == 'item':
                if current_index == index:
                    logger.info(f"Found ITEM at index {index}: {msg}")
                    event = msg['payload']
                    return event, 200
                current_index += 1
            

    except Exception as e:
        logger.debug(e)
    # logger.error("Could not find ITEM at index %d" % index)
    return { "message": "Not Found"}, 404

def get_transaction_event(index):
    hostname = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)

    logger.info("Retrieving TRANSACTION at index %d" % index)
    try:
        current_index = 0
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            # logger.debug(f"(QUEUE TESTING {msg.offset}, {msg.value}")
            # Find the event at the index you want and
            # return code 200
            # i.e., return event, 200
            
            if msg['type'] == 'transaction':
                if current_index == index:
                    logger.info(f"Found TRANSACTION at index {index}: {msg}")
                    event = msg['payload']
                    return event, 200
                current_index += 1

    except Exception as e:
        logger.debug(e)
        # logger.error("No more messages found")
    # logger.error("Could not find TRANSACTION at index %d" % index)
    return { "message": "Not Found"}, 404

def get_event_stats():
    hostname = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)

    logger.info("Retrieving STATS")
    try:
        count_item = 0
        count_transaction = 0
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            
            if msg['type'] == 'item':
                count_item += 1

            if msg['type'] == 'transaction':
                count_transaction += 1
            
            total_count = {
                'num_item': count_item,
                'num_transaction': count_transaction,
            }
            # Find the event at the index you want and
            # return code 200
            # i.e., return event, 200
        return total_count, 200


    except:
        logger.error("No more messages found")
    return { "message": "Not Found"}, 404

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == '__main__':
    app.run(port=8110)