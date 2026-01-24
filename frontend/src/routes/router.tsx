import { createBrowserRouter, Navigate } from 'react-router-dom'
import { LoginPage } from './login'
import { SignupPage } from './signup'
import { ResetPasswordPage } from './reset-password'
import { CatalogPage } from './catalog'
import { CatalogDetailPage } from './catalog-detail'
import { DashboardPage } from './dashboard'
import { RootLayout } from '@/components/layout'
import { guestLoader, protectedLoader } from '@/lib/loaders'

/**
 * Centralized router configuration using createBrowserRouter.
 *
 * CRITICAL: This file is the single source of truth for all routes.
 * All subsequent plans (06-04) will MODIFY this file
 * by importing route components and adding them to the routes array below.
 *
 * DO NOT replace this file or create a new routing structure in App.tsx.
 * ALWAYS extend this router configuration by adding new route objects.
 *
 * Route structure:
 * - Auth routes (no layout): /login, /signup, /reset-password
 * - App routes (with RootLayout): /catalog, /catalog/:id, /dashboard, /settings
 */
export const router = createBrowserRouter([
  // Default redirect to catalog
  {
    path: '/',
    element: <Navigate to="/catalog" replace />,
  },

  // Auth routes (no layout wrapper, guest-only)
  {
    path: '/login',
    element: <LoginPage />,
    loader: guestLoader,
  },
  {
    path: '/signup',
    element: <SignupPage />,
    loader: guestLoader,
  },
  {
    path: '/reset-password',
    element: <ResetPasswordPage />,
  },

  // App routes with RootLayout (sidebar navigation)
  {
    element: <RootLayout />,
    children: [
      {
        path: '/catalog',
        element: <CatalogPage />,
      },
      {
        path: '/catalog/:id',
        element: <CatalogDetailPage />,
      },
      {
        path: '/dashboard',
        element: <DashboardPage />,
        loader: protectedLoader,
      },
      {
        path: '/settings',
        element: <div className="p-6">Settings (coming later)</div>,
        loader: protectedLoader,
      },
    ],
  },
])
