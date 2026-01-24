import { createBrowserRouter, Navigate } from 'react-router-dom'
import { LoginPage } from './login'
import { SignupPage } from './signup'
import { ResetPasswordPage } from './reset-password'

/**
 * Centralized router configuration using createBrowserRouter.
 *
 * CRITICAL: This file is the single source of truth for all routes.
 * All subsequent plans (06-03, 06-04, 06-05) will MODIFY this file
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

  // Auth routes (no layout wrapper)
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/signup',
    element: <SignupPage />,
  },
  {
    path: '/reset-password',
    element: <ResetPasswordPage />,
  },

  // Placeholder routes until 06-03, 06-04, 06-05 complete them
  {
    path: '/catalog',
    element: <div className="min-h-screen flex items-center justify-center bg-background text-foreground">Catalog (coming in 06-03)</div>,
  },
  {
    path: '/dashboard',
    element: <div className="min-h-screen flex items-center justify-center bg-background text-foreground">Dashboard (coming in 06-05)</div>,
  },
])
