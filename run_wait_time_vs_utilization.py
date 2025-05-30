"""
Run simulation and calculation for different utilizations factor 
and plot the wait time averages for both calculation and simulation.
"""
import os

import numpy as np

from base_parameters import QUEUE_PARAMETERS as qp
from run_one_calc_vs_sim import (
    calc_moments_by_mean_and_coev,
    run_calculation,
    run_simulation,
)
from utils import calc_rel_error_percent, plot_w1, plot_w1_errors


def run_wait_time_vs_utilization(utilization_min: float = 0.1,
                                 utilization_max: float = 0.9,
                                 num_points: int = 20, save_path: str = None):
    """
    Run simulation and calculation for different utilizations and plot the results.
    """
    rhoes = np.linspace(utilization_min, utilization_max, num_points)

    w1_num = []
    w1_sim = []
    w1_rel_errors = []

    total_num_time = 0
    total_sim_time = 0

    b_w = calc_moments_by_mean_and_coev(
        qp['warmup']['mean'], qp['warmup']['cv'])
    b_c = calc_moments_by_mean_and_coev(
        qp['cooling']['mean'], qp['cooling']['cv'])
    b_d = calc_moments_by_mean_and_coev(qp['delay']['mean'], qp['delay']['cv'])

    for rho_num, rho in enumerate(rhoes):
        print(
            f"Start {rho_num + 1}/{len(rhoes)} with utilization={rho:0.3f}... ")

        service_mean = qp['channels']*rho/qp['arrival_rate']

        b = calc_moments_by_mean_and_coev(service_mean, qp['service']['cv'])

        num_results = run_calculation(
            arrival_rate=qp['arrival_rate'], num_channels=qp['channels'], b=b, b_w=b_w, b_c=b_c, b_d=b_d)
        sim_results = run_simulation(
            arrival_rate=qp['arrival_rate'], num_channels=qp['channels'], b=b, b_w=b_w, b_c=b_c, b_d=b_d,
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
        w1_save_path = os.path.join(save_path, 'w1_vs_utilization.png')
        plot_w1(rhoes, w1_num, w1_sim, save_path=w1_save_path,
                x_label=r"$\rho$", is_xs_int=False)

        w1_errors_save_path = os.path.join(
            save_path, 'w1_errors_vs_utilization.png')
        plot_w1_errors(rhoes, w1_rel_errors, save_path=w1_errors_save_path,
                       x_label=r"$\rho$", is_xs_int=False)

    return rhoes, w1_num, w1_sim, w1_rel_errors


if __name__ == "__main__":

    # cur file dir
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    results_path = os.path.join(cur_dir, 'results')
    if not os.path.exists(results_path):
        os.makedirs(results_path)

    run_wait_time_vs_utilization(save_path=results_path)
