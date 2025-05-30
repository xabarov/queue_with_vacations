"""
Run simulation and calculation for different channels number  
and plot the wait time averages for both calculation and simulation.
"""
import os

import numpy as np
from run_one_calc_vs_sim import (calc_moments_by_mean_and_coev,
                                 run_calculation, run_simulation)
from utils import calc_rel_error_percent, plot_w1, plot_w1_errors

ARRIVAL_RATE = 1.0

SERVICE_TIME_CV = 1.2

WARM_UP_TIME_MEAN = 2.0
WARM_UP_TIME_CV = 0.87

COOL_TIME_MEAN = 2.0
COOL_TIME_CV = 1.2

COOL_DELAY_MEAN = 2.0
COOL_DELAY_CV = 1.4

UTILIZATION = 0.7

NUM_OF_JOBS_PER_SIM = 300_000  # Number of jobs per simulation
NUM_OF_SIM_TO_AVERAGE = 10  # Number of simulations to average over


def run_wait_time_vs_channels_num(channels_min: int = 1, channels_max: int = 10,
                                  save_path: str = None):
    """
    Run simulation and calculation for different number of channels and plot the results.
    """
    channels = np.arange(channels_min, channels_max + 1)

    w1_num = []
    w1_sim = []
    w1_rel_errors = []

    total_num_time = 0
    total_sim_time = 0

    b_w = calc_moments_by_mean_and_coev(WARM_UP_TIME_MEAN, WARM_UP_TIME_CV)
    b_c = calc_moments_by_mean_and_coev(COOL_TIME_MEAN, COOL_TIME_CV)
    b_d = calc_moments_by_mean_and_coev(COOL_DELAY_MEAN, COOL_DELAY_CV)

    for n in channels:
        print(f"Start {n} channels...")
        service_mean = n*UTILIZATION/ARRIVAL_RATE

        b = calc_moments_by_mean_and_coev(service_mean, SERVICE_TIME_CV)

        num_results = run_calculation(
            arrival_rate=ARRIVAL_RATE, num_channels=n, b=b, b_w=b_w, b_c=b_c, b_d=b_d)
        sim_results = run_simulation(
            arrival_rate=ARRIVAL_RATE, num_channels=n, b=b, b_w=b_w, b_c=b_c, b_d=b_d,
            num_of_jobs=NUM_OF_JOBS_PER_SIM, ave_num=NUM_OF_SIM_TO_AVERAGE)

        w1_num.append(num_results["w"][0])
        w1_sim.append(sim_results["w"][0])

        w1_rel_errors.append(calc_rel_error_percent(
            sim_results["w"][0], num_results["w"][0]))

        total_num_time += num_results["process_time"]
        total_sim_time += sim_results["process_time"]

    # Print process time comparison
    print(f"Total process time for num: {total_num_time:.4g}")
    print(f"Total process time for sim: {total_sim_time:.4g}")

    if save_path:
        w1_save_path = os.path.join(save_path, 'w1_vs_channels.png')
        plot_w1(channels, w1_num, w1_sim, save_path=w1_save_path,
                x_label="Number of Channels", is_xs_int=True)

        w1_errors_save_path = os.path.join(
            save_path, 'w1_errors_vs_channels.png')
        plot_w1_errors(channels, w1_rel_errors, save_path=w1_errors_save_path,
                       x_label="Number of Channels", is_xs_int=True)

    return channels, w1_num, w1_sim, w1_rel_errors


if __name__ == "__main__":

    # cur file dir
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    results_path = os.path.join(cur_dir, 'results')
    if not os.path.exists(results_path):
        os.makedirs(results_path)

    run_wait_time_vs_channels_num(save_path=results_path)
