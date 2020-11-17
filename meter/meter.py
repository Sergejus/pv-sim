#!/usr/bin/python

import pika

import random

from time import sleep
from datetime import datetime as dt

import json
import argparse
import logging

logger = logging.getLogger("meter")
logger.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(ch)


# Constants for meter sim
MAX_POWER = 9000  # [W]

START_TIME = 0  # [s]
END_TIME = 24*60*60  # [s] 24Hours in seconds
TIME_STEP = 5  # [s] sample interval


class Meter(object):
    """
    Meter simulator class
    """

    def __init__(self, host="localhost", port=5672):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=host, port=port))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue="meter")
        logger.info(
            f"Meter producer connected to RabbitMQ broker {host=}, {port=}")

    def run(self):
        """
        Run the meter simulation
        """
        try:
            for t in range(START_TIME, END_TIME, TIME_STEP):
                # TODO: make random values a bit more realistic with cyclic patterns
                meter_value = random.uniform(0, MAX_POWER)
                meter_data = {"time": t, "val": meter_value}

                self.channel.basic_publish(
                    exchange="",
                    routing_key="meter",
                    body=json.dumps(meter_data)
                )

                # Show and slow down the execution in debug mode to see the progress
                logger.debug(f"Sent: {json.dumps(meter_data)}")
                if logger.level == logging.DEBUG:
                    sleep(0.001)

        except KeyboardInterrupt:
            pass

        finally:
            # Send "simulation done" message as empty dict to consumers
            logger.info("Meter value simulation complete")
            logger.debug("Sending end simulation message")
            self.channel.basic_publish(
                exchange="",
                routing_key="meter",
                body=json.dumps({}),
                properties=pika.BasicProperties(
                         delivery_mode=2,  # make message persistent
                ))
            logger.debug("Closing RabbitMQ connection")
            self.connection.close()


if __name__ == "__main__":

    ap = argparse.ArgumentParser(description="Meter simulator")
    ap.add_argument("-s", "--host", default="localhost",
                    help="rabbitMQ host, defaults to localhost")
    ap.add_argument("-p", "--port", type=int, default=5672,
                    help="rabbitMQ port, defaults to 5672")
    ap.add_argument('-d', '--debug', help="Enable debug logs", action="store_const",
                    dest="loglevel", const=logging.DEBUG, default=logging.INFO)
    args = ap.parse_args()

    logger.setLevel(level=args.loglevel)

    meter = Meter(host=args.host, port=args.port)
    meter.run()
