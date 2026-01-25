/**
 * UserList - Table displaying users with actions.
 */

import { formatDistanceToNow } from 'date-fns'
import { Trash2, Shield, User } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Skeleton } from '@/components/ui/skeleton'
import type { AdminUser } from '../types'

interface UserListProps {
  users: AdminUser[]
  isLoading: boolean
  onChangeRole: (user: AdminUser) => void
  onDelete: (user: AdminUser) => void
  page: number
  pageSize: number
  total: number
  onPageChange: (page: number) => void
}

export function UserList({
  users,
  isLoading,
  onChangeRole,
  onDelete,
  page,
  pageSize,
  total,
  onPageChange,
}: UserListProps) {
  const totalPages = Math.ceil(total / pageSize)

  if (isLoading) {
    return <UserListSkeleton />
  }

  if (users.length === 0) {
    return <UserListEmpty />
  }

  return (
    <>
      <div className="rounded-lg border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Email</TableHead>
              <TableHead>Username</TableHead>
              <TableHead className="w-[100px]">Role</TableHead>
              <TableHead className="w-[80px]">Teams</TableHead>
              <TableHead className="w-[150px]">Created</TableHead>
              <TableHead className="w-[100px] text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {users.map((user) => (
              <TableRow key={user.id}>
                <TableCell className="font-medium">{user.email}</TableCell>
                <TableCell className="text-muted-foreground">{user.username}</TableCell>
                <TableCell>
                  <RoleBadge role={user.role} />
                </TableCell>
                <TableCell className="text-muted-foreground">{user.team_ids.length}</TableCell>
                <TableCell className="text-muted-foreground text-sm">
                  {formatDistanceToNow(new Date(user.created_at), { addSuffix: true })}
                </TableCell>
                <TableCell className="text-right">
                  <div className="flex justify-end gap-1">
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => onChangeRole(user)}
                      title="Change role"
                    >
                      <Shield className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => onDelete(user)}
                      title="Delete user"
                      className="text-destructive hover:text-destructive"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between mt-4">
          <p className="text-sm text-muted-foreground">
            Showing {(page - 1) * pageSize + 1} to {Math.min(page * pageSize, total)} of {total}{' '}
            users
          </p>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => onPageChange(page - 1)}
              disabled={page === 1}
            >
              Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => onPageChange(page + 1)}
              disabled={page >= totalPages}
            >
              Next
            </Button>
          </div>
        </div>
      )}
    </>
  )
}

function RoleBadge({ role }: { role: 'admin' | 'user' }) {
  if (role === 'admin') {
    return (
      <Badge variant="destructive" className="gap-1">
        <Shield className="h-3 w-3" />
        Admin
      </Badge>
    )
  }
  return (
    <Badge variant="secondary" className="gap-1">
      <User className="h-3 w-3" />
      User
    </Badge>
  )
}

function UserListSkeleton() {
  return (
    <div className="rounded-lg border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Email</TableHead>
            <TableHead>Username</TableHead>
            <TableHead className="w-[100px]">Role</TableHead>
            <TableHead className="w-[80px]">Teams</TableHead>
            <TableHead className="w-[150px]">Created</TableHead>
            <TableHead className="w-[100px] text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {[...Array(5)].map((_, i) => (
            <TableRow key={i}>
              <TableCell>
                <Skeleton className="h-5 w-40" />
              </TableCell>
              <TableCell>
                <Skeleton className="h-5 w-24" />
              </TableCell>
              <TableCell>
                <Skeleton className="h-5 w-16" />
              </TableCell>
              <TableCell>
                <Skeleton className="h-5 w-8" />
              </TableCell>
              <TableCell>
                <Skeleton className="h-5 w-24" />
              </TableCell>
              <TableCell>
                <div className="flex justify-end gap-1">
                  <Skeleton className="h-8 w-8" />
                  <Skeleton className="h-8 w-8" />
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}

function UserListEmpty() {
  return (
    <div className="rounded-lg border border-dashed p-12 text-center">
      <User className="h-12 w-12 mx-auto text-muted-foreground/50" />
      <h3 className="mt-4 text-lg font-medium">No users found</h3>
      <p className="mt-2 text-sm text-muted-foreground">
        No users match your search criteria.
      </p>
    </div>
  )
}
