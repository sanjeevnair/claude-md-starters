# [Project Name]

## Project Overview
[1–2 sentences: what this project does and who it's for.]

## Tech Stack
- **Framework:** React 19
- **Bundler:** Vite 5
- **Language:** TypeScript (strict mode)
- **Styling:** Tailwind CSS v4
- **Routing:** React Router v7
- **State Management:** [Zustand | Jotai | React Context | none]
- **Data Fetching:** [TanStack Query | SWR | fetch]
- **Deployment:** Vercel / Netlify / static host

## Commands
```bash
npm run dev        # Start dev server at http://localhost:5173
npm run build      # Production build (outputs to dist/)
npm run preview    # Preview production build locally
npm run lint       # ESLint check
npm run typecheck  # TypeScript check (tsc --noEmit)
npm test           # Run tests
npm run test:ui    # Tests with Vitest UI
```

## Project Structure
```
├── src/
│   ├── components/         # Shared UI components (PascalCase.tsx)
│   ├── pages/              # Route-level components
│   ├── hooks/              # Custom React hooks (use*.ts)
│   ├── lib/                # Utilities, API clients, helpers
│   ├── store/              # Global state (Zustand stores)
│   ├── types/              # TypeScript type definitions
│   ├── App.tsx             # Root component, router setup
│   └── main.tsx            # Entry point
├── public/                 # Static assets (not processed by Vite)
├── index.html              # HTML entry point
├── vite.config.ts          # Vite config, path aliases, plugins
└── tailwind.config.ts      # Tailwind theme customisation
```

## Key Files
- `vite.config.ts` — Path aliases (`@/` → `src/`), plugins, build config
- `src/lib/api.ts` — API client / base fetch wrapper
- `src/lib/utils.ts` — Shared utilities, `cn()` for class merging

## Code Conventions

### Components
- **Named exports only** — no default exports for components
- Props interface: `[ComponentName]Props` in the same file
- One component per file; filename matches component name (PascalCase)
- Keep components small — extract logic into hooks (`use*.ts`)

### TypeScript
- Strict mode enabled — never use `any`, use `unknown` and narrow
- Prefer `interface` over `type` for object shapes
- Use `zod` for runtime validation of API responses and form data
- Use `@/` path alias for all `src/` imports — no relative `../../../`

### Imports
- Always use `@/` alias for internal imports (e.g., `import { Button } from '@/components/Button'`)
- Group imports: external → internal → types → styles
- No barrel files (`index.ts`) unless the directory has 5+ exports

### State
- Local UI state: `useState` / `useReducer`
- Shared client state: Zustand store in `src/store/`
- Server state: TanStack Query (`useQuery`, `useMutation`)
- Never store server-fetched data in Zustand

## Do NOT
- Use `useEffect` for data fetching — use TanStack Query or SWR
- Use relative `../../../` imports — use `@/` alias
- Default export components
- Use `any` type — fix it properly
- Use `<a>` for internal routes — use React Router `<Link>`
- Mix state management patterns — pick one and stick to it

## Testing
- Framework: Vitest + React Testing Library
- Test files: colocated with components (`*.test.tsx`)
- Coverage: 80% for `lib/` utilities; integration tests for user flows
- Mock external APIs with `msw` (Mock Service Worker)
- Run before commit: `npm run typecheck && npm run lint && npm test`

## Environment Variables
```
VITE_API_URL=         # Backend API base URL
VITE_APP_ENV=         # development | staging | production
```

- All env vars must be prefixed with `VITE_` to be accessible in the browser
- Never put secrets in Vite env vars — they are bundled into the client

## Source Links
- **Repository:** [Link to your project's GitHub/GitLab/etc. repository]
- **License:** [MIT | Apache 2.0 | GPLv3 | etc.]

## Key Features
- [Feature 1: Describe a standout aspect or architectural pattern]
- [Feature 2: Highlight a unique solution or integration]
- [Feature 3: Mention specific educational value or advanced techniques]

## Project Status
[Active development | Maintenance mode | Archived]
