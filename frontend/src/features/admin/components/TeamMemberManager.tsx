/**
 * TeamMemberManager - Sheet for managing team members.
 */

import { useState, useMemo } from 'react'
import { X, UserPlus, Search } from 'lucide-react'
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/sheet'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { useTeam, useUsers, useAddTeamMember, useRemoveTeamMember } from '../hooks'
import type { Team, AdminUser } from '../types'

interface TeamMemberManagerProps {
  open: boolean
  onClose: () => void
  team: Team | null
}

export function TeamMemberManager({ open, onClose, team }: TeamMemberManagerProps) {
  const [search, setSearch] = useState('')
  const { data: teamData, isLoading: isLoadingTeam } = useTeam(team?.id || '')
  const { data: usersData, isLoading: isLoadingUsers } = useUsers(1, 100, search)
  const addMember = useAddTeamMember()
  const removeMember = useRemoveTeamMember()

  // Filter out users who are already members
  const availableUsers = useMemo(() => {
    if (!usersData || !teamData) return []
    const memberIds = new Set(teamData.team.member_ids)
    return usersData.items.filter((user) => !memberIds.has(user.id))
  }, [usersData, teamData])

  const handleAddMember = (userId: string) => {
    if (!team) return
    addMember.mutate({ teamId: team.id, userId })
  }

  const handleRemoveMember = (userId: string) => {
    if (!team) return
    removeMember.mutate({ teamId: team.id, userId })
  }

  return (
    <Sheet open={open} onOpenChange={(open) => !open && onClose()}>
      <SheetContent className="sm:max-w-md">
        <SheetHeader>
          <SheetTitle>Manage Members</SheetTitle>
          <SheetDescription>
            Add or remove members from <strong>{team?.name}</strong>
          </SheetDescription>
        </SheetHeader>

        <div className="mt-6 space-y-6">
          {/* Current Members */}
          <div>
            <h4 className="text-sm font-medium mb-3">
              Current Members ({teamData?.team.member_ids.length || 0})
            </h4>
            {isLoadingTeam ? (
              <MemberListSkeleton />
            ) : teamData?.members.length === 0 ? (
              <p className="text-sm text-muted-foreground py-4 text-center">
                No members yet. Add users below.
              </p>
            ) : (
              <div className="space-y-2">
                {teamData?.members.map((member) => (
                  <MemberItem
                    key={member.id}
                    user={member}
                    onRemove={() => handleRemoveMember(member.id)}
                    isRemoving={
                      removeMember.isPending &&
                      removeMember.variables?.userId === member.id
                    }
                  />
                ))}
              </div>
            )}
          </div>

          {/* Add Members */}
          <div>
            <h4 className="text-sm font-medium mb-3">Add Members</h4>
            <div className="relative mb-3">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search users..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-9"
              />
            </div>
            {isLoadingUsers ? (
              <MemberListSkeleton />
            ) : availableUsers.length === 0 ? (
              <p className="text-sm text-muted-foreground py-4 text-center">
                {search ? 'No users found' : 'All users are already members'}
              </p>
            ) : (
              <div className="space-y-2 max-h-[300px] overflow-y-auto">
                {availableUsers.map((user) => (
                  <AddUserItem
                    key={user.id}
                    user={user}
                    onAdd={() => handleAddMember(user.id)}
                    isAdding={
                      addMember.isPending && addMember.variables?.userId === user.id
                    }
                  />
                ))}
              </div>
            )}
          </div>
        </div>
      </SheetContent>
    </Sheet>
  )
}

interface MemberItemProps {
  user: AdminUser
  onRemove: () => void
  isRemoving: boolean
}

function MemberItem({ user, onRemove, isRemoving }: MemberItemProps) {
  return (
    <div className="flex items-center justify-between p-2 rounded-md bg-muted/50">
      <div className="min-w-0">
        <p className="text-sm font-medium truncate">{user.username}</p>
        <p className="text-xs text-muted-foreground truncate">{user.email}</p>
      </div>
      <Button
        variant="ghost"
        size="icon"
        onClick={onRemove}
        disabled={isRemoving}
        className="shrink-0"
      >
        <X className="h-4 w-4" />
      </Button>
    </div>
  )
}

interface AddUserItemProps {
  user: AdminUser
  onAdd: () => void
  isAdding: boolean
}

function AddUserItem({ user, onAdd, isAdding }: AddUserItemProps) {
  return (
    <div className="flex items-center justify-between p-2 rounded-md hover:bg-muted/50">
      <div className="min-w-0">
        <p className="text-sm font-medium truncate">{user.username}</p>
        <p className="text-xs text-muted-foreground truncate">{user.email}</p>
      </div>
      <Button variant="outline" size="sm" onClick={onAdd} disabled={isAdding} className="shrink-0">
        <UserPlus className="h-4 w-4 mr-1" />
        {isAdding ? 'Adding...' : 'Add'}
      </Button>
    </div>
  )
}

function MemberListSkeleton() {
  return (
    <div className="space-y-2">
      {[...Array(3)].map((_, i) => (
        <div key={i} className="flex items-center justify-between p-2">
          <div className="space-y-1">
            <Skeleton className="h-4 w-24" />
            <Skeleton className="h-3 w-32" />
          </div>
          <Skeleton className="h-8 w-8" />
        </div>
      ))}
    </div>
  )
}
