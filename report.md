# EcoSim AI: Modeling Simple Ecosystem Interactions

## Overview
This short, educational simulation follows a small fictional ecosystem where **Rabbits** (prey) and **Foxes** (predators) interact over 10 generations. The model uses simple, agent-like rules with a touch of randomness to illustrate how prey growth and predator dependence can drive population changes over time.

## Assumptions & Rules
- **Prey (Rabbits)** grow each generation by a base rate of 25%.
- **Predators (Foxes)** can only grow when they successfully eat prey.
- **Predation** depends on both prey and predator counts (more of each means more encounters).
- **Predators** lose a fixed portion of their population each generation (natural deaths).
- **Random noise** of ±5% is applied to prey births and predation to mimic variability.
- Populations are **clamped to non-negative integers** after each generation.

## Population Table (10 Generations)
| Generation | Rabbits (Prey) | Foxes (Predators) |
| --- | --- | --- |
| 1 | 108 | 22 |
| 2 | 100 | 20 |
| 3 | 95 | 18 |
| 4 | 95 | 16 |
| 5 | 97 | 14 |
| 6 | 100 | 12 |
| 7 | 106 | 11 |
| 8 | 115 | 10 |
| 9 | 126 | 9 |
| 10 | 142 | 8 |

## Generation-by-Generation Narrative
**Generation 1:** Rabbits drop from their start as predation outpaces births, and foxes decline slightly due to natural deaths. The system settles into a lower but still viable state for both species.

**Generation 2:** Rabbits continue to dip as predation remains significant, and foxes fall again as fewer prey mean fewer new predators.

**Generation 3:** The rabbit population keeps shrinking, and foxes lose another small step, showing the predator population trailing the prey decline.

**Generation 4:** Rabbits stabilize at a similar level, while foxes continue their slow decline because prey intake is no longer enough to offset deaths.

**Generation 5:** Rabbits finally edge upward as predation pressure eases, while foxes drop again, reflecting the delayed effect of fewer prey.

**Generation 6:** Rabbits climb further, benefiting from reduced predation, and foxes decline to a smaller but still present population.

**Generation 7:** With foxes now relatively few, rabbits rebound more clearly, and foxes slip again as prey intake remains modest.

**Generation 8:** Rabbits accelerate their recovery, while foxes continue their steady decrease, illustrating how predator losses can allow prey to bounce back.

**Generation 9:** Rabbit numbers rise into a healthier range, but foxes shrink again due to sustained low birth rates.

**Generation 10:** Rabbits reach their highest level in this run, while foxes end at a small population, highlighting a classic rebound of prey after predator decline.

## What Students Can Learn
- Predator and prey populations often move in opposite directions over time.
- Small changes in prey availability can cascade into predator declines.
- Randomness can nudge outcomes without changing the overall trend.
- Simple rules can produce realistic-looking ecosystem dynamics without being scientifically precise.
