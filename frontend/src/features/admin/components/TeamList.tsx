/**
 * TeamList - Table displaying teams with actions.
 */

import { useState } from 'react'
import { formatDistanceToNow } from 'date-fns'
import { Pencil, Trash2, Users } from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import { Skeleton } from '@/components/ui/skeleton'
import { useDeleteTeam } from '../hooks'
import type { Team } from '../types'

interface TeamListProps {
  teams: Team[]
  isLoading: boolean
  onEdit: (team: Team) => void
  onManageMembers: (team: Team) => void
  page: number
  pageSize: number
  total: number
  onPageChange: (page: number) => void
}

export function TeamList({
  teams,
  isLoading,
  onEdit,
  onManageMembers,
  page,
  pageSize,
  total,
  onPageChange,
}: TeamListProps) {
  const deleteTeam = useDeleteTeam()
  const [teamToDelete, setTeamToDelete] = useState<Team | null>(null)

  const handleDelete = () => {
    if (!teamToDelete) return
    deleteTeam.mutate(teamToDelete.id, {
      onSuccess: () => setTeamToDelete(null),
    })
  }

  const totalPages = Math.ceil(total / pageSize)

  if (isLoading) {
    return <TeamListSkeleton />
  }

  if (teams.length === 0) {
    return <TeamListEmpty />
  }

  return (
    <>
      <div className="rounded-lg border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead className="w-[100px]">Members</TableHead>
              <TableHead className="w-[150px]">Created</TableHead>
              <TableHead className="w-[120px] text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {teams.map((team) => (
              <TableRow key={team.id}>
                <TableCell className="font-medium">{team.name}</TableCell>
                <TableCell>
                  <span className="text-muted-foreground">{team.member_ids.length}</span>
                </TableCell>
                <TableCell className="text-muted-foreground text-sm">
                  {formatDistanceToNow(new Date(team.created_at), { addSuffix: true })}
                </TableCell>
                <TableCell className="text-right">
                  <div className="flex justify-end gap-1">
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => onManageMembers(team)}
                      title="Manage members"
                    >
                      <Users className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => onEdit(team)}
                      title="Edit team"
                    >
                      <Pencil className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => setTeamToDelete(team)}
                      title="Delete team"
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
            teams
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

      {/* Delete confirmation dialog */}
      <AlertDialog open={!!teamToDelete} onOpenChange={() => setTeamToDelete(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete team?</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete <strong>{teamToDelete?.name}</strong>? This action
              cannot be undone. All team members will be removed from this team.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={deleteTeam.isPending}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              disabled={deleteTeam.isPending}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              {deleteTeam.isPending ? 'Deleting...' : 'Delete team'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  )
}

function TeamListSkeleton() {
  return (
    <div className="rounded-lg border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Name</TableHead>
            <TableHead className="w-[100px]">Members</TableHead>
            <TableHead className="w-[150px]">Created</TableHead>
            <TableHead className="w-[120px] text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {[...Array(5)].map((_, i) => (
            <TableRow key={i}>
              <TableCell>
                <Skeleton className="h-5 w-32" />
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

function TeamListEmpty() {
  return (
    <div className="rounded-lg border border-dashed p-12 text-center">
      <Users className="h-12 w-12 mx-auto text-muted-foreground/50" />
      <h3 className="mt-4 text-lg font-medium">No teams yet</h3>
      <p className="mt-2 text-sm text-muted-foreground">
        Create your first team to organize users and manage permissions.
      </p>
    </div>
  )
}
