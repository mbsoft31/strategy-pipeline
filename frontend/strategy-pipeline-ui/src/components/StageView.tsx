/**
 * StageView Component - Clean Working Version
 */
import { useParams, Link, useNavigate } from '@tanstack/react-router'
import { ArrowLeft, CheckCircle, Loader2, Play, AlertCircle, RefreshCw } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { toast } from '@/components/ui/toast'
import { ArtifactViewer } from '@/components/ArtifactViewer'
import { useArtifact, useApproveStage, useRunStage } from '@/lib/api/hooks'

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
  const params = useParams({ strict: false })
  const projectId = params.projectId as string
  const stageName = params.stageName as string
  const navigate = useNavigate()

  const stageConfig = STAGE_CONFIG[stageName] || STAGE_CONFIG['project-setup']

  // Fetch artifact
  const { data: artifact, isLoading, error, refetch } = useArtifact(projectId, stageConfig.artifactType)

  // Mutations
  const runStage = useRunStage()
  const approveStage = useApproveStage()

  const handleRunStage = async () => {
    try {
      await runStage.mutateAsync({ projectId, stageName })
      await refetch()
      toast.success('Stage executed!', 'Review the generated content below')
    } catch (error: any) {
      console.error('Failed to run stage:', error)
      toast.error('Failed to run stage', error?.message || 'Please try again')
    }
  }

  const handleApprove = async () => {
    try {
      await approveStage.mutateAsync({
        projectId,
        stageName,
        edits: {},
        userNotes: undefined,
      })

      toast.success('Stage approved!', 'Moving to next stage')

      // Navigate back to project detail
      setTimeout(() => {
        navigate({ to: '/projects/$projectId', params: { projectId } })
      }, 1000)
    } catch (error: any) {
      console.error('Failed to approve stage:', error)
      toast.error('Failed to approve stage', error?.message || 'Please try again')
    }
  }

  // Loading state
  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-5xl">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          <span className="ml-2 text-muted-foreground">Loading stage...</span>
        </div>
      </div>
    )
  }

  // Error state - stage not run yet
  if (error && !artifact) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-5xl">
        <Button asChild variant="ghost" className="mb-6">
          <Link to="/projects/$projectId" params={{ projectId }}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Project
          </Link>
        </Button>

        <Alert className="mb-6">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Stage Not Generated</AlertTitle>
          <AlertDescription>
            This stage hasn't been generated yet. Click the button below to run it.
          </AlertDescription>
        </Alert>

        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <h3 className="text-lg font-semibold mb-2">{stageConfig.title}</h3>
              <p className="text-muted-foreground mb-4">{stageConfig.description}</p>
              <Button
                onClick={handleRunStage}
                disabled={runStage.isPending}
                size="lg"
              >
                {runStage.isPending ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Play className="mr-2 h-4 w-4" />
                    Run Stage
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  // No artifact state
  if (!artifact) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-5xl">
        <Button asChild variant="ghost" className="mb-6">
          <Link to="/projects/$projectId" params={{ projectId }}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Project
          </Link>
        </Button>

        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-muted-foreground mb-4">No artifact found for this stage.</p>
              <Button onClick={handleRunStage} disabled={runStage.isPending}>
                {runStage.isPending ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Play className="mr-2 h-4 w-4" />
                    Run Stage
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  // Success state - show artifact
  return (
    <div className="container mx-auto px-4 py-8 max-w-5xl">
      {/* Back Button */}
      <Button asChild variant="ghost" className="mb-6">
        <Link to="/projects/$projectId" params={{ projectId }}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Project
        </Link>
      </Button>

      {/* Stage Header */}
      <div className="mb-6">
        <h1 className="text-4xl font-bold mb-2">{stageConfig.title}</h1>
        <p className="text-lg text-muted-foreground">{stageConfig.description}</p>
      </div>

      {/* Artifact Display */}
      <ArtifactViewer
        artifact={artifact}
        artifactType={stageConfig.artifactType}
        title={stageConfig.title}
      />

      {/* Action Buttons */}
      <Card className="mt-6">
        <CardContent className="pt-6">
          <div className="flex gap-3 justify-end">
            <Button
              variant="outline"
              onClick={handleRunStage}
              disabled={runStage.isPending}
            >
              {runStage.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Re-generating...
                </>
              ) : (
                <>
                  <RefreshCw className="mr-2 h-4 w-4" />
                  Re-run Stage
                </>
              )}
            </Button>

            <Button
              onClick={handleApprove}
              disabled={approveStage.isPending}
            >
              {approveStage.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Approving...
                </>
              ) : (
                <>
                  <CheckCircle className="mr-2 h-4 w-4" />
                  Approve & Continue
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

