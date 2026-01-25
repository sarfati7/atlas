/**
 * AdminTeams - Team management page for admin users.
 */

import { useState } from 'react'
import { Plus } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { TeamList } from '@/features/admin/components/TeamList'
import { TeamForm } from '@/features/admin/components/TeamForm'
import { TeamMemberManager } from '@/features/admin/components/TeamMemberManager'
import { useTeams } from '@/features/admin/hooks'
import type { Team } from '@/features/admin/types'

export function AdminTeamsPage() {
  const [page, setPage] = useState(1)
  const pageSize = 10
  const { data, isLoading } = useTeams(page, pageSize)

  // Form dialog state
  const [formOpen, setFormOpen] = useState(false)
  const [editingTeam, setEditingTeam] = useState<Team | null>(null)

  // Member manager sheet state
  const [memberManagerOpen, setMemberManagerOpen] = useState(false)
  const [managingTeam, setManagingTeam] = useState<Team | null>(null)

  const handleCreate = () => {
    setEditingTeam(null)
    setFormOpen(true)
  }

  const handleEdit = (team: Team) => {
    setEditingTeam(team)
    setFormOpen(true)
  }

  const handleManageMembers = (team: Team) => {
    setManagingTeam(team)
    setMemberManagerOpen(true)
  }

  const handleFormClose = () => {
    setFormOpen(false)
    setEditingTeam(null)
  }

  const handleMemberManagerClose = () => {
    setMemberManagerOpen(false)
    setManagingTeam(null)
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto max-w-5xl px-4 py-8">
        {/* Header */}
        <header className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-foreground">Team Management</h1>
            <p className="text-muted-foreground">Create and manage teams for your organization</p>
          </div>
          <Button onClick={handleCreate} className="gap-2">
            <Plus className="h-4 w-4" />
            Create Team
          </Button>
        </header>

        {/* Team List */}
        <TeamList
          teams={data?.items || []}
          isLoading={isLoading}
          onEdit={handleEdit}
          onManageMembers={handleManageMembers}
          page={page}
          pageSize={pageSize}
          total={data?.total || 0}
          onPageChange={setPage}
        />

        {/* Create/Edit Form Dialog */}
        <TeamForm open={formOpen} onClose={handleFormClose} team={editingTeam} />

        {/* Member Manager Sheet */}
        <TeamMemberManager
          open={memberManagerOpen}
          onClose={handleMemberManagerClose}
          team={managingTeam}
        />
      </div>
    </div>
  )
}
