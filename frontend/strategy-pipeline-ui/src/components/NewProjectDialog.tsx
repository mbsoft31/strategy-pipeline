/**
 * NewProjectDialog Component
 * Modal for creating a new project from raw idea
 */
import { useState } from 'react'
import { useNavigate } from '@tanstack/react-router'
import { Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { useCreateProject } from '@/lib/api/hooks'

interface NewProjectDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export default function NewProjectDialog({ open, onOpenChange }: NewProjectDialogProps) {
  const [rawIdea, setRawIdea] = useState('')
  const navigate = useNavigate()
  const createProject = useCreateProject()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!rawIdea.trim()) {
      return
    }

    try {
      const result = await createProject.mutateAsync(rawIdea)
      onOpenChange(false)
      setRawIdea('')
      navigate({ to: '/projects/$projectId', params: { projectId: result.project_id } })
    } catch (error) {
      console.error('Failed to create project:', error)
    }
  }

  if (!open) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50"
        onClick={() => onOpenChange(false)}
      />

      {/* Dialog */}
      <div className="relative bg-background rounded-lg shadow-lg max-w-2xl w-full mx-4 p-6">
        <h2 className="text-2xl font-bold mb-4">Create New Project</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="raw_idea">
              Research Idea
            </Label>
            <Textarea
              id="raw_idea"
              placeholder="Describe your research idea... For example: 'I want to understand how retrieval augmentation helps reduce hallucinations in large language models'"
              value={rawIdea}
              onChange={(e) => setRawIdea(e.target.value)}
              rows={6}
              className="mt-2"
              required
            />
            <p className="text-sm text-muted-foreground mt-2">
              Provide a brief description of your research topic. The AI will help structure this into a systematic literature review.
            </p>
          </div>

          <div className="flex justify-end gap-3">
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={createProject.isPending}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={createProject.isPending || !rawIdea.trim()}>
              {createProject.isPending && (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              )}
              Create Project
            </Button>
          </div>

          {createProject.isError && (
            <p className="text-sm text-destructive">
              Failed to create project. Please try again.
            </p>
          )}
        </form>
      </div>
    </div>
  )
}

