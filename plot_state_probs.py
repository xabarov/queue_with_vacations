"""
Plot the state probabilities for a queueing system with H2-warming, H2-cooling, and H2-delay.
"""
import matplotlib.pyplot as plt
from most_queue.general.tables import probs_print, times_print

from run_one_calc_vs_sim import run_calculation, run_simulation
from utils import calc_moments_by_mean_and_coev



if __name__ == "__main__":

    from utils import read_parameters_from_yaml
    
    qp = read_parameters_from_yaml("base_parameters.yaml")

    SERVICE_TIME_MEAN = qp['channels']['base']*qp['utilization']['base']/qp['arrival_rate']

    # Calculate initial moments for service time, warm-up time,
    # cool-down time, and delay before cooling starts.
    
    SAVE_PATH_PROBS = 'results/probs.png'
    
    _fig, ax = plt.subplots()
    
    rhoes = [0.5, 0.7, 0.9]
    
    p_size = 10
    xs = [i for i in range(p_size)]
    
    for rho_num, rho in enumerate(rhoes):
        print(
            f"Start {rho_num + 1}/{len(rhoes)} with utilization={rho:0.3f}... ")

        service_mean = qp['channels']['base']*rho/qp['arrival_rate']

        b_service = calc_moments_by_mean_and_coev(service_mean, qp['service']['cv']['base'])
        b_warmup = calc_moments_by_mean_and_coev(
        qp['warmup']['mean']['base'], qp['warmup']['cv']['base'])
        b_cooling = calc_moments_by_mean_and_coev(qp['cooling']['mean']['base'], qp['cooling']['cv']['base'])
        b_delay = calc_moments_by_mean_and_coev(qp['delay']['mean']['base'], qp['delay']['cv']['base'])

        num_results = run_calculation(
            arrival_rate=qp['arrival_rate'], num_channels=qp['channels']['base'], b=b_service,
            b_w=b_warmup, b_c=b_cooling, b_d=b_delay, p_size=p_size
        )
        sim_results = run_simulation(
            arrival_rate=qp['arrival_rate'], num_channels=qp['channels']['base'], b=b_service,
            b_w=b_warmup, b_c=b_cooling, b_d=b_delay, num_of_jobs=qp['jobs_per_sim'],
            ave_num=qp['sim_to_average'], p_size=p_size
        )

        probs_print(p_sim=sim_results["p"], p_num=num_results["p"], size=10)
        times_print(sim_moments=sim_results["w"], calc_moments=num_results["w"])
        
        ax.plot(xs, sim_results["p"], linestyle='--', label=r"$\rho$"+f' sim={rho}')
        ax.plot(xs, num_results["p"], label=r"$\rho$"+f' num={rho}')

    ax.set_xlabel("State")
    ax.set_ylabel('Probability')
    plt.legend()

    plt.savefig(SAVE_PATH_PROBS)
    plt.show()

    plt.close(_fig)
