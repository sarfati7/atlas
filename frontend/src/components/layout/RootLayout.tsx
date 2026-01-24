/**
 * RootLayout - Main app layout with sidebar and content area.
 */

import { Outlet } from 'react-router-dom'
import { Sidebar } from './Sidebar'

export function RootLayout() {
  return (
    <div className="flex h-screen bg-background text-foreground">
      <Sidebar />
      <main className="flex-1 overflow-auto">
        <Outlet />
      </main>
    </div>
  )
}
