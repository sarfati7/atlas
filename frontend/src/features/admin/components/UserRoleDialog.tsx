/**
 * UserRoleDialog - Dialog for changing a user's role.
 */

import { useState, useEffect } from 'react'
import { Shield, User, AlertTriangle } from 'lucide-react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useUpdateUserRole } from '../hooks'
import type { AdminUser, UserRole } from '../types'

interface UserRoleDialogProps {
  open: boolean
  onClose: () => void
  user: AdminUser | null
}

export function UserRoleDialog({ open, onClose, user }: UserRoleDialogProps) {
  const [selectedRole, setSelectedRole] = useState<UserRole>('user')
  const updateRole = useUpdateUserRole()

  // Reset selection when dialog opens
  useEffect(() => {
    if (open && user) {
      setSelectedRole(user.role)
    }
  }, [open, user])

  const handleSubmit = async () => {
    if (!user || selectedRole === user.role) return
    await updateRole.mutateAsync({ id: user.id, data: { role: selectedRole } })
    onClose()
  }

  const isChanging = selectedRole !== user?.role
  const isPromoting = user?.role === 'user' && selectedRole === 'admin'
  const isDemoting = user?.role === 'admin' && selectedRole === 'user'

  return (
    <Dialog open={open} onOpenChange={(open) => !open && onClose()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Change User Role</DialogTitle>
          <DialogDescription>
            Update role for <strong>{user?.email}</strong>
          </DialogDescription>
        </DialogHeader>

        <div className="py-4 space-y-4">
          {/* User info */}
          <div className="p-3 rounded-md bg-muted/50">
            <p className="text-sm font-medium">{user?.username}</p>
            <p className="text-xs text-muted-foreground">{user?.email}</p>
          </div>

          {/* Role selector */}
          <div className="space-y-2">
            <Label htmlFor="role">Role</Label>
            <Select value={selectedRole} onValueChange={(value) => setSelectedRole(value as UserRole)}>
              <SelectTrigger id="role">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="user">
                  <div className="flex items-center gap-2">
                    <User className="h-4 w-4" />
                    User
                  </div>
                </SelectItem>
                <SelectItem value="admin">
                  <div className="flex items-center gap-2">
                    <Shield className="h-4 w-4" />
                    Admin
                  </div>
                </SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Warning messages */}
          {isPromoting && (
            <div className="flex gap-2 p-3 rounded-md bg-amber-500/10 border border-amber-500/20">
              <AlertTriangle className="h-4 w-4 text-amber-500 shrink-0 mt-0.5" />
              <div className="text-sm text-amber-500">
                <strong>Promoting to Admin:</strong> This user will be able to manage teams, users,
                and access all admin features.
              </div>
            </div>
          )}

          {isDemoting && (
            <div className="flex gap-2 p-3 rounded-md bg-amber-500/10 border border-amber-500/20">
              <AlertTriangle className="h-4 w-4 text-amber-500 shrink-0 mt-0.5" />
              <div className="text-sm text-amber-500">
                <strong>Demoting to User:</strong> This user will lose access to admin features
                including team and user management.
              </div>
            </div>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose} disabled={updateRole.isPending}>
            Cancel
          </Button>
          <Button onClick={handleSubmit} disabled={!isChanging || updateRole.isPending}>
            {updateRole.isPending ? 'Updating...' : 'Update Role'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
