import time

import numpy as np
from most_queue.sim import rand_destribution as rd
from most_queue.sim.qs_sim import QueueingSystemSimulator
from most_queue.theory.mgn_with_h2_delay_cold_warm import MGnH2ServingColdWarmDelay

from utils import dump_stat
from utils import print_table, make_plot, calc_moments_by_mean_and_coev, load_stat


def get_sim_stat(stat, n, l, buff, b, b_c, b_w, b_d, num_of_jobs, p_limit, sim_ave):
    im_start = time.process_time()
    w_sim_mass = []
    p_sim_mass = []
    warm_prob_sim_mass = []
    cold_prob_sim_mass = []
    cold_delay_prob_sim_mass = []

    for j in range(sim_ave):
        print(f"\nStart {j + 1}/{sim_ave} simulation")
        sim = QueueingSystemSimulator(n, buffer=buff)
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

        w_sim_mass.append(sim.w)
        p_sim_mass.append(sim.get_p()[:p_limit])
        warm_prob_sim_mass.append(sim.get_warmup_prob())
        cold_prob_sim_mass.append(sim.get_cold_prob())
        cold_delay_prob_sim_mass.append(sim.get_cold_delay_prob())

    # average all sim data

    w_ave = [0, 0, 0]
    p_ave = [0.0] * p_limit
    for k in range(3):
        for j in range(sim_ave):
            w_ave[k] += w_sim_mass[j][k]
        w_ave[k] /= sim_ave

    for k in range(p_limit):
        for j in range(sim_ave):
            p_ave[k] += p_sim_mass[j][k]
        p_ave[k] /= sim_ave

    im_time = time.process_time() - im_start

    stat["w_sim"] = w_ave
    stat["p_sim"] = p_ave
    stat["sim_time"] = im_time

    stat["sim_warm_prob"] = np.array(warm_prob_sim_mass).mean()

    stat["sim_cold_prob"] = np.array(cold_prob_sim_mass).mean()

    stat["sim_cold_delay_prob"] = np.array(cold_delay_prob_sim_mass).mean()


def get_tt_stat(stat, n, l, buff, b, b_c, b_w, b_d, p_limit, w_pls_dt, stable_w_pls, verbose=False):
    tt_start = time.process_time()
    tt = MGnH2ServingColdWarmDelay(l, b, b_w, b_c, b_d, n,
                                   buffer=buff, verbose=verbose, w_pls_dt=w_pls_dt, stable_w_pls=stable_w_pls)

    tt.run()
    p_tt = tt.get_p()
    w_tt = tt.get_w()  # .get_w() -> wait times

    tt_time = time.process_time() - tt_start

    stat["w_tt"] = w_tt
    stat["tt_time"] = tt_time
    stat["p_tt"] = p_tt[:p_limit]
    stat["tt_num_of_iter"] = tt.num_of_iter_

    stat["tt_warm_prob"] = tt.get_warmup_prob()
    stat["tt_cold_prob"] = tt.get_cold_prob()
    stat["tt_cold_delay_prob"] = tt.get_cold_delay_prob()


def ro_test(b1_service, coev_service,
            b1_warm, coev_warm,
            b1_cold, coev_cold,
            b1_cold_delay, coev_cold_delay,
            n=1, num_of_jobs=300000,
            num_of_roes=12, min_ro=0.1, max_ro=0.9,
            p_limit=20, w_pls_dt=1e-3, stable_w_pls=False, sim_ave=3,
            verbose=False):
    """
    b1_service: mean service time
    coev_service: service time coefficient of variation

    b1_warm: setup (or "warm-up ") mean time
    coev_warm: warm-up coefficient of variation

    b1_cold: vacation  (or "cooling") mean time
    coev_cold: vacation  (or "cooling") coefficient of variation

    b1_cold_delay: average cooling start delay time
    coev_cold_delay: coefficient of variation of cooling start delay

    n: number of channels
    num_of_jobs - number of jobs for the simulation model

    num_of_roes - number of utilization factors
    min_ro - min value of utilization factor
    max_ro - max value of utilization factor

    p_limit - max number of probabilities

    w_pls_dt -  some variable to stabilize derivative of the Laplace-Stieltjes transform
                for the waiting time initial moments calculation

    stable_w_pls -  if True the algorithm try to fit w_pls_dt value
                    taking into account the values of transition intensities

    sim_ave - number of runs of the simulation model to average values (reduce variance)

    verbose - is it necessary to display related information
    """

    # ro = l*b1/n Будем подбирать l от ro
    roes = np.linspace(min_ro, max_ro, num_of_roes)

    experiment_stats = []

    for ro_num, ro in enumerate(roes):
        print(f"Start {ro_num + 1}/{len(roes)} with ro={ro:0.3f}... ")

        stat = {}
        l = n * ro / b1_service

        stat["l"] = l
        stat["ro"] = ro
        stat["n"] = n

        b = calc_moments_by_mean_and_coev(b1_service, coev_service)
        b_w = calc_moments_by_mean_and_coev(b1_warm, coev_warm)
        b_c = calc_moments_by_mean_and_coev(b1_cold, coev_cold)
        b_d = calc_moments_by_mean_and_coev(b1_cold_delay, coev_cold_delay)

        stat["b"] = b
        stat["coev_service"] = coev_service

        stat["b_w"] = b_w
        stat["coev_warm"] = coev_warm

        stat["b_c"] = b_c
        stat["coev_cold"] = coev_cold

        stat["b_d"] = b_d
        stat["coev_cold_delay"] = coev_cold_delay

        get_tt_stat(stat, n, l, None, b, b_c, b_w, b_d, p_limit, w_pls_dt, stable_w_pls, verbose=verbose)

        get_sim_stat(stat, n, l, None, b, b_c, b_w, b_d, num_of_jobs, p_limit, sim_ave)

        experiment_stats.append(stat)

    return experiment_stats


def n_test(b1_service, coev_service,
           b1_warm, coev_warm,
           b1_cold, coev_cold,
           b1_cold_delay, coev_cold_delay,
           num_of_jobs=300000,
           ro=0.7, n_min=1, n_max=30,
           p_limit=20, w_pls_dt=1e-3, stable_w_pls=False, sim_ave=3,
           verbose=False):
    """
    b1_service: mean service time
    coev_service: service time coefficient of variation

    b1_warm: setup (or "warm-up ") mean time
    coev_warm: warm-up coefficient of variation

    b1_cold: vacation  (or "cooling") mean time
    coev_cold: vacation  (or "cooling") coefficient of variation

    b1_cold_delay: average cooling start delay time
    coev_cold_delay: coefficient of variation of cooling start delay

    ro - QS utilization factor

    num_of_jobs - number of jobs for the simulation model

    n_min: min value of number of channels
    n_max: max value of number of channels

    p_limit - max number of probabilities

    w_pls_dt -  some variable to stabilize derivative of the Laplace-Stieltjes transform
                for the waiting time initial moments calculation

    stable_w_pls -  if True the algorithm try to fit w_pls_dt value
                    taking into account the values of transition intensities

    sim_ave - number of runs of the simulation model to average values (reduce variance)

    verbose - is it necessary to display related information
    """

    # ro = l*b1/n Будем подбирать l от ro
    ns = [n for n in range(n_min, n_max + 1)]

    experiment_stats = []

    for n in ns:
        print(f"Start {n}/{len(ns)}... ")

        stat = {}
        l = n * ro / b1_service

        stat["l"] = l
        stat["ro"] = ro
        stat["n"] = n

        b = calc_moments_by_mean_and_coev(b1_service, coev_service)
        b_w = calc_moments_by_mean_and_coev(b1_warm, coev_warm)
        b_c = calc_moments_by_mean_and_coev(b1_cold, coev_cold)
        b_d = calc_moments_by_mean_and_coev(b1_cold_delay, coev_cold_delay)

        stat["b"] = b
        stat["coev_service"] = coev_service

        stat["b_w"] = b_w
        stat["coev_warm"] = coev_warm

        stat["b_c"] = b_c
        stat["coev_cold"] = coev_cold

        stat["b_d"] = b_d
        stat["coev_cold_delay"] = coev_cold_delay

        get_tt_stat(stat, n, l, None, b, b_c, b_w, b_d, p_limit, w_pls_dt, stable_w_pls, verbose=verbose)

        get_sim_stat(stat, n, l, None, b, b_c, b_w, b_d, num_of_jobs, p_limit, sim_ave)

        experiment_stats.append(stat)

    return experiment_stats


def delay_mean_test(b1_service, coev_service,
                    b1_warm, coev_warm,
                    b1_cold, coev_cold,
                    coev_cold_delay,
                    n=1, num_of_jobs=300000, ro=0.7,
                    num_of_delays=12, min_delay=0.1, max_delay=10,
                    p_limit=20, w_pls_dt=1e-3, stable_w_pls=False, sim_ave=3,
                    verbose=False):
    """
    b1_service: mean service time
    coev_service: service time coefficient of variation

    b1_warm: setup (or "warm-up ") mean time
    coev_warm: warm-up coefficient of variation

    b1_cold: vacation  (or "cooling") mean time
    coev_cold: vacation  (or "cooling") coefficient of variation

    coev_cold_delay: coefficient of variation of cooling start delay

    n - number of channels
    num_of_jobs - number of jobs for the simulation model
    ro - QS utilization factor

    num_of_delays - number of cooling delays times
    min_delay - min value of cooling delay
    max_delay - max value of cooling delay

    p_limit - max number of probabilities

    w_pls_dt -  some variable to stabilize derivative of the Laplace-Stieltjes transform
                for the waiting time initial moments calculation

    stable_w_pls -  if True the algorithm try to fit w_pls_dt value
                    taking into account the values of transition intensities

    sim_ave - number of runs of the simulation model to average values (reduce variance)

    verbose - is it necessary to display related information
    """

    ds = np.linspace(min_delay, max_delay, num_of_delays)

    experiment_stats = []

    for d_num, d in enumerate(ds):
        print(f"Start {d_num + 1}/{len(ds)} with delta={d:0.3f}... ")
        stat = {}
        l = n * ro / b1_service

        stat["l"] = l
        stat["ro"] = ro
        stat["n"] = n

        b = calc_moments_by_mean_and_coev(b1_service, coev_service)
        b_w = calc_moments_by_mean_and_coev(b1_warm, coev_warm)
        b_c = calc_moments_by_mean_and_coev(b1_cold, coev_cold)
        b_d = calc_moments_by_mean_and_coev(d, coev_cold_delay)

        stat["b"] = b
        stat["coev_service"] = coev_service

        stat["b_w"] = b_w
        stat["coev_warm"] = coev_warm

        stat["b_c"] = b_c
        stat["coev_cold"] = coev_cold

        stat["b_d"] = b_d
        stat["coev_cold_delay"] = coev_cold_delay

        get_tt_stat(stat, n, l, None, b, b_c, b_w, b_d, p_limit, w_pls_dt, stable_w_pls, verbose=verbose)
        get_sim_stat(stat, n, l, None, b, b_c, b_w, b_d, num_of_jobs, p_limit, sim_ave)

        experiment_stats.append(stat)

    return experiment_stats


if __name__ == '__main__':
    import os

    n = 3
    ro = 0.7

    if not os.path.exists(f"ro_test/n_{n}.json"):
        ro_stat = ro_test(b1_service=10.0, coev_service=1.2,
                          b1_warm=3.1, coev_warm=0.87,
                          b1_cold=4.1, coev_cold=1.1,
                          b1_cold_delay=3.71, coev_cold_delay=1.2,
                          n=n, num_of_jobs=300000,
                          num_of_roes=30, min_ro=0.1, max_ro=0.9, w_pls_dt=1e-3,
                          stable_w_pls=True, sim_ave=10)

        dump_stat(ro_stat, save_name=f"ro_test/n_{n}.json")

    else:
        ro_stat = load_stat(f"ro_test/n_{n}.json")

    print_table(ro_stat)
    make_plot(ro_stat, param_name='ro', mode='abs')

    if not os.path.exists(f"n_test/ro_{ro:0.3f}.json"):
        n_stat = n_test(b1_service=10.0, coev_service=1.2,
                        b1_warm=3.1, coev_warm=0.87,
                        b1_cold=4.1, coev_cold=1.1,
                        b1_cold_delay=3.71, coev_cold_delay=1.2,
                        num_of_jobs=300000,
                        n_min=1, n_max=30, ro=ro, w_pls_dt=1e-3,
                        stable_w_pls=True, sim_ave=10)

        dump_stat(n_stat, save_name=f"n_test/ro_{ro:0.3f}.json")

    else:

        n_stat = load_stat(f"n_test/ro_{ro:0.3f}.json")


    print_table(n_stat)
    make_plot(n_stat, param_name='n', mode='abs')

    if not os.path.exists(f"delay_mean_test/n_{n}_ro_{ro}.json"):

        delay_stat = delay_mean_test(b1_service=10.0, coev_service=1.2,
                                     b1_warm=3.1, coev_warm=0.87,
                                     b1_cold=4.1, coev_cold=1.1, ro=ro,
                                     coev_cold_delay=1.2,
                                     n=n, num_of_jobs=1000000,
                                     num_of_delays=30, min_delay=0.1, max_delay=10,
                                     w_pls_dt=1e-3, stable_w_pls=True, sim_ave=10)

        dump_stat(delay_stat, save_name=f"delay_mean_test/n_{n}_ro_{ro}.json")

    else:

        delay_stat = load_stat(f"delay_mean_test/n_{n}_ro_{ro}.json")

    print_table(delay_stat)
    make_plot(delay_stat, param_name='delay_mean', mode='abs')