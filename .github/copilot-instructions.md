## Purpose
Short, actionable guidance for AI coding agents working in this repository (frontend-first Vue 3 app).

## Quick facts (one-liners)
- Framework: Vue 3 + Vite (frontend lives in `frontend/`).
- State: Pinia stores (see `frontend/src/stores/`).
- Routing: `frontend/src/router/index.js` (lazy-loads `AboutView.vue`).
- Styling: Tailwind + local CSS in `frontend/src/assets/main.css` and `frontend/src/App.vue` imports `main.css`.
- Build/dev: run scripts from `frontend/package.json` (see examples below).

## Contract for changes you will make
- Inputs: small, focused PRs touching `frontend/` only unless a backend is added.
- Outputs: runnable UI using `npm run dev` and passing ESLint autofix for changed files.
- Error modes: when routing/components fail, check `frontend/src/router` and the component export (Options vs Composition API).

## How to run (developer workflow)
1. cd into the frontend folder:

```bash
cd frontend
npm install
npm run dev     # start dev server (Vite)
npm run build   # production build
npm run lint    # lint and auto-fix where possible
```

Notes: `package.json` specifies a Node engine (`node` >= 20.19 or >= 22.12). Use the project's Node version to avoid dependency issues.

## Key architecture & patterns (what I should know)
- Entry: `frontend/src/main.js` mounts the app, registers Pinia and router, and imports global CSS and FontAwesome.
- Routing: `frontend/src/router/index.js` defines routes. Follow its structure for new pages (example: add a route and point to `views/MyView.vue`).
- Stores: Pinia is used with the setup-style `defineStore` (see `frontend/src/stores/counter.js`). Prefer this style for new stores.
- Components: `frontend/src/components/` holds reusable UI pieces; `views/` contains route-level pages. Components use both Composition API (`<script setup>`) and Options API — be consistent within a single component.
- Lazy-loading: The About route demonstrates dynamic import for code-splitting — continue this pattern for non-critical pages.

## Project-specific conventions and gotchas
- Mixed API: Some files use `<script setup>` (Composition API) and some use Options API (e.g., `LoginView.vue`). When editing, do not accidentally convert the component style unless the change is intentional.
- Demo behavior: `LoginView.vue` accepts any credentials and shows a browser alert. Fix or extend only when adding auth integration.
- CSS: Tailwind classes are used heavily; prefer utility classes for layout, but you may add scoped CSS in the view when necessary.
- Static assets: global CSS is `frontend/src/assets/main.css`; FontAwesome is included in `main.js`.

## Examples (common tasks)
- Add a new page and route:
  1. Create `frontend/src/views/MyPage.vue`.
  2. Import it or add an async route in `frontend/src/router/index.js`.

- Create a new Pinia store (setup-style example): see `frontend/src/stores/counter.js`.

## Linting & formatting
- Run `npm run lint` to auto-fix many issues. Prettier is configured; run `npm run format` to apply formatting to `src/`.

## Integration points & dependencies
- No backend code present in this repo slice — changes should not assume a backend exists.
- External libs used: `pinia`, `vue-router`, `tailwindcss`, `@fortawesome/fontawesome-free` (refer to `frontend/package.json`).

## Where to look when things fail
- Dev server errors: check console where `vite` runs and browser DevTools. Ensure Node version matches `package.json` engines.
- Component render errors: inspect `frontend/src/router` and the component's default export or `<script setup>` block.
- State bugs: check Pinia stores under `frontend/src/stores`.

## What NOT to do
- Do not introduce backend assumptions or add server-side code under `frontend/`.
- Avoid sweeping, stylistic rewrites across many files in a single PR — prefer focused changes.

---
If any of the above is unclear or you want more examples (sample PRs, tests, or a tiny end-to-end run), tell me which area to expand.
