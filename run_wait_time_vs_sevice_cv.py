"""
Run simulation and calculation for different service time coefficient of variation 
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

UTILIZATION = 0.7

WARM_UP_TIME_MEAN = 3.1
WARM_UP_TIME_CV = 0.87

COOL_TIME_MEAN = 4.1
COOL_TIME_CV = 1.1

COOL_DELAY_MEAN = 3.71
COOL_DELAY_CV = 1.2

NUM_OF_CHANNES = 3


def run_wait_time_vs_service_cv(cv_min: float = 0.3, cv_max: float = 3.0,
                                num_points: int = 20, save_path: str = None):
    """
    Run simulation and calculation for different service time coefficient of variation 
    """
    cvs = np.linspace(cv_min, cv_max, num_points)

    w1_num = []
    w1_sim = []

    b_w = calc_moments_by_mean_and_coev(WARM_UP_TIME_MEAN, WARM_UP_TIME_CV)
    b_c = calc_moments_by_mean_and_coev(COOL_TIME_MEAN, COOL_TIME_CV)
    b_d = calc_moments_by_mean_and_coev(COOL_DELAY_MEAN, COOL_DELAY_CV)

    service_mean = NUM_OF_CHANNES*UTILIZATION/ARRIVAL_RATE

    for cv_num, cv in enumerate(cvs):
        print(
            f"Start {cv_num + 1}/{len(cvs)} with service time cv={cv:0.3f}... ")

        b = calc_moments_by_mean_and_coev(service_mean, cv)

        num_results = run_calculation(
            arrival_rate=ARRIVAL_RATE, num_channels=NUM_OF_CHANNES, b=b, b_w=b_w, b_c=b_c, b_d=b_d)
        sim_results = run_simulation(
            arrival_rate=ARRIVAL_RATE, num_channels=NUM_OF_CHANNES, b=b, b_w=b_w, b_c=b_c, b_d=b_d)

        w1_num.append(num_results["w"][0])
        w1_sim.append(sim_results["w"][0])

    _fig, ax = plt.subplots()
    ax.plot(cvs, w1_num, label="num")
    ax.plot(cvs, w1_sim, label="sim")
    ax.legend()
    ax.set_xlabel("Service time CV")
    ax.set_ylabel("Wait Time")

    if save_path:
        plt.savefig(save_path, dpi=300)
    else:
        plt.show()


if __name__ == "__main__":
    run_wait_time_vs_service_cv(save_path='wait_time_vs_service_cv.png')
