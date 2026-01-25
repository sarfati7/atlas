/**
 * TeamForm - Dialog for creating and editing teams.
 */

import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
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
import { useCreateTeam, useUpdateTeam } from '../hooks'
import type { Team } from '../types'

const teamSchema = z.object({
  name: z
    .string()
    .min(3, 'Name must be at least 3 characters')
    .max(50, 'Name must be at most 50 characters'),
})

type TeamFormData = z.infer<typeof teamSchema>

interface TeamFormProps {
  open: boolean
  onClose: () => void
  team?: Team | null
}

export function TeamForm({ open, onClose, team }: TeamFormProps) {
  const isEditing = !!team
  const createTeam = useCreateTeam()
  const updateTeam = useUpdateTeam()

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<TeamFormData>({
    resolver: zodResolver(teamSchema),
    defaultValues: {
      name: team?.name || '',
    },
  })

  // Reset form when dialog opens/closes or team changes
  useEffect(() => {
    if (open) {
      reset({ name: team?.name || '' })
    }
  }, [open, team, reset])

  const onSubmit = async (data: TeamFormData) => {
    if (isEditing && team) {
      await updateTeam.mutateAsync({ id: team.id, data: { name: data.name } })
    } else {
      await createTeam.mutateAsync({ name: data.name })
    }
    onClose()
  }

  const isPending = createTeam.isPending || updateTeam.isPending

  return (
    <Dialog open={open} onOpenChange={(open) => !open && onClose()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{isEditing ? 'Edit Team' : 'Create Team'}</DialogTitle>
          <DialogDescription>
            {isEditing
              ? 'Update the team name. Team members will not be affected.'
              : 'Create a new team to organize users and manage permissions.'}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit)}>
          <div className="py-4">
            <Label htmlFor="name">Team Name</Label>
            <Input
              id="name"
              placeholder="Engineering"
              className="mt-2"
              {...register('name')}
              autoFocus
            />
            {errors.name && (
              <p className="text-sm text-destructive mt-1">{errors.name.message}</p>
            )}
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose} disabled={isPending}>
              Cancel
            </Button>
            <Button type="submit" disabled={isPending}>
              {isPending ? (isEditing ? 'Saving...' : 'Creating...') : isEditing ? 'Save' : 'Create'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
