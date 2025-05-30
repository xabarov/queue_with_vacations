QUEUE_PARAMETERS = {
    "arrival_rate": 1.0,
    "service": {
        "cv": 1.2
    },
    "warmup": {
        "mean": 4.0,
        "cv": 0.87
    },
    "cooling": {
        "mean": 4.0,
        "cv": 1.2
    },
    "delay": {
        "mean": 4.0,
        "cv": 1.4
    },
    "utilization": 0.7,
    "jobs_per_sim": 300_000,
    "sim_to_average": 10,
    "channels": 3
}
