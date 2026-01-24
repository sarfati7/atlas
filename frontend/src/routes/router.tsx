import { createBrowserRouter, Navigate } from 'react-router-dom'

/**
 * Centralized router configuration using createBrowserRouter.
 *
 * CRITICAL: This file is the single source of truth for all routes.
 * All subsequent plans (06-02, 06-03, 06-04, 06-05) will MODIFY this file
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
  // Placeholder - auth routes will be added by 06-02
  // Placeholder - app routes with RootLayout will be added by 06-03

  // Default redirect to catalog
  {
    path: '/',
    element: <Navigate to="/catalog" replace />,
  },

  // Temporary placeholder routes until plans complete them
  {
    path: '/login',
    element: <div className="min-h-screen flex items-center justify-center bg-background text-foreground">Login (coming in 06-02)</div>,
  },
  {
    path: '/catalog',
    element: <div className="min-h-screen flex items-center justify-center bg-background text-foreground">Catalog (coming in 06-03)</div>,
  },
])
