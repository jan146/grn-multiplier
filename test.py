from mealpy import FloatVar, SMA, DE, GA
from mealpy import GWO
import numpy as np
import os

def objective_function(solution):
    print(f"{os.getpid()=}, {solution=}")
    return np.sum(solution**2)

problem = {
    "obj_func": objective_function,
    "bounds": FloatVar(lb=(-100., )*3, ub=(100., )*3),
    "minmax": "min",
    "log_to": "console",
}

# optimizer = SMA.OriginalSMA(epoch=10000, pop_size=100, pr=0.03)
optimizer = DE.JADE(epoch=10, pop_size=10)
optimizer = DE.SAP_DE(epoch=10, pop_size=10)
optimizer = GWO.OriginalGWO(epoch=10, pop_size=10)
optimizer = GA.BaseGA(epoch=10, pop_size=10)

optimizer.solve(problem, mode="process", n_workers=2)
print(f"Best solution: {optimizer.g_best.solution}, Best fitness: {optimizer.g_best.target.fitness}")
