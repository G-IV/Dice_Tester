# Yahtzee Dice Comparison Report

This report compares the ten `six_sided_yahtzee_*` dice stored in the project database and ranks them by how close their observed face distribution is to a fair d6.

## Dataset

- Dice compared: 10
- Rolls per die: 1000
- Total rolls analyzed: 10000
- Primary ranking metric: chi-square goodness-of-fit to a uniform d6 distribution
- Supporting metrics: p-value, total variation distance (TVD), entropy gap, mean shift, repeat rate, and longest streak
- Group-of-5 ranking metric: pooled chi-square/TVD across all rolls from the five selected dice
- Caveat: the group ranking measures pooled balance, not physical independence between dice

## Executive Summary

- Closest single die to random: `10` with chi-square 0.968 and p-value 0.965.
- Weakest single die in this sample: `9` with chi-square 12.656 and p-value 0.027.
- Best five-die group by pooled fairness: `1, 10, 4, 6, 8` with pooled chi-square 1.586, TVD 0.0084, and p-value 0.903.
- The naive "pick the five best individual dice" set is `10, 4, 6, 7, 8`. Its pooled chi-square is 3.062, so the best pooled group improves that by 48.2%.
- All ten dice pooled together still look reasonably balanced: chi-square 9.549, p-value 0.089, TVD 0.0136.

## Ranked Single Dice

| Rank | Die | Chi-square | p-value | TVD | Entropy gap (bits) | Mean | Repeat rate | Longest streak | Strongest bias |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | `10` | 0.968 | 0.965 | 0.0133 | 0.000702 | 3.475 | 16.02% | 4x face 1 | +1 +0.63 pp; -6 -0.87 pp |
| 2 | `6` | 1.088 | 0.955 | 0.0120 | 0.000780 | 3.460 | 15.92% | 4x face 6 | +1 +1.03 pp; -4 -0.77 pp |
| 3 | `4` | 3.008 | 0.699 | 0.0243 | 0.002189 | 3.562 | 16.32% | 4x face 3 | +6 +1.03 pp; -1 -1.37 pp |
| 4 | `8` | 3.092 | 0.686 | 0.0250 | 0.002242 | 3.557 | 16.72% | 4x face 5 | +6 +1.23 pp; -2 -1.37 pp |
| 5 | `7` | 3.932 | 0.559 | 0.0260 | 0.002869 | 3.546 | 16.22% | 4x face 3 | +6 +1.43 pp; -2 -1.87 pp |
| 6 | `1` | 4.916 | 0.426 | 0.0293 | 0.003635 | 3.509 | 15.42% | 5x face 6 | +6 +1.23 pp; -3 -2.27 pp |
| 7 | `5` | 5.744 | 0.332 | 0.0360 | 0.004173 | 3.526 | 16.02% | 5x face 5 | +6 +1.43 pp; -2 -1.87 pp |
| 8 | `3` | 6.320 | 0.276 | 0.0327 | 0.004553 | 3.499 | 16.92% | 4x face 3 | +1 +2.03 pp; -2 -1.97 pp |
| 9 | `2` | 10.292 | 0.067 | 0.0470 | 0.007367 | 3.604 | 15.92% | 5x face 5 | +5 +2.73 pp; -4 -2.07 pp |
| 10 | `9` | 12.656 | 0.027 | 0.0427 | 0.008903 | 3.530 | 16.52% | 5x face 4 | +4 +3.63 pp; -3 -2.47 pp |

## Best Five-Die Groups

| Rank | Dice | Pooled chi-square | p-value | TVD | Mean | Most over/underrepresented faces |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | `1, 10, 4, 6, 8` | 1.586 | 0.903 | 0.0084 | 3.513 | +6 +0.45 pp; -4 -0.37 pp |
| 2 | `10, 4, 6, 8, 9` | 1.646 | 0.896 | 0.0072 | 3.517 | +5 +0.45 pp; -2 -0.47 pp |
| 3 | `1, 10, 4, 6, 7` | 2.121 | 0.832 | 0.0088 | 3.510 | +6 +0.49 pp; -3 -0.43 pp |
| 4 | `1, 10, 4, 5, 6` | 2.435 | 0.786 | 0.0098 | 3.506 | +6 +0.49 pp; -3 -0.45 pp |
| 5 | `10, 4, 5, 6, 8` | 2.714 | 0.744 | 0.0097 | 3.516 | +6 +0.49 pp; -2 -0.71 pp |

## Interesting Metrics

- Closest to the expected mean roll of 3.5: `3` at 3.499.
- Lowest repeat rate: `1` at 15.42% versus the ideal 16.67%.
- Highest repeat rate: `3` at 16.92%.
- Longest run of identical faces: `1` with 5 consecutive `6`s.
- Only one die crosses the common alpha=0.05 rejection threshold on its own: `9` (p-value 0.027).
- The best pooled group includes `1` even though it ranks sixth individually. Its biases complement the top dice better than `7` does.

## Worst Five-Die Group

- Worst pooled set: `1, 3, 5, 7, 9`.
- Pooled chi-square: 16.902
- Pooled p-value: 0.0047
- Pooled TVD: 0.0260

## All Ten Dice Pooled

- Chi-square: 9.549
- p-value: 0.089
- TVD: 0.0136
- Mean roll: 3.5268
- Aggregate bias: +face 6 +0.51 pp, -face 2 -0.91 pp

## Recommendation

- If you want the single best die, pick `10`.
- If you want the most balanced set of five from the ten tested dice, use `1, 10, 4, 6, 8`.
- If you want a conservative shortlist for future re-testing, focus on dice `9` and `2` first, because they show the strongest single-die departures from uniformity in this sample.
