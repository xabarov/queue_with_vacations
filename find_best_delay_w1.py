"""
Find best cooling delay for a given set of parameters and utilization factor.
"""
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

from run_one_calc_vs_sim import calc_moments_by_mean_and_coev, run_calculation
from utils import read_parameters_from_yaml

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

def calc_wait_cost(w1: float, wait_cost: float,) -> float:
    """
    Calculate cost of waiting 
    :param w1: mean, waiting time
    :param wait_cost: cost of waiting for
    :return: waiting cost
    """
    return w1*wait_cost


def calc_no_linear_wait_cost(w1: float, wait_cost: float, alpha=0.7) -> float:
    """
    Calculate cost of waiting 
    Waiting times raised in exp way, but user experience is more linear.
    :param w1: mean, waiting time
    :param wait_cost: cost of waiting for
    :return: waiting cost
    """
    return (w1 ** alpha)*wait_cost


def run(qp, wait_cost_calc_func=calc_wait_cost):
    """
    Find best cooling delay for a given set of parameters and utilization factor.
    :param qp: dictionary of parameters
    :param wait_cost: cost of waiting for
    :param server_cost: cost of running the server
    :param wait_cost_calc_func: function to calculate waiting cost
    :return: best cooling delay
    """
    wait_cost = qp['wait_cost']
    server_cost = qp['server_cost']
    idle_bonus = qp['idle_bonus']

    rhoes = np.linspace(qp['utilization']['min'], qp['utilization']['max'],
                        qp['utilization']['num_points'])

    delays = np.linspace(qp['delay']['mean']['min'], qp['delay']['mean']['max'],
                         qp['delay']['mean']['num_points'])

    total_costs = np.zeros((len(rhoes), len(delays)))
    wait_costs = np.zeros((len(rhoes), len(delays)))
    server_costs = np.zeros((len(rhoes), len(delays)))
    b_w = calc_moments_by_mean_and_coev(
        qp['warmup']['mean']['base'], qp['warmup']['cv']['base'])
    b_c = calc_moments_by_mean_and_coev(
        qp['cooling']['mean']['base'], qp['cooling']['cv']['base'])

    with tqdm(total=len(rhoes) * len(delays), desc="Calculating costs") as pbar:
        for rho_num, rho in enumerate(rhoes):

            service_mean = qp['channels']['base']*rho/qp['arrival_rate']

            b = calc_moments_by_mean_and_coev(
                service_mean, qp['service']['cv']['base'])

            for delay_num, delay in enumerate(delays):

                b_d = calc_moments_by_mean_and_coev(
                    delay, qp['delay']['cv']['base'])

                num_results = run_calculation(
                    arrival_rate=qp['arrival_rate'], num_channels=qp['channels']['base'],
                    b=b, b_w=b_w, b_c=b_c, b_d=b_d)

                server_busy_probs = num_results["servers_busy_probs"]
                cur_servers_cost = np.sum(
                    [i*prob*server_cost for i, prob in enumerate(server_busy_probs)])
                cur_servers_cost -= server_busy_probs[0] * \
                    qp['channels']['base']*idle_bonus

                cur_wait_cost = wait_cost_calc_func(
                    w1=num_results["w"][0], wait_cost=wait_cost)
                cur_total_cost = cur_wait_cost + cur_servers_cost

                total_costs[rho_num, delay_num] = cur_total_cost
                wait_costs[rho_num, delay_num] = cur_wait_cost
                server_costs[rho_num, delay_num] = cur_servers_cost

                pbar.update(1)

    min_cost_index = np.argmin(total_costs, axis=1)
    # find best cost for each rho
    best_total_costs = np.min(total_costs, axis=1)
    best_server_costs = np.min(server_costs, axis=1)
    best_wait_costs = np.min(wait_costs, axis=1)

    # find best delay for each rho
    best_delays = delays[min_cost_index]
    return rhoes, best_delays, best_total_costs, best_server_costs, best_wait_costs


if __name__ == "__main__":

    import os

    # if results/best_delay does not exist
    if not os.path.exists("results/best_delay"):
        os.makedirs("results/best_delay")

    base_qp = read_parameters_from_yaml("base_parameters.yaml")

    # only cooling for simplification
    base_qp['warmup']['mean']['base'] = 0.1
    base_qp['cooling']['mean']['base'] = 5.0
    base_qp['delay']['mean']['num_points'] = 10

    rhos, best_delay, best_cost, best_server, best_wait = run(
        base_qp, wait_cost_calc_func=calc_no_linear_wait_cost)

    y_labels = ["Cooling Delay", "Total Cost", "Server Cost", 'Wait Cost']

    for y_label, y_data in zip(y_labels, [best_delay, best_cost, best_server, best_wait]):

        # plot results
        _fig, ax = plt.subplots()
        ax.plot(rhos, y_data)
        ax.set_xlabel(r"$\rho$")
        ax.set_ylabel(y_label)

        SAVE_PATH = f"{y_label.replace(' ', '_').lower()}.png"

        plt.savefig(os.path.join('results/best_delay', SAVE_PATH))
        plt.show()

        plt.close(_fig)
