import numpy as np
from most_queue.theory.mgn_with_h2_delay_cold_warm import MGnH2ServingColdWarmDelay
from most_queue.sim.rand_destribution import Gamma
from utils import calc_moments_by_mean_and_coev
import matplotlib.pyplot as plt

import numpy


def calc_loss(sojourn_cost, heat_cost, n, l, b, b_c, b_w, b_d,
              buff=None, w_pls_dt=1e-3, stable_w_pls=True, mode='tail', v_max=1.0, prob_v_max=0.999,
              verbose=False):
    tt = MGnH2ServingColdWarmDelay(l, b, b_w, b_c, b_d, n,
                                   buffer=buff, verbose=verbose,
                                   w_pls_dt=w_pls_dt, stable_w_pls=stable_w_pls)

    tt.run()
    p_idle = tt.get_idle_prob()
    v_tt = tt.get_v()  # .get_w() -> wait times
    N = v_tt[0] * l
    if mode == 'tail':
        mu, alpha = Gamma.get_mu_alpha(v_tt)
        cdf = Gamma.get_cdf(mu, alpha, v_max)
        if cdf < prob_v_max:
            v_loss = sojourn_cost * N
        else:
            v_loss = 0
    else:

        v_loss = sojourn_cost * N

    h_loss = heat_cost * (1.0 - p_idle)

    return float(v_loss + h_loss)


def make_loss_plot(delta_mass, losses):
    fig, ax = plt.subplots()
    ax.plot(delta_mass, losses)
    ax.set_ylabel(r"loss")
    ax.set_xlabel("t, с")

    plt.show()


def run_experiment(sojourn_cost, heat_cost, b1_service, coev_service,
                   b1_warm, coev_warm,
                   b1_cold, coev_cold,
                   coev_cold_delay,
                   n=1, ro=0.7,
                   num_of_delays=12, min_delay=0.1, max_delay=10,
                   w_pls_dt=1e-3, stable_w_pls=False, buff=None, mode='tail', v_max=1.0, prob_v_max=0.999,
                   verbose=False):
    l = n * ro / b1_service

    b = calc_moments_by_mean_and_coev(b1_service, coev_service)
    b_w = calc_moments_by_mean_and_coev(b1_warm, coev_warm)
    b_c = calc_moments_by_mean_and_coev(b1_cold, coev_cold)
    ds = np.linspace(min_delay, max_delay, num_of_delays)

    losses = []

    for d in ds:
        b_d = calc_moments_by_mean_and_coev(d, coev_cold_delay)
        losses.append(calc_loss(sojourn_cost, heat_cost, n, l, b, b_c, b_w, b_d,
                                buff=buff, w_pls_dt=w_pls_dt, stable_w_pls=stable_w_pls,
                                verbose=verbose, prob_v_max=prob_v_max, v_max=v_max, mode=mode))

    make_loss_plot(ds, losses)

    min_loss = min(losses)
    delta_min = ds[np.argmin(np.array(losses))]
    print(f"Min loss {min_loss:0.3f} at delta = {delta_min:0.3f}s")


if __name__ == '__main__':
    n = 3
    ro = 0.1
    run_experiment(sojourn_cost=1.0, heat_cost=1.0, b1_service=1.0, coev_service=1.2,
                   b1_warm=1.0, coev_warm=0.87,
                   b1_cold=1.0, coev_cold=1.1,
                   coev_cold_delay=1.2,
                   n=n, ro=ro,
                   num_of_delays=30, min_delay=0.01, max_delay=10, mode='tail', v_max=1.3, prob_v_max=0.5,
                   w_pls_dt=1e-3, stable_w_pls=True)
