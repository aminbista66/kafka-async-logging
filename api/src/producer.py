from confluent_kafka import SerializingProducer, Message
from confluent_kafka.error import KafkaError
import os
import socket
import json
from uuid import uuid4
import logging

logging.basicConfig(
    level=logging.INFO,
    filename="callback.log",
    filemode="a",
    datefmt='%H:%M:%S',
    format="%(asctime)s %(levelname)s %(message)s",
)


class LogProducer:
    producer: SerializingProducer
    topic_name: str | None

    def __init__(self):
        self.topic_name = os.environ.get("KAFKA_TOPIC_NAME")
        self.producer = SerializingProducer(
            {
                "bootstrap.servers": os.environ.get("KAFKA_CLUSTER_SERVER"),
                "security.protocol": "SASL_SSL",
                "sasl.mechanism": "PLAIN",
                "sasl.username": os.environ.get("KAFKA_CLUSTER_USERNAME"),
                "sasl.password": os.environ.get("KAFKA_CLUSTER_SECRET"),
                "client.id": socket.gethostname(),
            }
        )

    def serailize_data(self, data):
        return json.dumps(data)

    def delivery_callback(self, err: KafkaError | None, msg: Message):
        if err:
            logging.error("ERROR: Message failed delivery: {}".format(err))
        else:
            logging.info(
                "Produced event to topic {topic}: key = {key} value = {value}".format(
                    topic=msg.topic(), key=msg.key(), value=msg.value()
                )
            )

    def emit_event(self, data: dict):
        if not self.topic_name:
            raise Exception("set KAFKA_TOPIC_NAME in .env")

        event_id = str(uuid4())
        data["event_id"] = event_id

        self.producer.produce(
            topic=self.topic_name,
            key=event_id,
            value=self.serailize_data(data),
            on_delivery=self.delivery_callback,
        )

        self.producer.poll(timeout=1)
