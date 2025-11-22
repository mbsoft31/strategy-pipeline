/**
 * StageView Component
 * Display and edit individual stage artifacts
 */
import { useState } from 'react'
import { useParams, Link, useNavigate } from '@tanstack/react-router'
import { ArrowLeft, CheckCircle, Loader2, Save, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Textarea } from '@/components/ui/textarea'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useArtifact, useApproveStage, useRunStage } from '@/lib/api/hooks'
import type { ProjectContext, ProblemFraming } from '@/types/project'

const STAGE_CONFIG: Record<string, { title: string; description: string; artifactType: string }> = {
  'project-setup': {
    title: 'Project Setup',
    description: 'Review and refine the AI-generated project context',
    artifactType: 'ProjectContext',
  },
  'problem-framing': {
    title: 'Problem Framing',
    description: 'Define the research problem and scope',
    artifactType: 'ProblemFraming',
  },
  'research-questions': {
    title: 'Research Questions',
    description: 'Generate primary and secondary research questions',
    artifactType: 'ResearchQuestionSet',
  },
  'search-concept-expansion': {
    title: 'Search Concept Expansion',
    description: 'Expand search concepts with synonyms and variations',
    artifactType: 'SearchConceptBlocks',
  },
  'database-query-plan': {
    title: 'Database Query Plan',
    description: 'Create database search strategy',
    artifactType: 'DatabaseQueryPlan',
  },
}

export default function StageView() {
  const { projectId, stageName } = useParams({ strict: false }) as {
    projectId: string
    stageName: string
  }
  const navigate = useNavigate()

  const stageConfig = STAGE_CONFIG[stageName] || STAGE_CONFIG['project-setup']
  const [isEditing, setIsEditing] = useState(false)
  const [editedData, setEditedData] = useState<Record<string, unknown>>({})
  const [userNotes, setUserNotes] = useState('')

  // Fetch artifact
  const { data: artifact, isLoading, error } = useArtifact(projectId, stageConfig.artifactType)

  // Mutations
  const runStage = useRunStage()
  const approveStage = useApproveStage()

  const handleRunStage = async () => {
    try {
      await runStage.mutateAsync({ projectId, stageName })
    } catch (error) {
      console.error('Failed to run stage:', error)
    }
  }

  const handleApprove = async () => {
    try {
      await approveStage.mutateAsync({
        projectId,
        stageName,
        edits: isEditing ? editedData : undefined,
        userNotes: userNotes || undefined,
      })

      // Navigate back to project detail
      navigate({ to: '/projects/$projectId', params: { projectId } })
    } catch (error) {
      console.error('Failed to approve stage:', error)
    }
  }

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-5xl">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      </div>
    )
  }

  if (error && !artifact) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-5xl">
        <Card className="border-destructive">
          <CardContent className="pt-6">
            <p className="text-destructive mb-4">
              This stage hasn't been generated yet.
            </p>
            <Button onClick={handleRunStage} disabled={runStage.isPending}>
              {runStage.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Generate Stage
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-5xl">
      {/* Back Button */}
      <Link
        to="/projects/$projectId"
        params={{ projectId }}
        className="inline-flex items-center text-muted-foreground hover:text-foreground mb-6"
      >
        <ArrowLeft className="mr-2 h-4 w-4" />
        Back to Project
      </Link>

      {/* Stage Header */}
      <div className="mb-6">
        <h1 className="text-4xl font-bold mb-2">{stageConfig.title}</h1>
        <p className="text-muted-foreground">{stageConfig.description}</p>
      </div>

      {/* Artifact Display */}
      <Card className="mb-6">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>AI-Generated Draft</CardTitle>
              <CardDescription>
                Review the content below. You can edit any field before approving.
              </CardDescription>
            </div>
            <Button
              variant="outline"
              onClick={() => setIsEditing(!isEditing)}
            >
              {isEditing ? (
                <>
                  <X className="mr-2 h-4 w-4" />
                  Cancel Edit
                </>
              ) : (
                <>
                  <Save className="mr-2 h-4 w-4" />
                  Edit
                </>
              )}
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {stageName === 'project-setup' && artifact !== null && artifact !== undefined && (
            <ProjectSetupForm
              artifact={artifact as ProjectContext}
              isEditing={isEditing}
              editedData={editedData}
              onEdit={setEditedData}
            />
          )}
          {stageName === 'problem-framing' && artifact !== null && artifact !== undefined && (
            <ProblemFramingForm
              artifact={artifact as ProblemFraming}
              isEditing={isEditing}
              editedData={editedData}
              onEdit={setEditedData}
            />
          )}
        </CardContent>
      </Card>

      {/* User Notes */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Notes (Optional)</CardTitle>
          <CardDescription>Add any comments or observations</CardDescription>
        </CardHeader>
        <CardContent>
          <Textarea
            value={userNotes}
            onChange={(e) => setUserNotes(e.target.value)}
            placeholder="Add your notes here..."
            rows={4}
          />
        </CardContent>
      </Card>

      {/* Actions */}
      <div className="flex justify-end gap-3">
        <Button variant="outline" asChild>
          <Link to="/projects/$projectId" params={{ projectId }}>
            Cancel
          </Link>
        </Button>
        <Button
          size="lg"
          onClick={handleApprove}
          disabled={approveStage.isPending}
        >
          {approveStage.isPending ? (
            <Loader2 className="mr-2 h-5 w-5 animate-spin" />
          ) : (
            <CheckCircle className="mr-2 h-5 w-5" />
          )}
          Approve & Continue
        </Button>
      </div>

      {approveStage.isError && (
        <p className="text-sm text-destructive mt-4 text-right">
          Failed to approve stage. Please try again.
        </p>
      )}
    </div>
  )
}

// Form components for different artifacts
function ProjectSetupForm({
  artifact,
  isEditing,
  editedData,
  onEdit,
}: {
  artifact: ProjectContext
  isEditing: boolean
  editedData: Record<string, unknown>
  onEdit: (data: Record<string, unknown>) => void
}) {
  const getValue = (field: keyof ProjectContext) =>
    (editedData[field] as string) ?? artifact[field]

  const handleChange = (field: string, value: unknown) => {
    onEdit({ ...editedData, [field]: value })
  }

  return (
    <div className="space-y-6">
      <div>
        <Label>Title</Label>
        {isEditing ? (
          <Input
            value={getValue('title') as string}
            onChange={(e) => handleChange('title', e.target.value)}
            className="mt-2"
          />
        ) : (
          <p className="mt-2 text-lg font-medium">{artifact.title}</p>
        )}
      </div>

      <div>
        <Label>Background Summary</Label>
        {isEditing ? (
          <Textarea
            value={getValue('background_summary') as string}
            onChange={(e) => handleChange('background_summary', e.target.value)}
            rows={4}
            className="mt-2"
          />
        ) : (
          <p className="mt-2 text-muted-foreground">{artifact.background_summary}</p>
        )}
      </div>

      <div>
        <Label>Research Domain</Label>
        {isEditing ? (
          <Input
            value={getValue('research_domain') as string}
            onChange={(e) => handleChange('research_domain', e.target.value)}
            className="mt-2"
          />
        ) : (
          <p className="mt-2">{artifact.research_domain}</p>
        )}
      </div>

      <div>
        <Label>Expected Outcomes</Label>
        <ul className="mt-2 list-disc list-inside space-y-1">
          {artifact.expected_outcomes?.map((outcome, i) => (
            <li key={i}>{outcome}</li>
          ))}
        </ul>
      </div>
    </div>
  )
}

function ProblemFramingForm({
  artifact,
  isEditing,
  editedData,
  onEdit,
}: {
  artifact: ProblemFraming
  isEditing: boolean
  editedData: Record<string, unknown>
  onEdit: (data: Record<string, unknown>) => void
}) {
  const getValue = (field: keyof ProblemFraming) =>
    (editedData[field] as string) ?? artifact[field]

  const handleChange = (field: string, value: unknown) => {
    onEdit({ ...editedData, [field]: value })
  }

  return (
    <div className="space-y-6">
      <div>
        <Label>Problem Statement</Label>
        {isEditing ? (
          <Textarea
            value={getValue('problem_statement') as string}
            onChange={(e) => handleChange('problem_statement', e.target.value)}
            rows={4}
            className="mt-2"
          />
        ) : (
          <p className="mt-2">{artifact.problem_statement}</p>
        )}
      </div>

      <div>
        <Label>Goals</Label>
        <ul className="mt-2 list-disc list-inside space-y-1">
          {artifact.goals.map((goal, i) => (
            <li key={i}>{goal}</li>
          ))}
        </ul>
      </div>

      <div>
        <Label>PICO Elements</Label>
        <div className="mt-2 grid md:grid-cols-2 gap-4">
          {artifact.pico_elements && Object.entries(artifact.pico_elements).map(([key, value]) =>
            value ? (
              <div key={key}>
                <strong className="capitalize">{key}:</strong> {value}
              </div>
            ) : null
          )}
        </div>
      </div>

      <div>
        <Label>Scope Boundaries</Label>
        <ul className="mt-2 list-disc list-inside space-y-1">
          {artifact.scope_boundaries?.map((boundary, i) => (
            <li key={i}>{boundary}</li>
          ))}
        </ul>
      </div>
    </div>
  )
}

