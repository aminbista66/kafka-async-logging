from confluent_kafka import Consumer, Message
import os
from confluent_kafka.error import KafkaError, KafkaException
import sys


class LogConsumer:
    consumer: Consumer
    topics: list[str]

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

    def run(self):
        try:
            self.consumer.subscribe(topics=self.topics)
            print("starting consumer....")
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
                    print(msg)
                    print(
                        "Consumed message: value={value}, key={key}".format(
                            value=msg.value(), key=msg.key()
                        )
                    )
                    # msg_process(msg)
        except KeyboardInterrupt:
            print("closing consumer...")
        finally:
            # Close down consumer to commit final offsets.
            print("closing consumer...")
            self.consumer.close()
