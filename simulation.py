import csv
import random
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple


@dataclass(frozen=True)
class SimulationParams:
    prey_name: str = "Rabbits"
    predator_name: str = "Foxes"
    prey_start: int = 120
    predator_start: int = 25
    prey_growth_rate: float = 0.25
    predation_rate: float = 0.015
    predator_efficiency: float = 0.006
    predator_death_rate: float = 0.12
    noise_fraction: float = 0.05
    generations: int = 10
    seed: int = 42


def clamp_population(value: float) -> int:
    return max(0, int(round(value)))


def simulate(params: SimulationParams) -> List[Tuple[int, int, int]]:
    rng = random.Random(params.seed)
    prey = params.prey_start
    predators = params.predator_start
    results: List[Tuple[int, int, int]] = []

    for generation in range(1, params.generations + 1):
        birth_noise = rng.uniform(-params.noise_fraction, params.noise_fraction)
        predation_noise = rng.uniform(-params.noise_fraction, params.noise_fraction)

        prey_births = prey * params.prey_growth_rate * (1 + birth_noise)
        prey_eaten = prey * params.predation_rate * predators * (1 + predation_noise)

        predator_births = prey_eaten * params.predator_efficiency
        predator_deaths = predators * params.predator_death_rate

        prey = clamp_population(prey + prey_births - prey_eaten)
        predators = clamp_population(predators + predator_births - predator_deaths)

        results.append((generation, prey, predators))

    return results


def write_csv(path: Path, rows: List[Tuple[int, int, int]]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["generation", "prey_population", "predator_population"])
        writer.writerows(rows)


def main() -> None:
    params = SimulationParams()
    results = simulate(params)
    write_csv(Path("results.csv"), results)

    print("generation,prey_population,predator_population")
    for row in results:
        print(f"{row[0]},{row[1]},{row[2]}")


if __name__ == "__main__":
    main()
