import { createBrowserRouter, Navigate } from 'react-router-dom'
import { LoginPage } from './login'
import { SignupPage } from './signup'
import { ResetPasswordPage } from './reset-password'
import { CatalogPage } from './catalog'
import { CatalogDetailPage } from './catalog-detail'
import { DashboardPage } from './dashboard'
import { SettingsPage } from './settings'
import { AdminTeamsPage } from './admin-teams'
import { AdminUsersPage } from './admin-users'
import { AdminAnalyticsPage } from './admin-analytics'
import { AdminAuditLogsPage } from './admin-audit'
import { AdminSettingsPage } from './admin-settings'
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
        element: <SettingsPage />,
        loader: protectedLoader,
      },

      // Admin routes (protected + admin-only via backend)
      {
        path: '/admin/teams',
        element: <AdminTeamsPage />,
        loader: protectedLoader,
      },
      {
        path: '/admin/users',
        element: <AdminUsersPage />,
        loader: protectedLoader,
      },
      {
        path: '/admin/analytics',
        element: <AdminAnalyticsPage />,
        loader: protectedLoader,
      },
      {
        path: '/admin/audit',
        element: <AdminAuditLogsPage />,
        loader: protectedLoader,
      },
      {
        path: '/admin/settings',
        element: <AdminSettingsPage />,
        loader: protectedLoader,
      },
    ],
  },
])
