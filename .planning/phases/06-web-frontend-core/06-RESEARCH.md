# Phase 6: Web Frontend Core - Research

**Researched:** 2026-01-24
**Domain:** Modern React web application with Vite, TanStack Query, and shadcn/ui
**Confidence:** HIGH

## Summary

Phase 6 implements a developer-focused web UI for authentication, catalog browsing, and profile viewing. The standard 2026 stack uses Vite for tooling, React with TypeScript for components, TanStack Query for server state, Zustand for client state, and shadcn/ui for UI components with Tailwind CSS.

The established pattern is feature-based organization with centralized API layer, protected routes using React Router loaders, JWT token management with httpOnly cookies, and dark-only theme using CSS variables.

Key findings: Modern React development has shifted toward server state libraries (TanStack Query) instead of storing API data in Redux/Zustand, uncontrolled forms with React Hook Form for performance, and component-driven development with pre-built accessible components (shadcn/ui).

**Primary recommendation:** Use Vite + React + TypeScript with TanStack Query for all API calls, React Hook Form + Zod for forms, Zustand only for UI state (auth status, sidebar state), and shadcn/ui components for consistent dark theme.

## Standard Stack

The established libraries/tools for modern React applications in 2026:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Vite | 6.x | Build tool and dev server | Industry standard for React, 10-100x faster than webpack, native ESM support |
| React | 18.3+ | UI framework | Stable, mature ecosystem, concurrent rendering features |
| TypeScript | 5.x | Type safety | Default for modern React, catches errors at compile time |
| React Router | 6.28+ | Client-side routing | Most popular router, loader pattern for data fetching |
| TanStack Query | 5.x | Server state management | De facto standard for API data (formerly React Query) |
| Zustand | 4.x | Client state management | Lightweight alternative to Redux, no providers needed |
| React Hook Form | 7.x | Form handling | Best performance, uncontrolled by default |
| Zod | 3.x | Schema validation | TypeScript-first validation, pairs with React Hook Form |
| shadcn/ui | latest | Component library | Copy-paste accessible components, full control |
| Tailwind CSS | 4.x | Styling | Utility-first, pairs with shadcn/ui, theme via CSS vars |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| @hookform/resolvers | 3.x | Form validation bridge | Connect Zod schemas to React Hook Form |
| @tanstack/react-query-devtools | 5.x | Query debugging | Development only, visualize cache and queries |
| next-themes | 0.3+ | Dark mode | If using Next.js; for Vite use custom implementation |
| class-variance-authority (CVA) | latest | Component variants | Manage component style variants with Tailwind |
| clsx / tailwind-merge | latest | Class merging | Conditionally combine Tailwind classes |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Vite | Create React App | CRA is deprecated, Vite is 10-100x faster |
| React Router | TanStack Router | TanStack Router has better typing and file-based routing, but React Router is more mature and widely adopted |
| TanStack Query | SWR | SWR is simpler but less feature-rich, TQ has better caching and DevTools |
| Zustand | Redux Toolkit | Redux is more opinionated/boilerplate, use for very large apps with strict patterns |
| React Hook Form | Formik | Formik causes more re-renders (controlled), RHF is more performant |
| shadcn/ui | MUI, Chakra UI, Ant Design | Those are npm packages with opinions; shadcn gives you the source code to modify |

**Installation:**
```bash
# Create Vite project with React + TypeScript
npm create vite@latest frontend -- --template react-ts

# Core dependencies
npm install react-router-dom @tanstack/react-query zustand react-hook-form zod @hookform/resolvers

# shadcn/ui setup (requires Tailwind CSS first)
npm install -D tailwindcss @tailwindcss/vite @types/node
npx shadcn@latest init

# Development tools
npm install -D @tanstack/react-query-devtools
```

## Architecture Patterns

### Recommended Project Structure
```
frontend/
├── public/                 # Static assets
├── src/
│   ├── assets/            # Images, icons, fonts
│   ├── components/        # Reusable UI components
│   │   ├── ui/           # shadcn/ui components (auto-generated)
│   │   ├── layout/       # Layout components (Sidebar, Header)
│   │   └── shared/       # Shared business components
│   ├── features/          # Feature-based modules
│   │   ├── auth/
│   │   │   ├── components/      # Auth-specific components (LoginForm, SignupForm)
│   │   │   ├── api/            # Auth API calls (login, register, logout)
│   │   │   ├── hooks/          # Auth hooks (useAuth, useLogin)
│   │   │   └── types.ts        # Auth TypeScript types
│   │   ├── catalog/
│   │   │   ├── components/      # Catalog components (CatalogCard, FilterTabs)
│   │   │   ├── api/            # Catalog API calls
│   │   │   └── hooks/          # Catalog hooks
│   │   └── profile/
│   ├── lib/               # Utilities and configurations
│   │   ├── api.ts        # Axios/fetch client setup
│   │   ├── queryClient.ts     # TanStack Query client config
│   │   └── utils.ts      # Helper functions
│   ├── stores/            # Zustand stores
│   │   └── authStore.ts  # Auth state (logged in user, tokens)
│   ├── routes/            # Route components
│   │   ├── root.tsx
│   │   ├── auth/
│   │   ├── catalog/
│   │   └── profile/
│   ├── types/             # Global TypeScript types
│   │   └── api.ts        # API response types
│   ├── App.tsx
│   ├── main.tsx
│   └── vite-env.d.ts     # Vite env type definitions
├── components.json        # shadcn/ui config
├── tailwind.config.js
├── tsconfig.json
├── vite.config.ts
└── package.json
```

### Pattern 1: API Layer with TanStack Query
**What:** Centralized API client with query hooks for each endpoint
**When to use:** All server data fetching
**Example:**
```typescript
// src/features/auth/api/authApi.ts
import { apiClient } from '@/lib/api'

export const authApi = {
  login: async (email: string, password: string) => {
    const { data } = await apiClient.post('/api/v1/auth/login', { email, password })
    return data
  },

  getCurrentUser: async () => {
    const { data } = await apiClient.get('/api/v1/auth/me')
    return data
  },

  logout: async () => {
    await apiClient.post('/api/v1/auth/logout')
  },
}

// src/features/auth/hooks/useAuth.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { authApi } from '../api/authApi'

export const useCurrentUser = () => {
  return useQuery({
    queryKey: ['auth', 'me'],
    queryFn: authApi.getCurrentUser,
    retry: false,
  })
}

export const useLogin = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ email, password }: { email: string; password: string }) =>
      authApi.login(email, password),
    onSuccess: (data) => {
      // Update auth cache with user data
      queryClient.setQueryData(['auth', 'me'], data.user)
    },
  })
}

export const useLogout = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: authApi.logout,
    onSuccess: () => {
      // Clear all queries on logout
      queryClient.clear()
    },
  })
}
```

### Pattern 2: Protected Routes with React Router Loaders
**What:** Use React Router loaders to check auth before rendering protected routes
**When to use:** Any route requiring authentication
**Example:**
```typescript
// src/lib/loaders.ts
import { redirect } from 'react-router-dom'
import { queryClient } from './queryClient'

export const protectedLoader = async () => {
  try {
    // Ensure user data is loaded
    const user = await queryClient.ensureQueryData({
      queryKey: ['auth', 'me'],
      queryFn: async () => {
        const res = await fetch('/api/v1/auth/me', {
          credentials: 'include', // Include httpOnly cookie
        })
        if (!res.ok) throw new Error('Not authenticated')
        return res.json()
      },
    })
    return user
  } catch {
    // Redirect to login if not authenticated
    throw redirect('/login')
  }
}

// src/routes/root.tsx
import { createBrowserRouter } from 'react-router-dom'
import { protectedLoader } from '@/lib/loaders'

export const router = createBrowserRouter([
  {
    path: '/',
    element: <RootLayout />,
    children: [
      { path: 'login', element: <LoginPage /> },
      { path: 'signup', element: <SignupPage /> },
      { path: 'catalog', element: <CatalogPage /> }, // Public
      { path: 'catalog/:id', element: <CatalogDetailPage /> }, // Public
      {
        path: 'dashboard',
        element: <DashboardPage />,
        loader: protectedLoader, // Protected
      },
      {
        path: 'profile',
        element: <ProfilePage />,
        loader: protectedLoader, // Protected
      },
    ],
  },
])
```

### Pattern 3: Forms with React Hook Form + Zod
**What:** Uncontrolled forms with schema validation
**When to use:** All form inputs (login, signup, search, filters)
**Example:**
```typescript
// src/features/auth/components/LoginForm.tsx
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useLogin } from '../hooks/useAuth'

const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
})

type LoginFormData = z.infer<typeof loginSchema>

export function LoginForm() {
  const login = useLogin()

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  })

  const onSubmit = (data: LoginFormData) => {
    login.mutate(data)
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <div>
        <input {...register('email')} type="email" placeholder="Email" />
        {errors.email && <p className="text-red-500">{errors.email.message}</p>}
      </div>

      <div>
        <input {...register('password')} type="password" placeholder="Password" />
        {errors.password && <p className="text-red-500">{errors.password.message}</p>}
      </div>

      {login.isError && (
        <p className="text-red-500">Invalid credentials</p>
      )}

      <button type="submit" disabled={login.isPending}>
        {login.isPending ? 'Logging in...' : 'Log in'}
      </button>
    </form>
  )
}
```

### Pattern 4: Zustand for UI State Only
**What:** Lightweight store for client-only state (not server data)
**When to use:** Auth state, sidebar open/closed, modals, UI preferences
**Example:**
```typescript
// src/stores/authStore.ts
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface AuthState {
  isAuthenticated: boolean
  setAuthenticated: (value: boolean) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      isAuthenticated: false,
      setAuthenticated: (value) => set({ isAuthenticated: value }),
    }),
    {
      name: 'auth-storage', // localStorage key
    }
  )
)

// Usage in component
function Sidebar() {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)

  return (
    <nav>
      <a href="/catalog">Catalog</a>
      {isAuthenticated && <a href="/dashboard">Dashboard</a>}
    </nav>
  )
}
```

### Pattern 5: Dark Theme with CSS Variables (shadcn/ui)
**What:** Dark-only theme using Tailwind CSS variables
**When to use:** All UI styling
**Example:**
```css
/* src/index.css */
@import "tailwindcss";

@layer base {
  :root {
    --background: 0 0% 3.9%;
    --foreground: 0 0% 98%;
    --card: 0 0% 3.9%;
    --card-foreground: 0 0% 98%;
    --primary: 0 0% 98%;
    --primary-foreground: 0 0% 9%;
    --secondary: 0 0% 14.9%;
    --secondary-foreground: 0 0% 98%;
    --muted: 0 0% 14.9%;
    --muted-foreground: 0 0% 63.9%;
    --accent: 0 0% 14.9%;
    --accent-foreground: 0 0% 98%;
    --border: 0 0% 14.9%;
    --input: 0 0% 14.9%;
    --ring: 0 0% 83.1%;
  }
}
```

```typescript
// tailwind.config.js
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
        // ... other colors
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
}
```

### Pattern 6: Type-Safe Environment Variables
**What:** Typed environment variables using Vite's ImportMetaEnv
**When to use:** API URLs, feature flags, any runtime config
**Example:**
```typescript
// src/vite-env.d.ts
/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  readonly VITE_APP_NAME: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

// src/lib/api.ts
import axios from 'axios'

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL, // TypeScript knows this exists
  withCredentials: true, // Include httpOnly cookies
})
```

### Anti-Patterns to Avoid
- **Storing API data in Zustand/Redux:** Use TanStack Query for all server state; Zustand is only for UI state
- **Controlled forms everywhere:** Use React Hook Form's uncontrolled approach for better performance
- **Manual re-renders with setState after API calls:** Let TanStack Query handle cache invalidation automatically
- **Importing components from npm in shadcn/ui:** You copy the source into your project, don't install as dependency
- **Storing JWT in localStorage:** Use httpOnly cookies to prevent XSS attacks
- **Not using query keys consistently:** Inconsistent keys prevent proper cache invalidation
- **Overusing useEffect:** TanStack Query handles data fetching; don't mix with manual useEffect calls

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Form validation | Custom validation logic with useState | React Hook Form + Zod | Schema-based validation prevents bugs, type inference, performance optimization with uncontrolled components |
| API data caching | Manual cache with useEffect + useState | TanStack Query | Cache invalidation is hard; TQ handles deduplication, background refetch, stale-while-revalidate |
| Protected routes | Manual auth checks in components | React Router loaders | Loaders run before render, preventing auth UI flash; centralized logic |
| Dark mode toggle | Custom CSS class toggling | CSS variables with shadcn/ui theme | Semantic color tokens make theme consistent; variables work with SSR |
| HTTP client setup | Raw fetch with manual error handling | Axios with interceptors | Automatic request/response transformation, token refresh interceptors, centralized error handling |
| Accessible UI components | Custom buttons, dialogs, dropdowns | shadcn/ui components | ARIA compliance is complex; shadcn provides tested, accessible components you can modify |
| Token refresh logic | Manual token refresh with timers | Axios interceptors + TanStack Query | Handle race conditions, concurrent requests, automatic retry with fresh token |
| Form state management | useState for each field | React Hook Form | Uncontrolled = fewer re-renders; built-in validation, error handling, dirty/touched state |
| Data fetching loading states | Manual isLoading flags | TanStack Query status | Handles edge cases (error + refetch, background refetch while showing stale data) |
| Client-side routing | window.location or hash routing | React Router 6+ | Proper history management, nested routes, loaders for data fetching |

**Key insight:** Modern React development is declarative and library-driven. Don't build infrastructure; compose libraries that solve common problems with battle-tested solutions.

## Common Pitfalls

### Pitfall 1: Direct State Mutation in React
**What goes wrong:** Modifying state objects directly instead of creating new references
```typescript
// BAD
const [user, setUser] = useState({ name: 'John' })
user.name = 'Jane' // Direct mutation - won't trigger re-render
setUser(user)

// GOOD
setUser({ ...user, name: 'Jane' }) // New object reference
```
**Why it happens:** Coming from imperative programming backgrounds, forgetting React relies on referential equality
**How to avoid:** Always treat state as immutable; use spread operator or libraries like Immer
**Warning signs:** UI not updating after "setting" state, stale data in components

### Pitfall 2: Storing Server Data in Zustand/Context
**What goes wrong:** Fetching API data and storing it in Zustand or Context instead of TanStack Query
```typescript
// BAD - Manual cache management
const useUserStore = create((set) => ({
  user: null,
  fetchUser: async () => {
    const user = await api.getUser()
    set({ user })
  }
}))

// GOOD - Let TanStack Query handle it
const { data: user } = useQuery({
  queryKey: ['user'],
  queryFn: api.getUser,
})
```
**Why it happens:** Pre-TanStack Query habits, not understanding the difference between server state and UI state
**How to avoid:** Use TanStack Query for ALL server data; Zustand only for UI state (sidebar open, theme preference)
**Warning signs:** Manual loading states, stale data bugs, re-fetching logic in components

### Pitfall 3: JWT in localStorage (XSS Vulnerability)
**What goes wrong:** Storing access tokens in localStorage makes them accessible to JavaScript, vulnerable to XSS
```typescript
// BAD - XSS vulnerable
localStorage.setItem('token', accessToken)
axios.defaults.headers.common['Authorization'] = `Bearer ${localStorage.getItem('token')}`

// GOOD - httpOnly cookie (backend sets it)
axios.create({
  withCredentials: true, // Send cookies automatically
})
```
**Why it happens:** Tutorials often show localStorage for simplicity; devs don't understand XSS attack vectors
**How to avoid:** Use httpOnly cookies for refresh tokens (backend sets them), store access tokens in memory only or short-lived httpOnly cookies
**Warning signs:** Tokens in localStorage, no httpOnly flag on auth cookies, manual token attachment to requests

### Pitfall 4: Missing Query Keys = Broken Cache
**What goes wrong:** Not including relevant parameters in query keys prevents cache invalidation
```typescript
// BAD - Cache doesn't update when filter changes
const { data } = useQuery({
  queryKey: ['catalog'], // Missing 'type' parameter
  queryFn: () => api.getCatalog(type),
})

// GOOD - Cache key includes all variables
const { data } = useQuery({
  queryKey: ['catalog', { type, search }], // Cache separate for each type+search combo
  queryFn: () => api.getCatalog(type, search),
})
```
**Why it happens:** Not understanding that query keys are cache keys, treating them like identifiers only
**How to avoid:** Include ALL variables that affect the query result in the key; use objects for readability
**Warning signs:** Stale data when filters change, data from previous searches appearing

### Pitfall 5: Overusing useEffect for Data Fetching
**What goes wrong:** Mixing manual useEffect fetching with TanStack Query causes race conditions and duplicate requests
```typescript
// BAD - Manual fetching with useEffect
useEffect(() => {
  setLoading(true)
  api.getCatalog().then((data) => {
    setData(data)
    setLoading(false)
  })
}, [])

// GOOD - TanStack Query handles it
const { data, isLoading } = useQuery({
  queryKey: ['catalog'],
  queryFn: api.getCatalog,
})
```
**Why it happens:** useEffect is the "old way" of fetching data in React; tutorials from pre-2022 show this pattern
**How to avoid:** Use TanStack Query for ALL data fetching; reserve useEffect for side effects (logging, subscriptions)
**Warning signs:** Multiple useEffects fetching data, manual loading/error state management, race conditions

### Pitfall 6: Not Handling TanStack Query Error States
**What goes wrong:** Only checking isPending, not isError, causing blank screens on API failures
```typescript
// BAD - No error handling
const { data, isPending } = useQuery({ queryKey: ['user'], queryFn: api.getUser })
if (isPending) return <Spinner />
return <div>{data.name}</div> // Crashes if error occurred

// GOOD - Handle all states
const { data, isPending, isError, error } = useQuery({
  queryKey: ['user'],
  queryFn: api.getUser
})
if (isPending) return <Spinner />
if (isError) return <ErrorMessage error={error} />
return <div>{data.name}</div>
```
**Why it happens:** Optimism that APIs always succeed, not testing error scenarios
**How to avoid:** Always handle isPending, isError, and success states in that order; TypeScript narrows types automatically
**Warning signs:** White screen of death on API errors, uncaught promise rejections

### Pitfall 7: React Router Loader Waterfalls
**What goes wrong:** Not preloading data in loaders causes sequential requests (waterfall)
```typescript
// BAD - Component waits for loader, then fetches more data = waterfall
export const Route = {
  loader: async () => {
    const user = await api.getUser()
    return { user }
  },
  element: <Dashboard />, // Component then fetches dashboard data
}

// GOOD - Preload all data in parallel in loader
export const Route = {
  loader: async ({ context }) => {
    await Promise.allSettled([
      context.queryClient.ensureQueryData({ queryKey: ['user'], queryFn: api.getUser }),
      context.queryClient.ensureQueryData({ queryKey: ['dashboard'], queryFn: api.getDashboard }),
    ])
  },
  element: <Dashboard />, // Component reads from cache immediately
}
```
**Why it happens:** Not understanding that loaders can prefetch data that components will use
**How to avoid:** Use queryClient.ensureQueryData in loaders to prefetch all route data; use Promise.allSettled for parallel requests
**Warning signs:** Slow page loads, network tab shows sequential requests, loading spinners after route loads

### Pitfall 8: Controlled Form Inputs Causing Performance Issues
**What goes wrong:** Using useState for every form field causes re-render on every keystroke
```typescript
// BAD - Re-renders entire form on every keystroke
const [email, setEmail] = useState('')
const [password, setPassword] = useState('')
return (
  <form>
    <input value={email} onChange={(e) => setEmail(e.target.value)} />
    <input value={password} onChange={(e) => setPassword(e.target.value)} />
  </form>
)

// GOOD - React Hook Form uses uncontrolled inputs
const { register, handleSubmit } = useForm()
return (
  <form onSubmit={handleSubmit(onSubmit)}>
    <input {...register('email')} />
    <input {...register('password')} />
  </form>
)
```
**Why it happens:** Controlled components are the "default" pattern shown in React docs for simple examples
**How to avoid:** Use React Hook Form for all forms with more than 2-3 fields
**Warning signs:** Laggy typing in forms, React DevTools showing many re-renders per keystroke

### Pitfall 9: Missing Tailwind Dark Mode Class Configuration
**What goes wrong:** Dark mode styles not applying because Tailwind config doesn't have selector strategy
```typescript
// BAD - tailwind.config.js missing darkMode
export default {
  content: ['./src/**/*.{ts,tsx}'],
  theme: {},
}

// GOOD - Configure dark mode strategy
export default {
  darkMode: 'selector', // or 'media' for prefers-color-scheme
  content: ['./src/**/*.{ts,tsx}'],
  theme: {},
}
```
**Why it happens:** Default Tailwind config doesn't include darkMode; shadcn/ui requires it
**How to avoid:** Run `npx shadcn@latest init` which sets up config correctly; verify darkMode is set
**Warning signs:** dark: classes in components don't work, theme stays light

### Pitfall 10: Not Invalidating Queries After Mutations
**What goes wrong:** Creating/updating data via mutation doesn't refresh the list/detail views
```typescript
// BAD - Create item but list doesn't update
const createItem = useMutation({
  mutationFn: api.createItem,
  // No onSuccess
})

// GOOD - Invalidate relevant queries
const createItem = useMutation({
  mutationFn: api.createItem,
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['catalog'] }) // Refetch catalog list
  },
})
```
**Why it happens:** Not understanding TanStack Query's cache system, expecting automatic updates
**How to avoid:** Always invalidate affected queries in mutation onSuccess; use optimistic updates for instant feedback
**Warning signs:** Creating item doesn't show in list until page refresh, stale data after mutations

## Code Examples

Verified patterns from official sources:

### Axios Client Setup with Token Refresh
```typescript
// src/lib/api.ts
// Source: https://medium.com/@aqeel_ahmad/handling-jwt-access-token-refresh-token-using-axios-in-react-react-native-app-2024-f452c96a83fc
import axios from 'axios'

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  withCredentials: true, // Include httpOnly cookies
})

// Response interceptor for token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    // If 401 and haven't retried yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        // Refresh token endpoint (uses httpOnly cookie)
        await axios.post('/api/v1/auth/refresh', {}, { withCredentials: true })

        // Retry original request
        return apiClient(originalRequest)
      } catch (refreshError) {
        // Refresh failed, redirect to login
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)
```

### TanStack Query Setup
```typescript
// src/lib/queryClient.ts
// Source: https://tanstack.com/query/latest/docs/framework/react/overview
import { QueryClient } from '@tanstack/react-query'

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      gcTime: 1000 * 60 * 10, // 10 minutes (formerly cacheTime)
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})

// src/main.tsx
import { QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'

root.render(
  <QueryClientProvider client={queryClient}>
    <App />
    <ReactQueryDevtools initialIsOpen={false} />
  </QueryClientProvider>
)
```

### Feature-Based Catalog API Pattern
```typescript
// src/features/catalog/api/catalogApi.ts
import { apiClient } from '@/lib/api'
import type { CatalogItem, CatalogListResponse } from '../types'

export const catalogApi = {
  getItems: async (params: {
    type?: 'skill' | 'mcp' | 'tool'
    search?: string
    page?: number
  }): Promise<CatalogListResponse> => {
    const { data } = await apiClient.get('/api/v1/catalog', { params })
    return data
  },

  getItemById: async (id: string): Promise<CatalogItem> => {
    const { data } = await apiClient.get(`/api/v1/catalog/${id}`)
    return data
  },
}

// src/features/catalog/hooks/useCatalog.ts
import { useQuery } from '@tanstack/react-query'
import { catalogApi } from '../api/catalogApi'

export const useCatalogItems = (filters: {
  type?: 'skill' | 'mcp' | 'tool'
  search?: string
}) => {
  return useQuery({
    queryKey: ['catalog', filters],
    queryFn: () => catalogApi.getItems(filters),
  })
}

export const useCatalogItem = (id: string) => {
  return useQuery({
    queryKey: ['catalog', id],
    queryFn: () => catalogApi.getItemById(id),
    enabled: !!id, // Only fetch if id exists
  })
}
```

### shadcn/ui Component Usage
```typescript
// After running: npx shadcn@latest add button card
// Components are now in src/components/ui/

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export function CatalogCard({ item }: { item: CatalogItem }) {
  return (
    <Card className="hover:border-primary transition-colors">
      <CardHeader>
        <div className="flex items-center gap-2">
          <CardTitle>{item.name}</CardTitle>
          <span className="text-xs bg-secondary px-2 py-1 rounded">
            {item.type}
          </span>
        </div>
        <CardDescription className="line-clamp-2">
          {item.description}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex gap-2">
          {item.tags?.map((tag) => (
            <span key={tag} className="text-xs text-muted-foreground">
              #{tag}
            </span>
          ))}
        </div>
        <Button variant="outline" className="mt-4 w-full">
          View Details
        </Button>
      </CardContent>
    </Card>
  )
}
```

### React Router with Loaders
```typescript
// src/routes/catalog.tsx
// Source: https://reactrouter.com/en/main/start/overview
import { createBrowserRouter, RouterProvider, LoaderFunctionArgs } from 'react-router-dom'
import { queryClient } from '@/lib/queryClient'
import { catalogApi } from '@/features/catalog/api/catalogApi'

// Route loader
export const catalogDetailLoader = async ({ params }: LoaderFunctionArgs) => {
  const { id } = params

  if (!id) throw new Error('Missing catalog item ID')

  // Prefetch data before rendering
  await queryClient.ensureQueryData({
    queryKey: ['catalog', id],
    queryFn: () => catalogApi.getItemById(id),
  })

  return null
}

// Router configuration
export const router = createBrowserRouter([
  {
    path: '/',
    element: <RootLayout />,
    children: [
      {
        path: 'catalog/:id',
        element: <CatalogDetailPage />,
        loader: catalogDetailLoader,
      },
    ],
  },
])

// Component reads from cache (already loaded by loader)
function CatalogDetailPage() {
  const { id } = useParams()
  const { data, isLoading } = useCatalogItem(id!) // Data already in cache

  if (isLoading) return <Skeleton />

  return <div>{data.name}</div>
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Create React App | Vite | 2023 | 10-100x faster dev server, no more webpack config |
| React Query v4 | TanStack Query v5 | Nov 2023 | Renamed cacheTime → gcTime, better TypeScript, new APIs |
| Redux for all state | TanStack Query for server state, Zustand for UI | 2021-2022 | Less boilerplate, automatic cache management |
| Formik for forms | React Hook Form | 2020 | Better performance (uncontrolled), smaller bundle |
| Styled Components / Emotion | Tailwind CSS | 2021-2023 | Faster development, smaller runtime cost |
| Component libraries as npm packages | shadcn/ui (copy source) | 2023 | Full control, customize without fighting framework |
| Manual dark mode toggle | CSS variables + system preference | 2024 | Semantic tokens, better SSR support |
| React Router v5 | React Router v6 | 2021 | Nested routes, loaders for data fetching |
| localStorage for tokens | httpOnly cookies | 2022-2023 | XSS protection, automatic CSRF protection |
| Manual API client | Axios with interceptors | Long-standing | Centralized error handling, automatic token refresh |
| Tailwind CSS v3 (HSL) | Tailwind CSS v4 (OKLCH) | 2024 | Better color accessibility, wider gamut |

**Deprecated/outdated:**
- Create React App: Officially unmaintained; use Vite or Next.js
- Formik: Still works but React Hook Form is more performant
- next-themes with Vite: Designed for Next.js; for Vite use custom implementation or just CSS media queries
- React Router v5: Use v6+ for loaders and better TypeScript
- TanStack Query cacheTime: Renamed to gcTime in v5
- localStorage for JWTs: Use httpOnly cookies to prevent XSS

## Open Questions

Things that couldn't be fully resolved:

1. **Component Library Choice**
   - What we know: shadcn/ui is recommended in user context, widely adopted in 2026, provides accessible components
   - What's unclear: Specific developer-focused themes (GitHub-like) availability in shadcn/ui theme gallery
   - Recommendation: Start with shadcn/ui default dark theme, customize CSS variables to match GitHub aesthetic; use theme generators like tweakcn.com for inspiration

2. **Icon Library**
   - What we know: shadcn/ui uses Radix Icons by default, but doesn't enforce it
   - What's unclear: Best icon library for developer tools aesthetic (Lucide, Heroicons, Radix)
   - Recommendation: Use Lucide Icons (clean, consistent, good developer tool icons like Terminal, Code, Package)

3. **Testing Strategy**
   - What we know: Vitest is the standard for Vite projects, React Testing Library for components, Playwright for E2E
   - What's unclear: Testing plan wasn't specified in phase requirements
   - Recommendation: Defer comprehensive testing to a later phase; include basic smoke tests for critical paths (login, catalog view)

4. **Concurrent Request Handling for Token Refresh**
   - What we know: Multiple requests can trigger token refresh simultaneously, causing race conditions
   - What's unclear: Best pattern for preventing concurrent refresh requests
   - Recommendation: Implement request queuing pattern where first 401 triggers refresh, subsequent requests wait for result (see axios-auth-refresh library pattern)

## Sources

### Primary (HIGH confidence)
- [Vite Official Guide](https://vite.dev/guide/) - Build tool configuration and best practices
- [TanStack Query v5 React Docs](https://tanstack.com/query/latest/docs/framework/react/overview) - Query setup and patterns
- [React Router v6.28 Docs](https://reactrouter.com/en/main/start/overview) - Routing and loaders
- [shadcn/ui Installation - Vite](https://ui.shadcn.com/docs/installation/vite) - Component library setup
- [React Hook Form Get Started](https://react-hook-form.com/get-started) - Form handling patterns
- [Zustand GitHub](https://github.com/pmndrs/zustand) - State management API

### Secondary (MEDIUM confidence)
- [Complete Guide to Setting Up React with TypeScript and Vite (2026)](https://medium.com/@robinviktorsson/complete-guide-to-setting-up-react-with-typescript-and-vite-2025-468f6556aaf2)
- [React State Management in 2025: What You Actually Need](https://www.developerway.com/posts/react-state-management-2025)
- [React Router 7: Private Routes](https://www.robinwieruch.de/react-router-private-routes/)
- [Handling JWT Access and Refresh Token using Axios in React App](https://blog.theashishmaurya.me/handling-jwt-access-and-refresh-token-using-axios-in-react-app)
- [React Folder Structure in 5 Steps [2025]](https://www.robinwieruch.de/react-folder-structure/)
- [TanStack Query Integration with React Router](https://tanstack.com/query/latest/docs/framework/react/examples/react-router)
- [React Form Validation Best Practices](https://www.dhiwise.com/post/react-form-validation-best-practices-with-tips-and-tricks)

### Tertiary (LOW confidence - flagged for validation)
- [React Security: Vulnerabilities & Best Practices [2026]](https://www.glorywebs.com/blog/react-security-practices) - Security patterns (verify httpOnly cookie implementation with backend)
- [Avoiding Common Mistakes with TanStack Query](https://www.buncolak.com/posts/avoiding-common-mistakes-with-tanstack-query-part-1/) - Community pitfalls (validate against official docs)
- [shadcn/ui Dark Mode GitHub Issues](https://github.com/shadcn-ui/ui/issues/1147) - Community troubleshooting (verify fixes apply to Vite setup)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All libraries verified through official documentation and 2026 search results
- Architecture: HIGH - Patterns verified with official TanStack Query, React Router, and React Hook Form docs
- Pitfalls: MEDIUM - Mix of official documentation (HIGH) and community articles (MEDIUM); common issues cross-verified across multiple sources

**Research date:** 2026-01-24
**Valid until:** 2026-03-24 (60 days - stable ecosystem, but fast-moving in frontend space)

**Notes:**
- All version numbers are current as of January 2026
- Backend API already implemented with httpOnly cookie pattern for refresh tokens
- User context specifies dark-only theme, simplifying implementation (no theme toggle needed)
- Phase focuses on core functionality; advanced features (optimistic updates, offline support) can be added later
