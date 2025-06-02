"""
Run one simulation vs calculation for queueing system.
with H2-warming, H2-cooling and H2-delay of cooling starts.
"""
import time

import numpy as np
from most_queue.general.tables import probs_print, times_print
from most_queue.rand_distribution import GammaDistribution
from most_queue.sim.vacations import VacationQueueingSystemSimulator
from most_queue.theory.vacations.mgn_with_h2_delay_cold_warm import (
    MGnH2ServingColdWarmDelay,
)

from utils import calc_moments_by_mean_and_coev


def run_calculation(arrival_rate: float, b: list[float],
                    b_w: list[float], b_c: list[float], b_d: list[float],
                    num_channels: int, p_size: int=10):
    """
    Calculation of an M/H2/n queue with H2-warming, H2-cooling and H2-delay 
    of the start of cooling using Takahasi-Takami method.
    Args:
       arrival_rate (float): The arrival rate of the queue.
        b (list): A list containing the E[X^k] k=0, 1, 2. for the service time distribution.
        b_w (list): A list containing the E[X^k] k=0, 1, 2. for the warmup time distribution.
        b_c (list): A list containing the E[X^k] k=0, 1, 2. for the cooling time distribution.
        b_d (list): A list containing the E[X^k] k=0, 1, 2. for the delay time distribution.
        num_of_channels (int): The number of channels in the queue.
    Returns:
        dict: A dictionary containing the statistics of the queue.
    """
    num_start = time.process_time()

    solver = MGnH2ServingColdWarmDelay(
        arrival_rate, b, b_w, b_c, b_d, num_channels)

    solver.run()

    stat = {}
    stat["w"] = solver.get_w()
    stat["v"] = solver.get_v()
    stat["process_time"] = time.process_time() - num_start
    stat["p"] = solver.get_p()[:p_size]
    stat["num_of_iter"] = solver.num_of_iter_

    stat["warmup_prob"] = solver.get_warmup_prob()
    stat["cold_prob"] = solver.get_cold_prob()
    stat["cold_delay_prob"] = solver.get_cold_delay_prob()
    stat['servers_busy_probs'] = solver.get_probs_of_servers_busy()
 
    return stat


def run_simulation(arrival_rate: float, b: list[float],
                   b_w: list[float], b_c: list[float], b_d: list[float],
                   num_channels: int, num_of_jobs: int = 300_000, 
                   ave_num: int = 10, p_size: int=10):
    """
    Run simulation for an M/H2/n queue with H2-warming, 
    H2-cooling and H2-delay before cooling starts.
    Args:
       arrival_rate (float): The arrival rate of the queue.
        b (list): A list containing the E[X^k] k=0, 1, 2. for the service time distribution.
        b_w (list): A list containing the E[X^k] k=0, 1, 2. for the warmup time distribution.
        b_c (list): A list containing the E[X^k] k=0, 1, 2. for the cooling time distribution.
        b_d (list): A list containing the E[X^k] k=0, 1, 2. for the delay time distribution.
        num_of_channels (int): The number of channels in the queue.
        num_of_jobs (int): The number of jobs to simulate.
    Returns:
        dict: A dictionary containing the statistics of the queue.
    """

    gamma_params = GammaDistribution.get_params(b)
    gamma_params_warm = GammaDistribution.get_params(b_w)
    gamma_params_cold = GammaDistribution.get_params(b_c)
    gamma_params_cold_delay = GammaDistribution.get_params(b_d)

    ws = []
    vs = []
    ps = []
    process_times = []
    warmup_probs = []
    cold_probs = []
    cold_delay_probs = []

    for sim_run_num in range(ave_num):
        print(f"Running simulation {sim_run_num + 1} of {ave_num}")

        im_start = time.process_time()
        sim = VacationQueueingSystemSimulator(num_channels)
        sim.set_sources(arrival_rate, 'M')

        sim.set_servers(gamma_params, 'Gamma')
        sim.set_warm(gamma_params_warm, 'Gamma')
        sim.set_cold(gamma_params_cold, 'Gamma')
        sim.set_cold_delay(gamma_params_cold_delay, 'Gamma')
        sim.run(num_of_jobs)

        ws.append(sim.w)
        vs.append(sim.v)  
        process_times.append(time.process_time() - im_start)
        cold_probs.append(sim.get_cold_prob())
        cold_delay_probs.append(sim.get_cold_delay_prob())
        warmup_probs.append(sim.get_warmup_prob())
        ps.append(sim.get_p()[:p_size])

    # average over all simulations

    stat = {}

    stat["w"] = np.mean(ws, axis=0).tolist()
    stat["v"] = np.mean(vs, axis=0).tolist()
    stat["process_time"] = np.sum(process_times)
    stat["cold_prob"] = np.mean(cold_probs)
    stat["cold_delay_prob"] = np.mean(cold_delay_probs)
    stat["warmup_prob"] = np.mean(warmup_probs)
    stat["p"] = np.mean(ps, axis=0).tolist()

    return stat


if __name__ == "__main__":

    from utils import read_parameters_from_yaml
    
    qp = read_parameters_from_yaml("base_parameters.yaml")

    SERVICE_TIME_MEAN = qp['channels']['base']*qp['utilization']['base']/qp['arrival_rate']

    # Calculate initial moments for service time, warm-up time,
    # cool-down time, and delay before cooling starts.
    b_service = calc_moments_by_mean_and_coev(
        SERVICE_TIME_MEAN, qp['service']['cv']['base'])
    b_warmup = calc_moments_by_mean_and_coev(
        qp['warmup']['mean']['base'], qp['warmup']['cv']['base'])
    b_cooling = calc_moments_by_mean_and_coev(qp['cooling']['mean']['base'], qp['cooling']['cv']['base'])
    b_delay = calc_moments_by_mean_and_coev(qp['delay']['mean']['base'], qp['delay']['cv']['base'])

    num_results = run_calculation(
        arrival_rate=qp['arrival_rate'], num_channels=qp['channels']['base'], b=b_service,
        b_w=b_warmup, b_c=b_cooling, b_d=b_delay
    )
    sim_results = run_simulation(
        arrival_rate=qp['arrival_rate'], num_channels=qp['channels']['base'], b=b_service,
        b_w=b_warmup, b_c=b_cooling, b_d=b_delay, num_of_jobs=qp['jobs_per_sim'],
        ave_num=qp['sim_to_average']
    )
    
    print(f"Sim process time {sim_results['process_time']}")
    print(f"Calculation process time {num_results['process_time']}")

    probs_print(p_sim=sim_results["p"], p_num=num_results["p"], size=10)
    times_print(sim_moments=sim_results["w"], calc_moments=num_results["w"])
