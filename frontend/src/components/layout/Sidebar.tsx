/**
 * Sidebar - Navigation sidebar with Atlas branding.
 */

import { Link, useLocation } from 'react-router-dom'
import { Book, LayoutDashboard, LogIn, LogOut, Settings } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { useAuthStore } from '@/stores/authStore'
import { useLogout } from '@/features/auth/hooks/useAuth'

interface NavItemProps {
  to: string
  icon: React.ReactNode
  label: string
  isActive: boolean
}

function NavItem({ to, icon, label, isActive }: NavItemProps) {
  return (
    <Link
      to={to}
      className={cn(
        'flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors',
        isActive
          ? 'bg-accent text-accent-foreground'
          : 'text-muted-foreground hover:text-foreground hover:bg-accent/50'
      )}
    >
      {icon}
      {label}
    </Link>
  )
}

export function Sidebar() {
  const location = useLocation()
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  const logout = useLogout()

  const handleLogout = () => {
    logout.mutate()
  }

  return (
    <aside className="flex flex-col h-full w-60 border-r bg-card">
      {/* Branding */}
      <div className="flex items-center gap-2 px-4 py-5 border-b">
        <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary text-primary-foreground font-bold">
          A
        </div>
        <span className="text-lg font-semibold">Atlas</span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-3 space-y-1">
        <NavItem
          to="/catalog"
          icon={<Book className="h-4 w-4" />}
          label="Catalog"
          isActive={location.pathname.startsWith('/catalog')}
        />

        {isAuthenticated && (
          <>
            <NavItem
              to="/dashboard"
              icon={<LayoutDashboard className="h-4 w-4" />}
              label="Dashboard"
              isActive={location.pathname === '/dashboard'}
            />
            <NavItem
              to="/settings"
              icon={<Settings className="h-4 w-4" />}
              label="Settings"
              isActive={location.pathname === '/settings'}
            />
          </>
        )}
      </nav>

      {/* Footer */}
      <div className="p-3 border-t">
        {isAuthenticated ? (
          <Button
            variant="ghost"
            className="w-full justify-start gap-3 text-muted-foreground hover:text-foreground"
            onClick={handleLogout}
            disabled={logout.isPending}
          >
            <LogOut className="h-4 w-4" />
            {logout.isPending ? 'Signing out...' : 'Sign out'}
          </Button>
        ) : (
          <Button
            variant="ghost"
            className="w-full justify-start gap-3 text-muted-foreground hover:text-foreground"
            asChild
          >
            <Link to="/login">
              <LogIn className="h-4 w-4" />
              Sign in
            </Link>
          </Button>
        )}
      </div>
    </aside>
  )
}
