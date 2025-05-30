# Numerical Calculation of Multichannel Queues with Warm-Up, Cooling and Delay in Cooling Start

## Overview
This repository contains numerical calculations and simulation code for multichannel queue systems with:
- Vacation periods (warm-up, cooling)
- Delayed cooling start
- Different service time distributions

## Abstract: 

A method is proposed for obtaining probabilities of states, initial moments of waiting and sojourn times of applications in a multi-channel queueing system with hyperexponential service times, warm-up, cooling, and delay before cooling starts. The parameters of the hyperexponential distribution are generally complex, which allows setting arbitrary variation coefficients of the specified distributions (including less than one). Numerical calculation results are presented in comparison with simulation modeling results, confirming the high accuracy and correctness of the proposed solution. 

## Paper Reference

[PDF](https://doi.org/10.25791/aviakosmos.1.2025.1456) | [DOI](https://doi.org/10.25791/aviakosmos.1.2025.1456)


## Requirements
- Python 3.8+
- Dependencies in `requirements.txt`

## Installation
```bash
git clone https://github.com/username/repo.git
cd repo
pip install -r requirements.txt
```

## Usage

### Main Scripts

#### Compare Calculations vs Simulations
```bash
python run_one_calc_vs_sim.py 
```

#### Waiting Time Analysis
:chart: Analyze system performance with:
- `run_wait_time_vs_utilization.py` by utilization factor
- `run_wait_time_vs_channels.py` by number of channels
- `run_wait_time_vs_service_cv.py` by service time CV
- `run_wait_time_vs_warmup_time.py` by warm-up time parameters
- `run_wait_time_vs_cooling_time.py` by cooling time parameters
- `run_wait_time_vs_cooling_delay_time.py` by cooling delay parameters

## Results

:chart: Visualizations and quantitative results in [results/](results/) directory.

## Contributing

1. Fork repository :git:
2. Create issue before changes
3. Pull requests welcome!

## Issues

Report bugs, request features or ask questions in [Issues](https://github.com/xabarov/queue_with_vacations/issues).

## License

[MIT License](LICENSE)

## Related Repositories

:link: Check out related projects:
- [Queueing Systems: Simulation & Numerical Methods](https://github.com/xabarov/most-queue)