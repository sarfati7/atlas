/**
 * AdminUsers - User management page for admin users.
 */

import { useState } from 'react'
import { Search } from 'lucide-react'
import { Input } from '@/components/ui/input'
import { UserList } from '@/features/admin/components/UserList'
import { UserRoleDialog } from '@/features/admin/components/UserRoleDialog'
import { DeleteUserDialog } from '@/features/admin/components/DeleteUserDialog'
import { useUsers } from '@/features/admin/hooks'
import type { AdminUser } from '@/features/admin/types'

export function AdminUsersPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const pageSize = 10
  const { data, isLoading } = useUsers(page, pageSize, search || undefined)

  // Role dialog state
  const [roleDialogOpen, setRoleDialogOpen] = useState(false)
  const [roleUser, setRoleUser] = useState<AdminUser | null>(null)

  // Delete dialog state
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [deleteUser, setDeleteUser] = useState<AdminUser | null>(null)

  const handleChangeRole = (user: AdminUser) => {
    setRoleUser(user)
    setRoleDialogOpen(true)
  }

  const handleDelete = (user: AdminUser) => {
    setDeleteUser(user)
    setDeleteDialogOpen(true)
  }

  const handleRoleDialogClose = () => {
    setRoleDialogOpen(false)
    setRoleUser(null)
  }

  const handleDeleteDialogClose = () => {
    setDeleteDialogOpen(false)
    setDeleteUser(null)
  }

  // Reset page when search changes
  const handleSearchChange = (value: string) => {
    setSearch(value)
    setPage(1)
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto max-w-5xl px-4 py-8">
        {/* Header */}
        <header className="mb-8">
          <div className="mb-4">
            <h1 className="text-2xl font-semibold text-foreground">User Management</h1>
            <p className="text-muted-foreground">View and manage users in your organization</p>
          </div>

          {/* Search */}
          <div className="relative max-w-sm">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search by email or username..."
              value={search}
              onChange={(e) => handleSearchChange(e.target.value)}
              className="pl-9"
            />
          </div>
        </header>

        {/* User List */}
        <UserList
          users={data?.items || []}
          isLoading={isLoading}
          onChangeRole={handleChangeRole}
          onDelete={handleDelete}
          page={page}
          pageSize={pageSize}
          total={data?.total || 0}
          onPageChange={setPage}
        />

        {/* Role Dialog */}
        <UserRoleDialog open={roleDialogOpen} onClose={handleRoleDialogClose} user={roleUser} />

        {/* Delete Dialog */}
        <DeleteUserDialog
          open={deleteDialogOpen}
          onClose={handleDeleteDialogClose}
          user={deleteUser}
        />
      </div>
    </div>
  )
}
