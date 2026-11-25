# Frontend

The frontend is a single-page app for the Playgorithm coach management system. We build it with React, Vite, [Mantine](https://mantine.dev) and `react-router`. Mantine is open source (MIT licence). The Vite setup and the `/health` plugin follow challenge-one.

## Run with Docker

From the repository root, run:

```bash
docker compose up -d --build frontend
```

Open [http://localhost:4173](http://localhost:4173). `GET /health` at the same address returns `{"status": "ok"}`. The header shows whether the backend answers.

## Run on your computer

You need Node.js 22.22 or newer.

1. Go to the folder: `cd frontend`
2. Install the dependencies: `npm ci`
3. Start the development server: `npm run start:dev`

The server reloads the page when you change a file. `npm run dev` does the same. Vite prints the address, normally [http://localhost:5173](http://localhost:5173). To build for production, run `npm run build`.

## Configure the frontend

The backend address comes from the Vite variable `VITE_API_URL`. The default is `http://localhost:8000`. The app reads it in `src/config/env.ts`.

To change the address on your computer:

1. Go to the folder: `cd frontend`
2. Copy the example file: `cp .env.example .env` (on Windows PowerShell: `Copy-Item .env.example .env`)
3. Edit `VITE_API_URL` in `.env`.

Vite reads the variable at build time. After you change it, restart the development server or run `npm run build` again.

In Docker, `VITE_API_URL` is a build argument. Set it in `docker-compose.yaml` under `frontend.build.args`, then rebuild with `docker compose up -d --build frontend`.

Do not commit `.env`. The `.env.example` file is safe to commit.

## Code organisation

```
src/
  main.tsx              renders App
  app/App.tsx           MantineProvider and the router
  theme/theme.ts        colours, design tokens and component defaults
  config/env.ts         reads VITE_API_URL, the backend address
  config/navigation.ts  the single list of pages
  api/                  backend calls; routes.ts lists every backend route
  hooks/                logic, for example useBackendHealth
  components/
    <Name>/             one folder for each shared component, for example BackendStatus
    layout/<Name>/      one folder for each layout component, for example AppLayout and Footer
  pages/
    <Name>Page/         one folder for each page: HomePage, PredictionsPage, PlanningPage, NotFoundPage
```

Each component folder holds its `*.tsx` file and, when needed, its `*.module.css` file.

`config/navigation.ts` is the single list of pages. The router, the breadcrumbs and the landing cards read it. The header has no navigation links and no mobile menu. You reach pages from the landing cards.

The app has a landing page (`/`) and 2 placeholder pages: Predictions (`/predictions`) and Planning (`/planning`).

Rules for the code:

- Use Mantine components, the theme and style props as much as possible.
- Keep colours and design tokens only in `theme/theme.ts`. The theme exposes them as CSS variables through `cssVariablesResolver`.
- Set component defaults in the theme with `X.extend(...)`.
- Put other custom CSS for one component in a CSS module next to that component. Use Mantine or theme CSS variables in it.
- Write no `style={{}}`, no `styles={{}}` and no raw colour values in JSX. Mantine spacing and layout props such as `p`, `mt`, `gap` and `c="dimmed"` are fine.
- Use the team blog (playgorithm.blogspot.com) colours in a dark scheme: page background `#061713`, cards `#0f1e1b` with a thin mint border, mint accent `#2ef2b3`, white text and dimmed text `#8fb3a9`. Set them in `theme/theme.ts`.
- Take only the layout and feel from Apple design: a calm layout, whitespace, a large radius and the system font stack.
- Keep the header simple. It is sticky, translucent and blurred. It shows the breadcrumbs ("Playgorithm › Page") on the left and the backend status on the right. The first crumb links home. Add no header links, no mobile menu and no separate breadcrumbs row.
- To add a page, create `pages/<Name>Page/<Name>Page.tsx`, add one entry to `config/navigation.ts` and add its path and element to the `elements` object in `app/App.tsx`. TypeScript reports an error if a page has no element. Do not add a `Route`, because `App.tsx` builds the routes from `pages`.
- Draw in components and put the logic in hooks.
- Send every HTTP call through `api/`, and write every route in `api/routes.ts`.
- Read the backend address from `config/env.ts` (`VITE_API_URL`). Never hard-code a URL.
