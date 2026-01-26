/**
 * Sidebar - Navigation sidebar with Atlas branding.
 */

import { Link, useLocation } from 'react-router-dom'
import { Activity, Book, FileText, LayoutDashboard, LogIn, LogOut, Settings, Settings2, Shield, Users, UsersRound } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { useAuthStore } from '@/stores/authStore'
import { useLogout, useCurrentUser } from '@/features/auth/hooks/useAuth'

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
  const { data: currentUser } = useCurrentUser()
  const logout = useLogout()
  const isAdmin = currentUser?.role === 'admin'

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

        {/* Admin section - only visible to admins */}
        {isAdmin && (
          <>
            <div className="mt-4 mb-2 px-3 py-1">
              <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider flex items-center gap-2">
                <Shield className="h-3 w-3" />
                Admin
              </span>
            </div>
            <NavItem
              to="/admin/teams"
              icon={<UsersRound className="h-4 w-4" />}
              label="Teams"
              isActive={location.pathname.startsWith('/admin/teams')}
            />
            <NavItem
              to="/admin/users"
              icon={<Users className="h-4 w-4" />}
              label="Users"
              isActive={location.pathname.startsWith('/admin/users')}
            />
            <NavItem
              to="/admin/analytics"
              icon={<Activity className="h-4 w-4" />}
              label="Analytics"
              isActive={location.pathname.startsWith('/admin/analytics')}
            />
            <NavItem
              to="/admin/audit"
              icon={<FileText className="h-4 w-4" />}
              label="Audit Logs"
              isActive={location.pathname.startsWith('/admin/audit')}
            />
            <NavItem
              to="/admin/settings"
              icon={<Settings2 className="h-4 w-4" />}
              label="Settings"
              isActive={location.pathname.startsWith('/admin/settings')}
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
