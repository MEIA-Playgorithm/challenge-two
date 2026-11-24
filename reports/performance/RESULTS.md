# Player and starting-lineup results

We select models on 2024–25 and evaluate once on 2025–26. Training uses 2019–20 through 2023–24.

Player model: `ridge_1`. Errors are in each statistic's units.

| Target | Test MAE | Last-10 baseline MAE |
| --- | ---: | ---: |
| points | 4.643 | 4.671 |
| rebounds_total | 1.931 | 1.936 |
| assists | 1.371 | 1.376 |

Starting-lineup model: `0_100.0`.
Test margin RMSE: 15.503 points; home-mean baseline: 16.407.

Accepted 7,054 games; excluded 1,229 games with invalid or missing starters.

These are associations with full-game outcomes, not estimates of shared on-court performance.
Bench players, opponents and coaching affect these outcomes. Coefficients do not establish individual causal value.
Player predictions assume participation and at least five earlier appearances in the season.
Observed starters are supplied retrospectively; availability before tip-off is not verified.

See [the method guide](../../docs/PERFORMANCE_EVALUATION.md) for definitions and reproducible commands.
