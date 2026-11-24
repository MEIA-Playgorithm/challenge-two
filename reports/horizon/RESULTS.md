# Multi-game plan

Team: 1610612738. Planning cutoff: 2026-04-01.
Target: 2 wins in 3 games. Expected wins: 2.062.
Probability of reaching the target: 77.1%, assuming independent outcomes.
Candidate selection status: **OPTIMAL**.

| Game | Date | Win probability | Selected minute cap | Plan |
| --- | --- | ---: | ---: | --- |
| 1 | 2026-04-01 | 59.5% | 32 | [Minutes](game_01/minutes.csv), [rotation](game_01/rotation.png) |
| 2 | 2026-04-03 | 78.4% | 32 | [Minutes](game_02/minutes.csv), [rotation](game_02/rotation.png) |
| 3 | 2026-04-05 | 68.3% | 32 | [Minutes](game_03/minutes.csv), [rotation](game_03/rotation.png) |

Each player is limited to 96 minutes over this horizon.
Consecutive-day games have a combined 64-minute limit per player.
The minute limits cover listed games only. Include every team fixture in the horizon.
The plan does not claim to increase these win probabilities. Rotation utility and win forecasts are separate outputs.
Replan after each completed game with updated data and availability.

See [the integration guide](../../docs/HORIZON_PLANNING.md) for assumptions, module contracts and commands.
