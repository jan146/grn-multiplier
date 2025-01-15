from mealpy.utils.agent import Agent
import grn
from typing import Any
from mealpy import MixedSetVar
from mealpy.evolutionary_based.DE import JADE
from src.multipliers import get_four_bit_multiplier, to_structured_output_multiplier_specific
from src.utils import run_grn
import numpy.typing as npt
import numpy as np
import time

SEED: int = 123
DE_EPOCH: int = 10
DE_POP_SIZE: int = 50

PARAM_KD_VALUES: npt.NDArray = np.linspace(3, 5, 100)
PARAM_N_VALUES: npt.NDArray = np.arange(2, 3+1)
PARAM_ALPHA_VALUES: npt.NDArray = np.linspace(8, 12, 100)
PARAM_DELTA_VALUES: npt.NDArray = np.linspace(0.05, 0.30, 100)

def params_to_accuracy(param_kd: float, param_n: float, param_alpha: float, param_delta: float):
    four_bit_multiplier: grn.grn = get_four_bit_multiplier(param_kd, param_n, param_alpha, param_delta)
    results = run_grn(four_bit_multiplier)
    _, accuracy = to_structured_output_multiplier_specific(
        simulation_results=results,
        operand_1_inputs=["M_X3", "M_X2", "M_X1", "M_X0"],
        operand_2_inputs=["M_Y3", "M_Y2", "M_Y1", "M_Y0"],
        outputs=["M_Z7", "M_Z6", "M_Z5", "M_Z4", "M_Z3", "M_Z2", "M_Z1", "M_Z0"],
    )
    return accuracy

def four_bit_multiplier_optimization():
    invocation_counter: int = 0
    mixed_set_var: MixedSetVar = MixedSetVar(valid_sets=[PARAM_KD_VALUES, PARAM_N_VALUES, PARAM_ALPHA_VALUES, PARAM_DELTA_VALUES])
    def obj_func(solution: npt.NDArray):
        nonlocal invocation_counter, mixed_set_var
        param_kd: float = float(mixed_set_var.valid_sets[0][int(solution[0])])
        param_n: int = int(mixed_set_var.valid_sets[1][int(solution[1])])
        param_alpha: float = float(mixed_set_var.valid_sets[2][int(solution[2])])
        param_delta: float = float(mixed_set_var.valid_sets[3][int(solution[3])])
        t0: float = time.time()
        accuracy: float = params_to_accuracy(param_kd, param_n, param_alpha, param_delta)
        invocation_counter += 1
        print(f"{invocation_counter+1:d}: {param_kd=}, {param_n=}, {param_alpha=}, {param_delta=} -> {accuracy=} ({time.time() - t0:.1f}s)")
        return accuracy
    problem: dict[str, Any] = {
        "obj_func": obj_func,
        "bounds": mixed_set_var,
        "minmax": "max",
        "log_to": "console",
    }
    model: JADE = JADE(epoch=DE_EPOCH, pop_size=DE_POP_SIZE)
    agent: Agent = model.solve(problem, seed=SEED)
    solution: list[float] = [float(x) for x in agent.solution]
    fitness: float = float(agent.target.fitness)
    print(f"Best solution: {solution}, Best fitness: {fitness}")
    print()

def main():
    four_bit_multiplier_optimization()

if __name__ == "__main__":
    main()

