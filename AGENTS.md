# AGENTS.md

This file tells AI (artificial intelligence) coding agents how to work in this repository. Read it before you change anything. The [README](README.md) explains the project for people.

## What this project is

Playgorithm challenge two is an academic machine learning project. It uses NBA (National Basketball Association) data to build a simple management system for basketball coaches. The system has 3 parts:

1. **Data and ML (machine learning):** Python scripts prepare the data, predict game results and player performance, and plan rotations and substitutions.
2. **Backend:** a FastAPI service that will expose the predictions and decisions.
3. **Frontend:** a React single-page app for coaches.

## Find your way around

| Folder or file | What it holds |
|---|---|
| `backend/` | FastAPI service, managed with uv. Read the [backend README](backend/README.md). |
| `frontend/` | React, Vite and Mantine app. Read the [frontend README](frontend/README.md). |
| `docker-compose.yaml` | Runs the backend (port 8000) and the frontend (port 4173). |
| `scripts/` | Data preparation, ML training and planning scripts. |
| `tests/` | Unit tests for `scripts/`. |
| `docs/` | Guides for the data and for each ML element. |
| `reports/` | Results of the ML experiments. Scripts write them. |
| `data/archive/` | The data as a split zip. `data/unzip.sh` and `data/unzip.ps1` rebuild `data/csv/`. |
| `latex/` | The written report, in Portuguese. |
| `notebooks/` | Data exploration notebooks. |
| `.claude/skills/` | Project rules for branches, commits and documentation. |

## Run and check the code

### Backend

Run these commands from `backend/`:

| Task | Command |
|---|---|
| Install dependencies | `uv sync` |
| Start the server with auto-reload | `uv run src/main.py --dev` |
| Run the tests | `uv run pytest` |
| Find lint errors | `uv run ruff check .` |
| Check the formatting | `uv run ruff format --check .` |

### Frontend

Run these commands from `frontend/`. You need Node.js 22.22 or newer:

| Task | Command |
|---|---|
| Install dependencies | `npm ci` |
| Start the development server | `npm run start:dev` (same as `npm run dev`) |
| Type check and build | `npm run build` |

### Whole stack

From the repository root, run `docker compose up -d --build`. Open the frontend at http://localhost:4173 and the API at http://localhost:8000/docs.

### Data and ML scripts

Run these commands from the repository root, inside the root `.venv`:

| Task | Command |
|---|---|
| Install dependencies | `python -m pip install -r requirements.txt` |
| Run the tests | `python -m unittest discover -s tests` |

The scripts need Python 3.11 or newer. Most scripts also need `data/processed/`, which `scripts/prepare_data.py` creates from `data/csv/`.

## Before you finish a change

Run the checks for every part you changed. A change is done only when all of them pass:

- **Backend:** `uv run ruff check .`, `uv run ruff format --check .` and `uv run pytest`.
- **Frontend:** `npm run build`.
- **Scripts:** `python -m unittest discover -s tests`.

### Test in the running app

Test every change in the running app. Use Docker (`docker compose up -d --build`) or the development servers:

- **Backend:** `uv run src/main.py --dev`
- **Frontend:** `npm run start:dev`

If the user already runs the backend or the frontend in a terminal, use that instance. Do not start a second one. Lint and build checks alone do not count as a test.

## Write backend code

The backend uses a layered architecture. Each layer calls only the layers below it:

```
api/routes  →  services  →  repositories  →  domain
```

| Layer | Folder | Rules |
|---|---|---|
| API | `src/api/routes/`, `src/api/schemas/` | Translate HTTP (Hypertext Transfer Protocol) into service calls. Hold no business rules. Give every route a response schema. |
| Services | `src/services/` | Hold the business rules, predictions and decisions. Never import FastAPI. |
| Repositories | `src/repositories/` | Read and write data: CSV (comma-separated values) files, trained models. Return domain objects. |
| Domain | `src/domain/` | Frozen dataclasses. Import nothing from the other layers. |
| Core | `src/core/` | Settings, read from environment variables, including `APP_HOST` and `APP_PORT`. They can come from `backend/.env` (copy `backend/.env.example`). Every layer may use it. |
| Composition root | `src/app.py` | Builds the app and every object by hand in `create_app(settings)`. Creates no app instance. |
| Entry point | `src/main.py` | Creates the one app instance with `create_app(settings)` and starts the server. Uses the host and port from the settings. Passes the `app` object to uvicorn, or `"main:app"` with `--dev` so uvicorn can reload. Docker runs it with `python src/main.py`. Holds no wiring. |

Follow these rules:

- **Keep the code plain.** Use no metaprogramming: no metaclasses, no `setattr` or `getattr` tricks, no dynamic imports, no monkey patching and no clever decorators.
- **Wire by hand.** Pass every dependency through the constructor. `src/app.py` creates every object in `create_app(settings)`, so the whole wiring sits in that function. `src/main.py` calls it once to create the one app instance. Keep `src/main.py` as the command-line entry point only. Do not use FastAPI `Depends` for wiring.
- **Register routes explicitly.** Build each router in a `build_*_router(service)` function and call `router.add_api_route(...)`.
- **Convert with plain functions.** Turn domain objects into schemas with functions such as `to_health_response(...)`.
- **Import from the layer packages.** `src/` is on the Python path, so write `from services.health_service import HealthService`. Never write `from src.`.
- **Respect the ruff rules.** `backend/pyproject.toml` holds a strict rule set. Fix the code, not the config. Add an ignore only when the user agrees.
- **Pin dependencies.** Pin each new runtime dependency with an exact version (`==`). For dev tools, follow the pattern in `pyproject.toml`. Commit `uv.lock`.
- **Test each layer.** Put tests in `backend/tests/`. Import `create_app` from `app` and build the app with `create_app(settings)`, not the `app` instance in `main`.

## Write frontend code

The frontend uses React, Vite, [Mantine](https://mantine.dev) (`@mantine/core` and `@mantine/hooks`) and `react-router`. Mantine is open source (MIT licence). The build and runtime setup (Vite and the `/health` plugin) follows the team's challenge-one project.

Code tree under `frontend/src/`:

| Path | What it holds |
|---|---|
| `main.tsx` | Renders `App`. |
| `app/App.tsx` | `MantineProvider` and the router. Maps over `pages` to build the routes. Its `elements` object links each path to a page component. |
| `theme/theme.ts` | The Mantine theme: colours, design tokens and component defaults. |
| `config/env.ts` | Reads `VITE_API_URL`, the backend address. |
| `config/navigation.ts` | The single list of pages. |
| `api/` | Backend calls. `api/routes.ts` lists every backend route. |
| `hooks/` | The logic, for example `useBackendHealth`. |
| `components/<Name>/` | One folder for each shared component, for example `BackendStatus`. The `*.module.css` file sits next to it. |
| `components/layout/<Name>/` | One folder for each layout component, for example `AppLayout` (the Mantine `AppShell`) and `Footer`. |
| `pages/<Name>Page/` | One folder for each page: `HomePage`, `PredictionsPage`, `PlanningPage` and `NotFoundPage`. |

`config/navigation.ts` is the single list of pages. The router, the breadcrumbs and the landing cards read it. The header has no navigation links and no mobile menu. Users reach pages from the landing cards.

Pages today: a landing page (`/`) and 2 placeholder pages, Predictions (`/predictions`) and Planning (`/planning`).

Follow these rules:

- **Use Mantine first.** Use Mantine components, the theme and style props as much as possible.
- **Follow the styling rules.**
  1. Keep colours and design tokens only in `src/theme/theme.ts`. The theme exposes them as CSS variables through `cssVariablesResolver`.
  2. Set component defaults in the theme with `X.extend(...)`.
  3. Put other custom CSS for one component in a CSS module next to that component. Use Mantine or theme CSS variables in it.
  4. Write no `style={{}}`, no `styles={{}}` and no raw colour values in JSX. Mantine spacing and layout props such as `p`, `mt`, `gap` and `c="dimmed"` are fine.
- **Follow the team blog colours and an Apple-inspired feel.** The colours come from the team blog (playgorithm.blogspot.com) in a dark scheme: page background `#061713`, cards `#0f1e1b` with a thin mint border, mint accent `#2ef2b3`, white text and dimmed text `#8fb3a9`. The Apple inspiration covers the layout and feel only: a calm layout, whitespace, a large radius and the system font stack. Set the colours in `src/theme/theme.ts`. Use a card layout.
- **Keep the header simple.** The sticky header is translucent and blurred. It shows the breadcrumbs ("Playgorithm › Page") on the left and the backend status on the right. The first crumb links home. Add no header links, no mobile menu and no separate breadcrumbs row.
- **Add a page in 3 steps.** Create `src/pages/<Name>Page/<Name>Page.tsx`. Add one entry to `src/config/navigation.ts`. Add its path and element to the `elements` object in `src/app/App.tsx`. TypeScript reports an error if a page has no element. Do not add a `Route`, because `App.tsx` builds the routes from `pages`. The landing page then shows a card for the new page.
- **Separate drawing from logic.** Components draw. Hooks hold the logic. Put every hook in `src/hooks/`, for example `useBackendHealth.ts`.
- **Send every HTTP call through `src/api/`.** Write every route in `src/api/routes.ts`.
- **Read the backend address from `config/env.ts` (`VITE_API_URL`).** Never hard-code a URL. Copy `frontend/.env.example` to `frontend/.env` to change it. Vite reads it at build time.
- **Keep TypeScript strict.** Use no `any`.

## Work with the data

- **Leave the extracted data out of git.** Never commit `data/csv/`, `data/processed/`, `.venv/` or files over 100 MB.
- **Prevent leakage.** Build features only from games on earlier days. Split the data by season.
- **Keep the experiments.** The scripts refuse to overwrite an existing output folder. Choose a new folder rather than deleting old results.

## Branches, commits and documentation

- **Branches:** `development` is the default branch, and `main` holds releases. Work on a `type/task` branch, for example `feature/coach-api`, and merge through a pull request. Read the [branch guide](.claude/skills/branch-naming/SKILL.md).
- **Commits:** Commit only when the user asks. Write messages in English, in the NASA cFS format, for example `Fix #12, Add data overview notebook`. Make one commit per topic. Read the [commit guide](.claude/skills/commit/SKILL.md).
- **Documentation:** Write README files and guides in plain English. Read the [documentation guide](.claude/skills/docs-style/SKILL.md).
- **Secrets:** Never read or commit `.env` files or credentials. The `backend/.env.example` and `frontend/.env.example` files hold no secrets. You may read and commit them.

## Known issues

- **`scripts/prepare_data.py` crashes on Windows at the end of a run.** `inventory()` keys inputs with backslashes, but the cross-source reads use forward slashes. `finish()` then raises `KeyError: 'mtime_ns'`.
- **`tests/test_horizon.py` fails on every system.** The test patches `plan_horizon.build_features`, but it imports `scripts.plan_horizon`, which is a different module object.
