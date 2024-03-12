from dotenv import find_dotenv, load_dotenv
from consumer import LogConsumer

if __name__ == "__main__":
    load_dotenv(find_dotenv())
    consumer = LogConsumer()
    consumer.run()