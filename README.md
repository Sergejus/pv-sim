# PV Simulator

PV simulator with meter simulator and RabbitMQ message broker in between.

The simulator code is written using python 3.8 (those debug f-strings are just too good not to use ;) )

---

## Preparing to run the project

Clone the project

```bash
git clone git@github.com:Sergejus/pv-sim.git
```

Navigate to project root folder

```bash
cd pv-sim
```

---

## Run with Docker

Easiest way to run this is using `docker` and `docker-compose`.

[Install Docker](https://docs.docker.com/engine/install/)

[Install Docker Compose](https://docs.docker.com/compose/install/)

### Run

Build and start docker containers with the following command:

```bash
docker-compose up -d --build
```

You should see the containers start and run for a few seconds.
Meter and PV Simulator containers will run and stop automatically once the simulation is done.

This command shows which containers are still running:

```bash
docker ps
```

Stop the remaining container (RabbitMQ container is still running after the simulation is complete)

```bash
docker-compose down
```

---

## Run manually on Debian/Ubuntu Linux

Install Python 3.8.

Install and run RabbitMQ server:

[Install RabbitMQ](https://www.rabbitmq.com/install-debian.html)

It is a good practice to run the python project in virtualenv.

Navigate to project root folder.

Create a python 3.8 virtualenv:

```bash
python3 -m venv venv
```

Activate the virtualenv

```bash
source venv/bin/activate
```

Install the requirements to run the project.
The only mandatory prerequisite for this project to work is `pika` library :)

```bash
pip3 install -r requirements.txt
```

Run `pv_simulator` consumer. It will start and wait for meter values. 

```bash
python3 pv/pv_simulator.py -s localhost -p 5672 -o data/results.csv
```

Run `meter` producer to start the simulation.

```bash
python3 meter/meter.py -s localhost -p 5672
```

You can add `-d` option to both `pv_simulator` and/or `meter` to see debug messages.

The `pv_simulator` and `meter` will run for a few seconds to simulate the full 24 hours of household and PV power data.

---

## Results and plots

After running the simulator the results will appear in the `data` folder.
There is also a script to plot the results of the simulation.

The plot script depends on `matplotlib` and `pandas`, hence they should be installed first:

```bash
pip3 install matplotlib pandas
```

To plot the results run the following:

```bash
python3 data/plot_results.py data/results.csv
```

This will produce `data/results.png` and show an interactive plot.

If the plot does not appear, try to install PyQt5 for matplotlib:

```bash
pip3 install pyqt5
```

<!-- ![results.png](data/results.png "results.png") -->

---

## Notes

PV simulator depends on the meter simulator to generate the timestamps for the simulation.

Meter values of the household consumption, in reality, are not completely random as they typically follow a consumption pattern.
The pattern is a combination of multiple cyclic load patterns, from always on (fridge, AC, heater, etc.) and manually operated (stove/oven, kettle, lights, vacuum cleaner) appliances.

PV values from the example graph clearly show a slightly skewed production curve.
The curve could be modeled as a normal distribution or a Weibull distribution.
However, to reduce complexity and match the curve as closely as possible a quadratic model with two linear extensions is chosen.
 
## Author

**Sergejus Martinenas**

- [github/sergejus](https://github.com/sergejus)
- [linkedin/sergejusm](https://www.linkedin.com/in/sergejusm/)
