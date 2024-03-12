from confluent_kafka import SerializingProducer
import socket
from uuid import uuid4
from confluent_kafka import Message
from confluent_kafka.error import KafkaError

conf = {
    "bootstrap.servers": "pkc-ldvr1.asia-southeast1.gcp.confluent.cloud:9092",
    "security.protocol": "SASL_SSL",
    "sasl.mechanism": "PLAIN",
    "sasl.username": "OG362J7OGGVVECVX",
    "sasl.password": "6slPa2d9o1KkOBNE8WHX4BZDc+vGr8voO2bCp/RvcHRKB/tROMUK7Gf/YKIJvdyi",
    "client.id": socket.gethostname(),
}

producer = SerializingProducer(conf)


logs = [
    "created user",
    "added to inventory",
    "deleted product"
]

def delivery_callback(err: KafkaError | None, msg: Message):
    if err:
        print('ERROR: Message failed delivery: {}'.format(err))
    else:
        print("Produced event to topic {topic}: key = {key:12} value = {value:12}".format(
            topic=msg.topic(), key=msg.key(), value=msg.value()))

for log in logs:
    producer.produce(
        topic="log_topic",
        value=log,
        key=str(uuid4()),
        on_delivery=delivery_callback,
    )
producer.poll(timeout=1)
