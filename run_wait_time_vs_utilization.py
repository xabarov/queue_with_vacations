"""
Run simulation and calculation for different utilizations factor 
and plot the wait time averages for both calculation and simulation.
"""
import matplotlib.pyplot as plt
import numpy as np

from run_one_calc_vs_sim import (
    calc_moments_by_mean_and_coev,
    run_calculation,
    run_simulation,
)

ARRIVAL_RATE = 1.0

SERVICE_TIME_CV = 1.2

WARM_UP_TIME_MEAN = 3.1
WARM_UP_TIME_CV = 0.87

COOL_TIME_MEAN = 4.1
COOL_TIME_CV = 1.1

COOL_DELAY_MEAN = 3.71
COOL_DELAY_CV = 1.2

NUM_OF_CHANNES = 3


def run_wait_time_vs_utilization(utilization_min: float = 0.1,
                                 utilization_max: float = 0.9,
                                 num_points: int = 20, save_path: str = None):
    """
    Run simulation and calculation for different utilizations and plot the results.
    """
    rhoes = np.linspace(utilization_min, utilization_max, num_points)

    w1_num = []
    w1_sim = []

    b_w = calc_moments_by_mean_and_coev(WARM_UP_TIME_MEAN, WARM_UP_TIME_CV)
    b_c = calc_moments_by_mean_and_coev(COOL_TIME_MEAN, COOL_TIME_CV)
    b_d = calc_moments_by_mean_and_coev(COOL_DELAY_MEAN, COOL_DELAY_CV)

    for rho_num, rho in enumerate(rhoes):
        print(
            f"Start {rho_num + 1}/{len(rhoes)} with utilization={rho:0.3f}... ")

        service_mean = NUM_OF_CHANNES*rho/ARRIVAL_RATE

        b = calc_moments_by_mean_and_coev(service_mean, SERVICE_TIME_CV)

        num_results = run_calculation(
            arrival_rate=ARRIVAL_RATE, num_channels=NUM_OF_CHANNES, b=b, b_w=b_w, b_c=b_c, b_d=b_d)
        sim_results = run_simulation(
            arrival_rate=ARRIVAL_RATE, num_channels=NUM_OF_CHANNES, b=b, b_w=b_w, b_c=b_c, b_d=b_d)

        w1_num.append(num_results["w"][0])
        w1_sim.append(sim_results["w"][0])

    _fig, ax = plt.subplots()
    ax.plot(rhoes, w1_num, label="num")
    ax.plot(rhoes, w1_sim, label="sim")
    ax.legend()
    ax.set_xlabel("Utilization Factor")
    ax.set_ylabel("Wait Time")

    if save_path:
        plt.savefig(save_path, dpi=300)
    else:
        plt.show()


if __name__ == "__main__":
    run_wait_time_vs_utilization(save_path='wait_time_vs_utilization.png')
