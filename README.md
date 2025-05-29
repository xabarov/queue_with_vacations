# NUMERICAL CALCULATION OF A MULTICHANNEL QUEUES WITH WARM-UP, COOLING AND DELAY IN THE START OF COOLING

## Overview
This project demonstrates numerical calculations for multichannel queues with vacations such as warm-up, cooling, and delay in the start of cooling. The code includes functions to run calculations based on ours method and validate the results using simulations.

## Installation
To install the required packages, run:
```bash
pip install -r requirements.txt
```
or 
```bash
pip install most-queue
```

## Run One Calculation vs Simulation

The script `run_one_calc_vs_sim.py` is used to compare numerical calculations with simulations. It takes parameters such as arrival rate, service time distribution, warmup and cooling times, number of channels, and number of jobs for the simulation.
To run the script, use:

```bash
python run_one_calc_vs_sim.py 
```

## Run waiting time average calculation vs Simulation 

### Utilization Factor

The script `run_wait_time_vs_utilization.py` is used to compare numerical calculations with simulations for different utilization factors of the queue. To run the script, use:
```bash
python run_wait_time_vs_utilization.py
```
### Channels

To run the script for a specific number of channels, use:
```bash
python run_wait_time_vs_channels.py
```

### Service Time Coefficient of Variation (CV)
The script `run_wait_time_vs_sevice_cv.py` is used to compare numerical calculations with simulations for different service time coefficients of variation. To run the script, use:

```bash
python run_wait_time_vs_service_cv.py
```


## Contributing
Contributions are welcome! Please fork the repository and submit a pull request.
You can write us to xabarov.r@yandex.ru  for any questions or feedback.

## Paper Reference
Лохвицкий, В. А. Численный расчет многоканальной системы массового обслуживания с разогревом, охлаждением и задержкой начала охлаждения / В. А. Лохвицкий, Р. С. Хабаров, Е. Л. Яковлев // Авиакосмическое приборостроение. – 2025. – № 1. – С. 44-57. – DOI 10.25791/aviakosmos.1.2025.1456. – EDN OVJXKE.
