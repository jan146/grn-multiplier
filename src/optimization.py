from mealpy.utils.agent import Agent
import grn
from typing import Any
from mealpy import FloatVar
from mealpy.evolutionary_based.DE import JADE
from src.multipliers import get_four_bit_multiplier, to_structured_output_multiplier_specific
from src.utils import run_grn

SEED: int = 123
DE_EPOCH: int = 10
DE_POP_SIZE: int = 50

PARAM_BOUNDS: dict = {
    "Kd": (3, 5),
    "n": (2, 3),
    "alpha": (8, 12),
    "100delta": (10, 15),   # 0.1 - 0.15
}

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
    def obj_func(solution: Any):
        nonlocal invocation_counter
        param_kd: float = float(solution[0])
        param_n: float = float(solution[1])
        param_alpha: float = float(solution[2])
        param_delta: float = float(solution[3]/100)
        accuracy: float = params_to_accuracy(param_kd, param_n, param_alpha, param_delta)
        invocation_counter += 1
        print(f"{invocation_counter+1:d}: {param_kd=}, {param_n=}, {param_alpha=}, {param_delta=} -> {accuracy=}")
        return accuracy
    problem: dict[str, Any] = {
        "obj_func": obj_func,
        "bounds": FloatVar(
            lb=[PARAM_BOUNDS["Kd"][0], PARAM_BOUNDS["n"][0], PARAM_BOUNDS["alpha"][0], PARAM_BOUNDS["100delta"][0]],
            ub=[PARAM_BOUNDS["Kd"][1], PARAM_BOUNDS["n"][1], PARAM_BOUNDS["alpha"][1], PARAM_BOUNDS["100delta"][1]],
        ),
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

