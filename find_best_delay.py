"""
Find best cooling delay for a given set of parameters and utilization factor.
"""
import matplotlib.pyplot as plt
import numpy as np

from run_one_calc_vs_sim import calc_moments_by_mean_and_coev, run_calculation
from utils import read_parameters_from_yaml


def run(qp, wait_cost=1.0, server_cost=10.0):
    """
    Find best cooling delay for a given set of parameters and utilization factor.
    :param qp: dictionary of parameters
    :param wait_cost: cost of waiting for
    :param server_cost: cost of running the server
    :return: best cooling delay
    """
    rhoes = np.linspace(qp['utilization']['min'], qp['utilization']['max'],
                        qp['utilization']['num_points'])

    delays = np.linspace(qp['delay']['mean']['min'], qp['delay']['mean']['max'],
                         qp['delay']['mean']['num_points'])

    costs = np.zeros((len(rhoes), len(delays)))
    b_w = calc_moments_by_mean_and_coev(
        qp['warmup']['mean']['base'], qp['warmup']['cv']['base'])
    b_c = calc_moments_by_mean_and_coev(
        qp['cooling']['mean']['base'], qp['cooling']['cv']['base'])

    for rho_num, rho in enumerate(rhoes):
        print(
            f"Start {rho_num + 1}/{len(rhoes)} with utilization={rho:0.3f}... ")

        service_mean = qp['channels']['base']*rho/qp['arrival_rate']

        b = calc_moments_by_mean_and_coev(
            service_mean, qp['service']['cv']['base'])

        for delay_num, delay in enumerate(delays):

            b_d = calc_moments_by_mean_and_coev(
                delay, qp['delay']['cv']['base'])

            num_results = run_calculation(
                arrival_rate=qp['arrival_rate'], num_channels=qp['channels']['base'], b=b, b_w=b_w, b_c=b_c, b_d=b_d)

            cur_wait_cost = num_results["w"][0]*wait_cost
            server_busy_probs = num_results["servers_busy_probs"]
            cur_servers_cost = np.sum(
                [i*prob*server_cost for i, prob in enumerate(server_busy_probs)])
            total_cost = cur_servers_cost + cur_wait_cost
            costs[rho_num, delay_num] = total_cost

    min_cost_index = np.argmin(costs, axis=1)
    best_delay = delays[min_cost_index]
    return rhoes, best_delay


if __name__ == "__main__":
    base_qp = read_parameters_from_yaml("base_parameters.yaml")
    rhos, best_delays = run(base_qp, wait_cost=1.0, server_cost=7.0)

    # plot results    
    _fig, ax = plt.subplots()
    ax.plot(rhos, best_delays, color="black")
    ax.legend()
    ax.set_xlabel(r"$\rho$")
    ax.set_ylabel("Cost")

    plt.show()

    plt.close(_fig)
