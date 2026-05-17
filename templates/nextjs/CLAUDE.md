# [Project Name]

## Project Overview
[1–2 sentences: what this project does and who it's for.]

## Tech Stack
- **Framework:** Next.js 15 (App Router)
- **Language:** TypeScript (strict mode)
- **Styling:** Tailwind CSS v4
- **UI Components:** [shadcn/ui | Radix UI | custom]
- **State Management:** [Zustand | Jotai | React Context | none]
- **Database:** [PostgreSQL | MySQL | SQLite] via Prisma
- **Auth:** [NextAuth.js | Clerk | Auth.js | none]
- **Deployment:** Vercel

## Commands
```bash
npm run dev        # Start dev server at http://localhost:3000
npm run build      # Production build
npm run start      # Run production build locally
npm run lint       # ESLint + type check
npm run typecheck  # TypeScript check only (tsc --noEmit)
npm test           # Run tests
npm run test:watch # Tests in watch mode
```

## Project Structure
```
├── app/                    # App Router
│   ├── (auth)/             # Auth route group
│   ├── (dashboard)/        # Dashboard route group
│   ├── api/                # Route handlers (route.ts)
│   ├── layout.tsx          # Root layout
│   └── page.tsx            # Home page
├── components/
│   ├── ui/                 # shadcn/ui components (do not edit)
│   └── [feature]/          # Feature-specific components
├── lib/
│   ├── db.ts               # Prisma client singleton
│   ├── auth.ts             # Auth configuration
│   └── utils.ts            # Shared utilities (includes cn())
├── hooks/                  # Custom React hooks
├── types/                  # TypeScript type definitions
├── public/                 # Static assets
└── prisma/
    └── schema.prisma       # Database schema
```

## Key Files
- `next.config.ts` — Next.js config, env validation, rewrites
- `tailwind.config.ts` — Tailwind theme, custom colours, animations
- `middleware.ts` — Auth guards, redirects, rate limiting
- `lib/db.ts` — Prisma client singleton (use this, never import PrismaClient directly)
- `lib/utils.ts` — Contains `cn()` for className merging (clsx + tailwind-merge)

## Code Conventions

### Components
- **Server Components by default.** Only add `"use client"` when using event handlers, hooks, or browser APIs
- **Named exports only** — no default exports for components
- Props interface: `[ComponentName]Props` in the same file
- One component per file; filename matches component name (PascalCase)

### TypeScript
- Strict mode enabled — never use `any`, use `unknown` and narrow types
- Prefer `interface` over `type` for object shapes
- Use `satisfies` operator for config objects
- Use `zod` for runtime validation of external data (API responses, form inputs)

### File naming
- Components: `PascalCase.tsx`
- Utilities/hooks: `camelCase.ts`
- Route files: `route.ts`, `page.tsx`, `layout.tsx` (Next.js conventions)
- Test files: `ComponentName.test.tsx` colocated with component

### API Routes
- Always validate request body with zod before using
- Return typed responses with consistent error format: `{ error: string, details?: unknown }`
- Use `NextResponse.json()` with explicit status codes
- Put business logic in `lib/` functions, not inline in route handlers

## Do NOT
- Use `useEffect` for data fetching — use Server Components or React Query
- Import `PrismaClient` directly — use the singleton from `lib/db.ts`
- Use `any` type — fix the type properly
- Put business logic in route handlers — move to `lib/` service functions
- Use `<img>` — use Next.js `<Image>` component
- Use `<a>` for internal links — use Next.js `<Link>`
- Modify files in `components/ui/` — regenerate from shadcn CLI instead
- Default export components

## Testing
- Framework: Vitest + React Testing Library
- Test files: colocated with components (`*.test.tsx`)
- Coverage target: 80% for `lib/` utilities; test critical user flows
- Before every commit: `npm run typecheck && npm run lint && npm test`

## Environment Variables
See `.env.example` for all required variables.

```
# Required
DATABASE_URL=          # PostgreSQL connection string
NEXTAUTH_SECRET=       # Random 32+ char string
NEXTAUTH_URL=          # Full deployment URL (https://yourdomain.com)

# Optional
NEXT_PUBLIC_APP_URL=   # Public base URL (accessible in browser)
```

- **Public** (prefix `NEXT_PUBLIC_`): accessible in browser bundle
- **Private**: server-only — never expose to client code

## Source Links
- **Repository:** [Link to your project's GitHub/GitLab/etc. repository]
- **License:** [MIT | Apache 2.0 | GPLv3 | etc.]

## Key Features
- [Feature 1: Describe a standout aspect or architectural pattern]
- [Feature 2: Highlight a unique solution or integration]
- [Feature 3: Mention specific educational value or advanced techniques]

## Project Status
[Active development | Maintenance mode | Archived]
