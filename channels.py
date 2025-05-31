"""
Run simulation and calculation for different channels number  
and plot the wait time averages for both calculation and simulation.
"""
import os

import numpy as np
from run_one_calc_vs_sim import (calc_moments_by_mean_and_coev,
                                 run_calculation, run_simulation)
from utils import calc_rel_error_percent, plot_w1, plot_w1_errors


def run_channels(qp, save_path: str = None):
    """
    Run simulation and calculation for different number of channels and plot the results.
    """
    channels = np.arange(qp['channels']['min'], qp['channels']['max'] + 1)

    w1_num = []
    w1_sim = []
    w1_rel_errors = []

    total_num_time = 0
    total_sim_time = 0

    b_w = calc_moments_by_mean_and_coev(
        qp['warmup']['mean']['base'], qp['warmup']['cv']['base'])
    b_c = calc_moments_by_mean_and_coev(
        qp['cooling']['mean']['base'], qp['cooling']['cv']['base'])
    b_d = calc_moments_by_mean_and_coev(
        qp['delay']['mean']['base'], qp['delay']['cv']['base'])

    for n in channels:
        print(f"Start {n} channels...")
        service_mean = n*qp['utilization']['base']/qp['arrival_rate']

        b = calc_moments_by_mean_and_coev(
            service_mean, qp['service']['cv']['base'])

        num_results = run_calculation(
            arrival_rate=qp['arrival_rate'], num_channels=n, b=b, b_w=b_w, b_c=b_c, b_d=b_d)
        sim_results = run_simulation(
            arrival_rate=qp['arrival_rate'], num_channels=n, b=b, b_w=b_w, b_c=b_c, b_d=b_d,
            num_of_jobs=qp['jobs_per_sim'], ave_num=qp['sim_to_average'])

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
