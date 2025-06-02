"""
Find best cooling delay for a given set of parameters and utilization factor.
"""
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

from run_one_calc_vs_sim import calc_moments_by_mean_and_coev, run_calculation
from utils import read_parameters_from_yaml
from most_queue.theory.utils.weibull import Weibull

SMALL_SIZE = 12
MEDIUM_SIZE = 14
BIGGER_SIZE = 16

plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=MEDIUM_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=MEDIUM_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title


def calc_cv(b: list[float]) -> float:
    """
     Calculate coefficient of variation
     :param b: list of initial moments
    """
    return np.sqrt(b[1] - b[0]**2)/b[0]


def run(qp, rho=0.7):
    """
    Find best cooling delay for a given set of parameters and utilization factor.
    :param qp: dictionary of parameters
    :param wait_cost: cost of waiting for
    :param server_cost: cost of running the server
    :param wait_cost_calc_func: function to calculate waiting cost
    :return: best cooling delay
    """

    delays = np.linspace(qp['delay']['mean']['min'], qp['delay']['mean']['max'],
                         qp['delay']['mean']['num_points'])

    wait_time_cv = np.zeros(len(delays))
    b_w = calc_moments_by_mean_and_coev(
        qp['warmup']['mean']['base'], qp['warmup']['cv']['base'])
    b_c = calc_moments_by_mean_and_coev(
        qp['cooling']['mean']['base'], qp['cooling']['cv']['base'])

    service_mean = qp['channels']['base']*rho/qp['arrival_rate']

    b = calc_moments_by_mean_and_coev(
        service_mean, qp['service']['cv']['base'])

    with tqdm(total=len(delays), desc="Calculating costs") as pbar:

        for delay_num, delay in enumerate(delays):

            b_d = calc_moments_by_mean_and_coev(
                delay, qp['delay']['cv']['base'])

            num_results = run_calculation(
                arrival_rate=qp['arrival_rate'], num_channels=qp['channels']['base'],
                b=b, b_w=b_w, b_c=b_c, b_d=b_d)

            wait_time_cv[delay_num] = calc_cv(num_results['w'])

            pbar.update(1)

    return wait_time_cv.tolist(), delays.tolist()


if __name__ == "__main__":

    import os

    # if results/best_delay does not exist
    if not os.path.exists("results/best_delay_sla"):
        os.makedirs("results/best_delay_sla")

    base_qp = read_parameters_from_yaml("base_parameters.yaml")

    # only cooling for simplification
    base_qp['warmup']['mean']['base'] = 0.1
    base_qp['cooling']['mean']['base'] = 5.0
    base_qp['delay']['mean']['num_points'] = 20

    save_path = 'results/best_delay_sla/wait_time_cv.png'

    _fig, ax = plt.subplots()

    for rho in [0.3, 0.7, 0.9]:
        wait_time_cv, delays = run(
            base_qp, rho=rho)

        ax.plot(delays, wait_time_cv, label=r"$\rho$"+f'={rho}')

    ax.set_xlabel("Cooling Delay (s)")
    ax.set_ylabel('Wait Time CV')
    plt.legend()

    plt.savefig(save_path)
    plt.show()

    plt.close(_fig)
