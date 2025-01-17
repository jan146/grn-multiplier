from typing import cast
import pandas as pd
import sys
import math
import matplotlib.pyplot as plt

SPACE_SIZE_COEFFICIENT: float = 20.0
HSPACE: float = 0.5
WSPACE: float = 0.0
FIG_SIZE_W: int = 16
FIG_SIZE_H: int = 20
FIG_DPI: int = 100
FONTSIZE_TITLE: int = 14
FONTSIZE_AXIS_LABELS: int = 12
FONTSIZE_TICK_LABELS: int = 12

def read_to_dataframe(filename: str) -> pd.DataFrame:
    data: list[dict[str, float]] = []
    with open(filename, "rt") as file:
        while (line := file.readline().strip()):
            line = "".join(line.split(":")[1:])
            params, accuracy = tuple(line.split("->"))
            params, accuracy = params.strip(), accuracy.strip()
            data_point: dict[str, float] = {}
            for param_str in params.split(","):
                param_str = param_str.strip()
                param_name, param_value = param_str.split("=")
                data_point[param_name] = float(param_value)
            accuracy = float(accuracy.split("=")[1])
            data_point["accuracy"] = accuracy
            data.append(data_point)
    return pd.DataFrame(data)

def get_single_plot_data(content: pd.DataFrame, alpha: int, delta: float, param_kd_values: list[int], param_n_values: list[int]) -> list[list[bool]]:
    plot_data: list[list[bool]] = []
    for kd in param_kd_values:
        line: list[bool] = []
        for n in param_n_values:
            accuracy: float = content[
                (content["param_alpha"] == alpha) &
                (abs(content["param_delta"] - delta) < 1e-5) &
                (content["param_kd"] == kd) &
                (content["param_n"] == n)
            ].iloc[0].accuracy
            line.append(bool(accuracy >= 1.0))
        plot_data.append(line)
    return plot_data

def main():

    if len(sys.argv) < 2:
        print("Usage: python -m src.analysis out.array-2.txt")
        exit(1)
    # Read file and find working combinations
    filename: str = sys.argv[1]
    content: pd.DataFrame = read_to_dataframe(filename)
    working_combinations: pd.DataFrame = cast(pd.DataFrame, content[content["accuracy"] >= 1.0])
    mean: pd.Series = cast(pd.Series, working_combinations.mean())
    mean_adjusted_std: pd.Series = working_combinations.std() / working_combinations.mean()

    # Get min and max values for the dimensions of each parameter
    param_kd_min, param_kd_max = math.ceil(mean.param_kd - (SPACE_SIZE_COEFFICIENT/2.0*mean_adjusted_std.param_kd)), math.floor(mean.param_kd + (SPACE_SIZE_COEFFICIENT/2.0*mean_adjusted_std.param_kd))
    param_n_min, param_n_max = math.ceil(mean.param_n - (SPACE_SIZE_COEFFICIENT/2.0*mean_adjusted_std.param_n)), math.floor(mean.param_n + (SPACE_SIZE_COEFFICIENT/2.0*mean_adjusted_std.param_n))
    param_alpha_min, param_alpha_max = math.ceil(mean.param_alpha - (SPACE_SIZE_COEFFICIENT/2.0*mean_adjusted_std.param_alpha)), math.floor(mean.param_alpha + (SPACE_SIZE_COEFFICIENT/2.0*mean_adjusted_std.param_alpha))
    param_delta_min, param_delta_max = float(mean.param_delta - (SPACE_SIZE_COEFFICIENT/20.0*mean_adjusted_std.param_delta)), float(mean.param_delta + (SPACE_SIZE_COEFFICIENT/20.0*mean_adjusted_std.param_delta))
    param_delta_min, param_delta_max = math.ceil(10*max(0, param_delta_min)), math.floor(10*param_delta_max)
    
    param_kd_min, param_kd_max = max(int(content.min().param_kd), param_kd_min), min(int(content.max().param_kd), param_kd_max)
    param_n_min, param_n_max = max(int(content.min().param_n), param_n_min), min(int(content.max().param_n), param_n_max)
    param_alpha_min, param_alpha_max = max(int(content.min().param_alpha), param_alpha_min), min(int(content.max().param_alpha), param_alpha_max)

    if param_kd_max - param_kd_min < 1:
        param_kd_min, param_kd_max = math.floor(mean.param_kd), math.ceil(mean.param_kd)
    if param_n_max - param_n_min < 1:
        param_n_min, param_n_max = math.floor(mean.param_n), math.ceil(mean.param_n)
    if param_alpha_max - param_alpha_min < 1:
        param_alpha_min, param_alpha_max = math.floor(mean.param_alpha), math.ceil(mean.param_alpha)
    if param_delta_max - param_delta_min < 1:
        param_delta_min, param_delta_max = math.floor(10*mean.param_delta), math.ceil(10*mean.param_delta)
        if param_delta_min == param_delta_max:
            param_delta_max += 1

    # Get all possible values for each parameter
    param_kd_values: list[int] = list(range(param_kd_min, param_kd_max+1))
    param_n_values: list[int] = list(range(param_n_min, param_n_max+1))
    param_alpha_values: list[int] = list(range(param_alpha_min, param_alpha_max+1))
    param_delta_values: list[float] = list(map(lambda x: x/10.0, range(param_delta_min, param_delta_max+1)))

    # Prepare plots
    fig, axs = plt.subplots(nrows=len(param_delta_values), ncols=len(param_alpha_values))
    fig.set_dpi(FIG_DPI)
    fig.tight_layout()
    fig.set_size_inches(FIG_SIZE_W, FIG_SIZE_H)
    plt.subplots_adjust(wspace=WSPACE, hspace=HSPACE)
    for i, delta in enumerate(param_delta_values):
        for j, alpha in enumerate(param_alpha_values):
            plot_data: list[list[bool]] = get_single_plot_data(content, alpha, delta, param_kd_values, param_n_values)
            axs[i, j].imshow(plot_data, extent=[min(param_n_values), max(param_n_values)+1, min(param_kd_values), max(param_kd_values)+1])
            axs[i, j].set_title(f"{alpha=}, {delta=}", fontsize=FONTSIZE_TITLE)
            axs[i, j].set_xlabel(f"n", fontsize=FONTSIZE_AXIS_LABELS)
            axs[i, j].set_ylabel(f"kd", fontsize=FONTSIZE_AXIS_LABELS)
            axs[i, j].set_xticks([x+0.5 for x in param_n_values])
            axs[i, j].set_yticks([y+0.5 for y in param_kd_values])
            axs[i, j].set_xticklabels(param_n_values)
            axs[i, j].set_yticklabels(param_kd_values)
            axs[i, j].tick_params(axis="x", labelsize=FONTSIZE_TICK_LABELS)
            axs[i, j].tick_params(axis="y", labelsize=FONTSIZE_TICK_LABELS)
            axs[i, j].set_xlim(min(param_n_values), max(param_n_values)+1)
            axs[i, j].set_ylim(min(param_kd_values), max(param_kd_values)+1)
    plt.show()

if __name__ == "__main__":
    main()
