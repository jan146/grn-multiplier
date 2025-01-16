from typing import cast
import grn
from src.multipliers import get_array_multiplier, to_structured_output_multiplier_specific
from src.utils import InputList, OutputList, run_grn
import itertools
import multiprocessing
import os

N_WORKERS: int = cast(int, os.cpu_count())

PARAM_KD_VALUES: list[int] = list(range(2, 10+1))
PARAM_N_VALUES: list[int] = list(range(2, 10+1))
PARAM_ALPHA_VALUES: list[int] = list(range(5, 15+1))
PARAM_DELTA_VALUES: list[float] = list(map(lambda x: x/10.0, range(10)))

def get_multiplier_accuracy(multiplier: grn.grn, size: int) -> float:
    results: list[tuple[InputList, OutputList]] = run_grn(multiplier)
    _, accuracy = to_structured_output_multiplier_specific(
        simulation_results=results,
        operand_1_inputs=[f"M_X{i}" for i in reversed(range(size))],
        operand_2_inputs=[f"M_Y{i}" for i in reversed(range(size))],
        outputs=[f"M_Z{i}" for i in reversed(range(2*size))],
    )
    return accuracy

def print_multiplier_accuracy(params: tuple[int|float,...]) -> float:
    size, param_kd, param_n, param_alpha, param_delta = params
    array_multiplier: grn.grn = get_array_multiplier(
        size=int(size),
        param_kd=param_kd,
        param_n=param_n,
        param_alpha=param_alpha,
        param_delta=param_delta,
    )
    accuracy: float = get_multiplier_accuracy(array_multiplier, int(size))
    print(f"{param_kd=:02d}, {param_n=:02d}, {param_alpha=:02d}, {param_delta=:.3f} -> {accuracy=:0.1f}")
    return accuracy

def grid_search(size: int):
    param_grid: list[tuple[int|float,...]] = list(itertools.product([size], PARAM_KD_VALUES, PARAM_N_VALUES, PARAM_ALPHA_VALUES, PARAM_DELTA_VALUES))
    with multiprocessing.Pool(processes=N_WORKERS) as pool:
        results: list[float] = pool.map(print_multiplier_accuracy, param_grid)

def main():
    grid_search(size=2)

if __name__ == "__main__":
    main()

