"""
Run one simulation vs calculation for queueing system.
with H2-warming, H2-cooling and H2-delay of cooling starts.
"""
import math
import time

from most_queue.general.tables import probs_print, times_print
from most_queue.rand_distribution import GammaDistribution
from most_queue.sim.vacations import VacationQueueingSystemSimulator
from most_queue.theory.vacations.mgn_with_h2_delay_cold_warm import (
    MGnH2ServingColdWarmDelay,
)


def calc_moments_by_mean_and_coev(mean, coev):
    """
    Calculate the E[X^k] for k=0,1,2
    for a distribution with given mean and coefficient of variation.
    :param mean: The mean value of the distribution.
    :param coev: The coefficient of variation (standard deviation divided by the mean).
    :return: A list containing the calculated moments
    """
    b = [0.0] * 3
    alpha = 1 / (coev ** 2)
    b[0] = mean
    b[1] = math.pow(b[0], 2) * (math.pow(coev, 2) + 1)
    b[2] = b[1] * b[0] * (1.0 + 2 / alpha)
    return b


def run_calculation(arrival_rate: float, 
                    b: list, b_w: list, b_c: list, b_d: list,
                    num_channels: int):
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
    stat["process_time"] = time.process_time() - num_start
    stat["p"] = solver.get_p()[:10]
    stat["num_of_iter"] = solver.num_of_iter_

    stat["warmup_prob"] = solver.get_warmup_prob()
    stat["cold_prob"] = solver.get_cold_prob()
    stat["cold_delay_prob"] = solver.get_cold_delay_prob()

    return stat


def run_simulation(arrival_rate: float, b: float, b_w: float, b_c: float, b_d: float,
                   num_channels: int, num_of_jobs: int=300_000):
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
    im_start = time.process_time()
    print("Start simulation")
    sim = VacationQueueingSystemSimulator(num_channels)
    sim.set_sources(arrival_rate, 'M')

    gamma_params = GammaDistribution.get_params(b)
    gamma_params_warm = GammaDistribution.get_params(b_w)
    gamma_params_cold = GammaDistribution.get_params(b_c)
    gamma_params_cold_delay = GammaDistribution.get_params(b_d)

    sim.set_servers(gamma_params, 'Gamma')
    sim.set_warm(gamma_params_warm, 'Gamma')
    sim.set_cold(gamma_params_cold, 'Gamma')
    sim.set_cold_delay(gamma_params_cold_delay, 'Gamma')

    sim.run(num_of_jobs)

    stat = {}
    stat["w"] = sim.w
    stat["p"] = sim.get_p()[:10]
    stat["process_time"] = time.process_time() - im_start

    stat["warmup_prob"] = sim.get_warmup_prob()

    stat["cold_prob"] = sim.get_cold_prob()

    stat["cold_delay_prob"] = sim.get_cold_delay_prob()

    return stat


if __name__ == "__main__":

    ARRIVAL_RATE = 1.0

    SERVICE_TIME_CV = 1.2

    WARM_UP_TIME_MEAN = 3.1
    WARM_UP_TIME_CV = 0.87

    COOL_TIME_MEAN = 4.1
    COOL_TIME_CV = 1.1

    COOL_DELAY_MEAN = 3.71
    COOL_DELAY_CV = 1.2

    NUM_OF_CHANNES = 3

    UTILIZATION_FACTOR = 0.7

    SERVICE_TIME_MEAN = NUM_OF_CHANNES*UTILIZATION_FACTOR/ARRIVAL_RATE

    # Calculate initial moments for service time, warm-up time,
    # cool-down time, and delay before cooling starts.
    b = calc_moments_by_mean_and_coev(SERVICE_TIME_MEAN, SERVICE_TIME_CV)
    b_w = calc_moments_by_mean_and_coev(WARM_UP_TIME_MEAN, WARM_UP_TIME_CV)
    b_c = calc_moments_by_mean_and_coev(COOL_TIME_MEAN, COOL_TIME_CV)
    b_d = calc_moments_by_mean_and_coev(COOL_DELAY_MEAN, COOL_DELAY_CV)

    num_results = run_calculation(arrival_rate=ARRIVAL_RATE, num_channels=NUM_OF_CHANNES, b=b, b_w=b_w, b_c=b_c, b_d=b_d)
    sim_results = run_simulation(arrival_rate=ARRIVAL_RATE, num_channels=NUM_OF_CHANNES, b=b, b_w=b_w, b_c=b_c, b_d=b_d)

    probs_print(p_sim=sim_results["p"], p_num=num_results["p"], size=10)
    times_print(sim_moments=sim_results["w"], calc_moments=num_results["w"])
