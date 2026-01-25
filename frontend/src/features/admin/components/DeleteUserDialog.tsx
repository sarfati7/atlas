/**
 * DeleteUserDialog - Confirmation dialog requiring email typing to delete.
 */

import { useState, useEffect } from 'react'
import { AlertTriangle } from 'lucide-react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useDeleteUser } from '../hooks'
import type { AdminUser } from '../types'

interface DeleteUserDialogProps {
  open: boolean
  onClose: () => void
  user: AdminUser | null
}

export function DeleteUserDialog({ open, onClose, user }: DeleteUserDialogProps) {
  const [confirmEmail, setConfirmEmail] = useState('')
  const deleteUser = useDeleteUser()

  // Reset confirmation when dialog opens
  useEffect(() => {
    if (open) {
      setConfirmEmail('')
    }
  }, [open])

  const handleDelete = async () => {
    if (!user || confirmEmail !== user.email) return
    await deleteUser.mutateAsync(user.id)
    onClose()
  }

  const canDelete = confirmEmail === user?.email

  return (
    <Dialog open={open} onOpenChange={(open) => !open && onClose()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle className="text-destructive">Delete User</DialogTitle>
          <DialogDescription>
            This action cannot be undone. This will permanently delete the user account.
          </DialogDescription>
        </DialogHeader>

        <div className="py-4 space-y-4">
          {/* Warning banner */}
          <div className="flex gap-2 p-3 rounded-md bg-destructive/10 border border-destructive/20">
            <AlertTriangle className="h-4 w-4 text-destructive shrink-0 mt-0.5" />
            <div className="text-sm text-destructive">
              <strong>Warning:</strong> Deleting this user will:
              <ul className="list-disc list-inside mt-1 space-y-0.5">
                <li>Remove them from all teams</li>
                <li>Delete their configuration</li>
                <li>Remove all associated data</li>
              </ul>
            </div>
          </div>

          {/* User info */}
          <div className="p-3 rounded-md bg-muted/50">
            <p className="text-sm font-medium">{user?.username}</p>
            <p className="text-xs text-muted-foreground">{user?.email}</p>
          </div>

          {/* Email confirmation */}
          <div className="space-y-2">
            <Label htmlFor="confirm-email">
              Type <code className="bg-muted px-1 py-0.5 rounded text-sm">{user?.email}</code> to
              confirm
            </Label>
            <Input
              id="confirm-email"
              placeholder="Enter email to confirm"
              value={confirmEmail}
              onChange={(e) => setConfirmEmail(e.target.value)}
              autoComplete="off"
            />
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose} disabled={deleteUser.isPending}>
            Cancel
          </Button>
          <Button
            variant="destructive"
            onClick={handleDelete}
            disabled={!canDelete || deleteUser.isPending}
          >
            {deleteUser.isPending ? 'Deleting...' : 'Delete User'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
