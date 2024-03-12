from confluent_kafka import Consumer, Message
import os
from confluent_kafka.error import KafkaError, KafkaException
import sys
from redis import Redis
import json
from typing import Union


class LogConsumer:
    consumer: Consumer
    topics: list[str]
    redis: Redis

    def __init__(self) -> None:
        if not os.environ.get("KAFKA_TOPIC_NAME"):
            raise Exception("set KAFKA_TOPIC_NAME in your .env")
        self.topics = [os.environ.get("KAFKA_TOPIC_NAME", "log_topic")]

        self.consumer = Consumer(
            {
                "bootstrap.servers": os.environ.get("KAFKA_CLUSTER_SERVER"),
                "bootstrap.servers": os.environ.get("KAFKA_CLUSTER_SERVER"),
                "security.protocol": "SASL_SSL",
                "sasl.mechanism": "PLAIN",
                "sasl.username": os.environ.get("KAFKA_CLUSTER_USERNAME"),
                "sasl.password": os.environ.get("KAFKA_CLUSTER_SECRET"),
                "group.id": os.environ.get("KAFKA_CONSUMER_GUID"),
                "auto.offset.reset": "earliest",
            }
        )

        self.redis = Redis(
            host=os.environ.get("REDIS_HOST", "localhost"),
            port=int(os.environ.get("REDIS_PORT", 6379)),
            decode_responses=True,
            db=0,
        )

    def serialize_message(self, message: Union[str, bytes]):
        if isinstance(message, str):
            data = json.loads(message)
        elif isinstance(message, bytes):
            data = json.loads(message.decode("utf-8"))
        else:
            raise TypeError("message must be either a string or bytes")
        return data

    def save_to_redis(self, message: Union[str, bytes]):
        response = self.redis.get("logs")
        data = self.serialize_message(message)
        if not response:

            self.redis.set("logs", json.dumps([data]).encode("utf-8"))
        else:
            logs: list = json.loads(response)  # type: ignore
            logs.append(data)
            self.redis.set(name="logs", value=json.dumps(logs).encode(), ex=60*5)

    def run(self):
        try:
            self.consumer.subscribe(topics=self.topics)
            print("Subcribed to topic: {} listening....".format(self.topics))

            while True:
                msg: Message | None = self.consumer.poll(timeout=1.0)
                if msg is None:
                    continue

                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:  # type:ignore
                        # End of partition event
                        sys.stderr.write(
                            "%% %s [%d] reached end at offset %d\n"
                            % (msg.topic(), msg.partition(), msg.offset())
                        )
                    elif msg.error():
                        raise KafkaException(msg.error())
                else:
                    self.consumer.commit(asynchronous=False)
                    print(
                        "Consumed message: value={value}, key={key}".format(
                            value=msg.value().decode("utf-8"),  # type:ignore
                            key=msg.key().decode("utf-8"),  # type:ignore
                        )
                    )
                    # save log payload to redis
                    self.save_to_redis(msg.value().decode("utf-8"))  # type:ignore

        except KeyboardInterrupt:
            print("exitting...")
        finally:
            # Close down consumer to commit final offsets.
            print("closing consumer...")
            self.consumer.close()
