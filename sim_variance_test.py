import numpy as np
from most_queue.sim.qs_sim import QueueingSystemSimulator
import time
from most_queue.sim import rand_destribution as rd
import json
from utils import calc_moments_by_mean_and_coev, load_stat
import matplotlib.pyplot as plt

def get_sim_w_on_ro(n, b1_service, coev_service, b1_warm, coev_warm, b1_cold, coev_cold, b1_cold_delay, coev_cold_delay,
              num_of_jobs,
              sim_at_ro=30, ro_min=0.1, ro_max=0.9, num_of_roes=15,
              save_json_name='variance_test.json'):
    im_start = time.process_time()
    w1_sim_mass = []

    b = calc_moments_by_mean_and_coev(b1_service, coev_service)
    b_w = calc_moments_by_mean_and_coev(b1_warm, coev_warm)
    b_c = calc_moments_by_mean_and_coev(b1_cold, coev_cold)
    b_d = calc_moments_by_mean_and_coev(b1_cold_delay, coev_cold_delay)

    roes = np.linspace(ro_min, ro_max, num_of_roes)

    experiments_stat = {'roes': roes.tolist(), 'sim_at_ro': sim_at_ro, 'n': n, 'b': b, 'b_c': b_c, 'b_w': b_w,
                        'b_d': b_d, 'num_of_jobs': num_of_jobs}

    for ro_i, ro in enumerate(roes):
        w1_sim_mass.append([])
        for j in range(sim_at_ro):
            l = n * ro / b1_service
            sim = QueueingSystemSimulator(n, buffer=None)
            sim.set_sources(l, 'M')

            gamma_params = rd.Gamma.get_mu_alpha(b)
            gamma_params_warm = rd.Gamma.get_mu_alpha(b_w)
            gamma_params_cold = rd.Gamma.get_mu_alpha(b_c)
            gamma_params_cold_delay = rd.Gamma.get_mu_alpha(b_d)

            sim.set_servers(gamma_params, 'Gamma')
            sim.set_warm(gamma_params_warm, 'Gamma')
            sim.set_cold(gamma_params_cold, 'Gamma')
            sim.set_cold_delay(gamma_params_cold_delay, 'Gamma')

            sim.run(num_of_jobs)

            w1_sim_mass[ro_i].append(sim.w[0])

    experiments_stat['w1_mass'] = w1_sim_mass
    experiments_stat['sim_time'] = time.process_time() - im_start

    if save_json_name:
        with open(save_json_name, 'w') as f:
            json.dump(experiments_stat, f)

    return experiments_stat

def get_sim_w_on_n(ro, b1_service, coev_service, b1_warm, coev_warm, b1_cold, coev_cold, b1_cold_delay, coev_cold_delay,
              num_of_jobs,
              sim_at_n=30, n_min=1, n_max=30,
              save_json_name='variance_test.json'):
    im_start = time.process_time()
    w1_sim_mass = []

    b = calc_moments_by_mean_and_coev(b1_service, coev_service)
    b_w = calc_moments_by_mean_and_coev(b1_warm, coev_warm)
    b_c = calc_moments_by_mean_and_coev(b1_cold, coev_cold)
    b_d = calc_moments_by_mean_and_coev(b1_cold_delay, coev_cold_delay)

    ns = [x for x in range(n_min, n_max+1)]

    experiments_stat = {'ro': ro, 'sim_at_n': sim_at_n, 'ns': ns, 'b': b, 'b_c': b_c, 'b_w': b_w,
                        'b_d': b_d, 'num_of_jobs': num_of_jobs}

    for i, n in enumerate(ns):
        w1_sim_mass.append([])
        for j in range(sim_at_n):
            l = n * ro / b1_service
            sim = QueueingSystemSimulator(n, buffer=None)
            sim.set_sources(l, 'M')

            gamma_params = rd.Gamma.get_mu_alpha(b)
            gamma_params_warm = rd.Gamma.get_mu_alpha(b_w)
            gamma_params_cold = rd.Gamma.get_mu_alpha(b_c)
            gamma_params_cold_delay = rd.Gamma.get_mu_alpha(b_d)

            sim.set_servers(gamma_params, 'Gamma')
            sim.set_warm(gamma_params_warm, 'Gamma')
            sim.set_cold(gamma_params_cold, 'Gamma')
            sim.set_cold_delay(gamma_params_cold_delay, 'Gamma')

            sim.run(num_of_jobs)

            w1_sim_mass[i].append(sim.w[0])

    experiments_stat['w1_mass'] = w1_sim_mass
    experiments_stat['sim_time'] = time.process_time() - im_start

    if save_json_name:
        with open(save_json_name, 'w') as f:
            json.dump(experiments_stat, f)

    return experiments_stat

def plot_variance(stat, x='ro'):
    w1_mass = stat['w1_mass']
    if x == 'ro':
        xs = stat['roes']
        vars = []
        for ro_i, ro in enumerate(xs):
            vars.append(np.array(w1_mass[ro_i]).var())
    elif x == 'n':
        xs = stat['ns']
        vars = []
        for n_i, n in enumerate(xs):
            vars.append(np.array(w1_mass[n_i]).var())

    fig, ax = plt.subplots()
    ax.plot(xs, vars)
    ax.set_ylabel(r"$\sigma$")

    if x == 'ro':
        ax.set_xlabel(r"$\rho$")
    elif x == 'n':
        ax.set_xlabel("n")

    plt.show()


if __name__ == '__main__':
    n = 3
    # stat = get_sim_w_on_ro(n, b1_service=10.0, coev_service=1.2,
    #                  b1_warm=3.1, coev_warm=0.87,
    #                  b1_cold=4.1, coev_cold=1.1,
    #                  b1_cold_delay=3.71, coev_cold_delay=1.2,
    #                  num_of_jobs=300000,
    #                  num_of_roes=10, ro_min=0.1, ro_max=0.9, sim_at_ro=10, save_json_name=f'variance_test_n_{n}_on_ro.json')

    ro = 0.7
    stat = get_sim_w_on_n(ro, b1_service=10.0, coev_service=1.2,
                           b1_warm=3.1, coev_warm=0.87,
                           b1_cold=4.1, coev_cold=1.1,
                           b1_cold_delay=3.71, coev_cold_delay=1.2,
                           num_of_jobs=300000,
                           n_min=1, n_max=30, sim_at_n=10,
                           save_json_name=f'variance_test_ro_{ro:0.3f}_on_n.json')

    # stat = load_stat(f'variance_test_n_{n}.json')

    plot_variance(stat, x='n')
