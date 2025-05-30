"""
Run simulation and calculation for different cooling delay mean times, 
cooling delay coefficient of variation, 
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
from utils import calc_rel_error_percent, plot_probs, plot_w1, plot_w1_errors


def run_wait_time_vs_cool_delay_average(cool_min: float = 1.0, cool_max: float = 5.0,
                                        num_points: int = 20, save_path: str = None):
    """
    Run simulation and calculation for different cooling delay mean times
    """
    cools = np.linspace(cool_min, cool_max, num_points)

    w1_num = []
    w1_sim = []

    cool_probs_num = []
    cool_probs_sim = []

    total_num_time = 0
    total_sim_time = 0

    w1_rel_errors = []

    service_mean = qp['channels']*qp['utilization']/qp['arrival_rate']

    b = calc_moments_by_mean_and_coev(service_mean, qp['service']['cv'])

    b_w = calc_moments_by_mean_and_coev(
        qp['warmup']['mean'], qp['warmup']['cv'])
    b_c = calc_moments_by_mean_and_coev(
        qp['cooling']['mean'], qp['cooling']['cv'])

    for cool_num, cool_ave in enumerate(cools):
        print(
            f"Start {cool_num + 1}/{len(cools)} with cooling delay={cool_ave:0.3f}... ")

        b_d = calc_moments_by_mean_and_coev(cool_ave, qp['delay']['cv'])

        num_results = run_calculation(
            arrival_rate=qp['arrival_rate'], num_channels=qp['channels'], b=b, b_w=b_w, b_c=b_c, b_d=b_d)
        sim_results = run_simulation(
            arrival_rate=qp['arrival_rate'], num_channels=qp['channels'], b=b, b_w=b_w, b_c=b_c, b_d=b_d,
            num_of_jobs=qp['jobs_per_sim'], ave_num=qp['sim_to_average'])

        w1_num.append(num_results["w"][0])
        w1_sim.append(sim_results["w"][0])
        w1_rel_errors.append(calc_rel_error_percent(
            sim_results["w"][0], num_results["w"][0]))

        cool_probs_num.append(num_results["cold_delay_prob"])
        cool_probs_sim.append(sim_results["cold_delay_prob"])

        total_num_time += num_results["process_time"]
        total_sim_time += sim_results["process_time"]

    # Print process time comparison
    print(f"Total process time for num: {total_num_time:.4g}")
    print(f"Total process time for sim: {total_sim_time:.4g}")

    if save_path:
        wait_time_save_path = os.path.join(
            save_path, 'w1_vs_cool_delay_ave.png')

        plot_w1(cools, w1_num, w1_sim, x_label='Cooling Delay Average',
                save_path=wait_time_save_path)

        w1_error_save_path = os.path.join(
            save_path, 'w1_error_vs_cool_delay_ave.png')

        plot_w1_errors(cools, w1_rel_errors,
                       x_label='Cooling Delay Average', save_path=w1_error_save_path)

        cool_probs_save_path = os.path.join(
            save_path, 'cooling_delay_probs_vs_cool_delay_ave.png')

        plot_probs(cools, cool_probs_num, cool_probs_sim, x_label='Cooling Delay Average',
                   save_path=cool_probs_save_path)

    return cools, w1_num, w1_sim, w1_rel_errors, cool_probs_sim, cool_probs_num


def run_wait_time_vs_cool_delay_cv(cool_cv_min: float = 0.3, cool_cv_max: float = 3.0,
                                   num_points: int = 20, save_path: str = None):
    """
    Run simulation and calculation for different cooling delay coefficient of variation
    """
    cool_cvs = np.linspace(cool_cv_min, cool_cv_max, num_points)

    w1_num = []
    w1_sim = []
    w1_rel_errors = []

    cool_probs_num = []
    cool_probs_sim = []

    total_num_time = 0
    total_sim_time = 0

    service_mean = qp['channels']*qp['utilization']/qp['arrival_rate']

    b = calc_moments_by_mean_and_coev(service_mean, qp['service']['cv'])

    b_w = calc_moments_by_mean_and_coev(
        qp['warmup']['mean'], qp['warmup']['cv'])
    b_c = calc_moments_by_mean_and_coev(
        qp['cooling']['mean'], qp['cooling']['cv'])

    for cool_num, cool_cv in enumerate(cool_cvs):
        print(
            f"Start {cool_num + 1}/{len(cool_cvs)} with cooling delay cv={cool_cv:0.3f}... ")

        b_d = calc_moments_by_mean_and_coev(qp['delay']['mean'], cool_cv)

        num_results = run_calculation(
            arrival_rate=qp['arrival_rate'], num_channels=qp['channels'], b=b, b_w=b_w, b_c=b_c, b_d=b_d)
        sim_results = run_simulation(
            arrival_rate=qp['arrival_rate'], num_channels=qp['channels'], b=b, b_w=b_w, b_c=b_c, b_d=b_d,
            num_of_jobs=qp['jobs_per_sim'], ave_num=qp['sim_to_average'])

        w1_num.append(num_results["w"][0])
        w1_sim.append(sim_results["w"][0])

        w1_rel_errors.append(calc_rel_error_percent(
            sim_results["w"][0], num_results["w"][0]))

        cool_probs_num.append(num_results["cold_delay_prob"])
        cool_probs_sim.append(sim_results["cold_delay_prob"])

        total_num_time += num_results["process_time"]
        total_sim_time += sim_results["process_time"]

    # Print process time comparison
    print(f"Total process time for num: {total_num_time:.4g}")
    print(f"Total process time for sim: {total_sim_time:.4g}")

    if save_path:
        wait_time_save_path = os.path.join(
            save_path, 'w1_vs_cool_delay_cv.png')

        plot_w1(cool_cvs, w1_num, w1_sim, x_label='Cooling Delay CV',
                save_path=wait_time_save_path)

        w1_error_save_path = os.path.join(
            save_path, 'w1_error_vs_cool_delay_cv.png')

        plot_w1_errors(cool_cvs, w1_rel_errors,
                       x_label='Cooling Delay CV', save_path=w1_error_save_path)

        cool_probs_save_path = os.path.join(
            save_path, 'cooling_delay_probs_vs_cool_delay_cv.png')

        plot_probs(cool_cvs, cool_probs_num, cool_probs_sim, x_label='Cooling Delay CV',
                   save_path=cool_probs_save_path)

    return cool_cvs, w1_num, w1_sim, w1_rel_errors, cool_probs_sim, cool_probs_num


if __name__ == "__main__":

    # cur file dir
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    results_path = os.path.join(cur_dir, 'results/delay')
    if not os.path.exists(results_path):
        os.makedirs(results_path)

    run_wait_time_vs_cool_delay_average(save_path=results_path)

    run_wait_time_vs_cool_delay_cv(save_path=results_path)
