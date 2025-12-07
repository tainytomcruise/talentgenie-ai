# HR-LLM-Enabled-Assistant (frontend)

This repository contains the frontend demo of an HR-focused platform that will integrate large language models (LLMs) in later iterations. The demo is built with Vue 3 and Vite and uses hardcoded/dummy data to demonstrate UI and interaction flows.

## Current status

- Frontend-only demo (no backend integration yet).
- Built with Vue 3, Vite and Tailwind CSS.
- Several dashboard views and components implemented (Admin and Employee flows).
- Active work: polishing UI and branding (NavBar / SideBar updated to display the TalentGenie name and login lightning icon in the sidebar).

## Notable recent changes

- Login, logout and registration implemented alongside SQLite3 and Flask scaffolding

These changes are UI-only and affect `frontend/src/components/SideBar.vue` and `frontend/src/components/NavBar.vue`.

## Prerequisites
- Node.js (v16 or higher)
- npm (v7 or higher)
- Python (v3.14 or higher)

## Quick start (Windows - cmd)

Open a Windows command prompt and navigate to the project root. Run the following set of commands in separate terminals:

```cmd
python -m venv .env
.env\Scripts\activate.bat
pip install -r requirements.txt
python main.py
```

```cmd
cd frontend
npm install
npm run dev
```

Vite will start and print the local URL (usually `http://localhost:5173` or similar). Open that URL in your browser.

## Project structure (relevant parts)

- `frontend/src/components/` — shared UI components (NavBar, SideBar, icons, etc.)
- `frontend/src/views/` — page views, e.g., LoginView.vue, WellnessView.vue, AdminDashboard.vue, LoginView.vue
- `frontend/src/router/index.js` — Vue Router configuration and application routes
- `frontend/package.json` — frontend dependencies and scripts

## Tech stack

- Vue 3
- Vite
- Vue Router
- Tailwind CSS
- ApexCharts
- FontAwesome (icons)

## License

See the `LICENSE` file in the repository root.

---
