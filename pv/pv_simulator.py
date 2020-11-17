#!/usr/bin/python

import pika

import json
import csv

import argparse
import logging

import random

from time import sleep
import datetime
from datetime import timedelta, datetime as dt


logger = logging.getLogger("pv_sim")
logger.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(ch)


# Simulation time constants hours from midnight
SUNRISE_TIME = 5.4
# time point where power curve changes from linear to quadratic
MORNING_POINT = 8
# time point where power curve changes from quadratic back to linear before sunset
EVENING_POINT = 20
SUNSET_TIME = 20.8


class PVSimulator(object):
    """
    PV Simulator class
    """

    def __init__(self, host="localhost", port=5672, output_filename='output.csv'):
        # Init the RabbitMQ connection
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=host, port=port))
        self.channel = connection.channel()
        self.channel.queue_declare(queue="meter")

        logger.info(
            f"PV Simulator consumer connected to RabbitMQ broker {host=}, {port=}")

        self.filename = output_filename

        # Open and clean the file from previous simulation
        with open(self.filename, 'w'):
            pass

    def callback(self, ch, method, properties, body):
        logger.debug(f"Received: {body}")

        meter_dict = json.loads(body)

        # Check if dict is empty
        if len(meter_dict) == 0:
            # Empty dict indicates last producer message -> close the channel stop consumer
            logger.debug("Meter value data stream end received")
            sleep(1)
            self.channel.close()
            logger.info("PV Simulation complete")
        else:
            # Process received message
            meter_power = meter_dict["val"]
            meter_timestamp = meter_dict["time"]
            # Convert simulation time in seconds to ISO datetime of today
            iso_timestamp = dt.isoformat(dt.combine(
                dt.date(dt.today()), datetime.time()) + timedelta(seconds=meter_timestamp))
            pv_power = self.get_pv_power(meter_timestamp)
            sum_power = meter_power - pv_power

            result_dict = {
                'timestamp': iso_timestamp,
                'meter_power': meter_power,
                'pv_power': pv_power,
                'sum_power': sum_power
            }

            self.write_csv(self.filename, result_dict)

    def run(self):
        # Run PV simulator
        try:
            self.channel.basic_consume(
            queue="meter", on_message_callback=self.callback, auto_ack=True)

            logger.debug("Waiting for meter values...")
            self.channel.start_consuming()
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        finally:
            self.channel.close()
        

    def get_pv_power(self, timestamp):
        # Function to generate the PV power value from the timestamp as input
        x = timestamp/3600
        pv_power = 0

        # PV power curve is modelled as a quadratic curve with two linear additions for simplicity
        if x >= SUNRISE_TIME and x < SUNSET_TIME:
            if x < MORNING_POINT:
                pv_power = 96 * x - 520
            elif x > EVENING_POINT:
                pv_power = -531 * x + 11050
            else:
                # TODO: improve the randomness in the pv_power to be most pronounced at peak power e.g. use quadratic multiplier for random element
                pv_power = -13033.3 + 2318.75 * x - \
                    82.29 * x**2 + random.uniform(-20, 20)

        return pv_power

    def write_csv(self, filename, data_dict):
        with open(filename, 'a', newline='') as csvfile:
            fieldnames = ['timestamp', 'meter_power', 'pv_power', 'sum_power']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if csvfile.tell() == 0:
                writer.writeheader()
            writer.writerow(data_dict)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="PV simulator")
    ap.add_argument("-s", "--host", default="localhost",
                    help="rabbitMQ host, defaults to localhost")
    ap.add_argument("-p", "--port", type=int, default=5672,
                    help="rabbitMQ port, defaults to 5672")
    ap.add_argument("-o", "--output", default="results.csv",
                    help="output CSV file name, defaults to results.csv")
    ap.add_argument('-d', '--debug', help="Enable debug logs", action="store_const",
                    dest="loglevel", const=logging.DEBUG, default=logging.INFO)
    args = ap.parse_args()

    logger.setLevel(level=args.loglevel)

    pv_sim = PVSimulator(host=args.host, port=args.port,
                         output_filename=args.output)
    pv_sim.run()
