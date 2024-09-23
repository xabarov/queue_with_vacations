from tests import n_test
from utils import dump_stat, load_stat, print_table, make_plot

# Run test
ro = 0.35
stat = n_test(b1_service=10.0, coev_service=1.2,
              b1_warm=3.1, coev_warm=0.87,
              b1_cold=4.1, coev_cold=1.1,
              b1_cold_delay=3.71, coev_cold_delay=1.2,
              num_of_jobs=300000,
              n_min=1, n_max=10, ro=ro, w_pls_dt=1e-3,
              stable_w_pls=True, sim_ave=10)

# Explanation of params:
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
# Save results
dump_stat(stat, save_name=f"results/channels_results_ro={ro:0.3f}.json")

# Load results if it needs later:
# stat = load_stat(f"results/channels_results.json")

# Print table with results
print_table(stat)

# Make plot for w1 times. Change mode to 'abs' if you want to see absolute values
make_plot(stat, param_name='n', mode='error')
