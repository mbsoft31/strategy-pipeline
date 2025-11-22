/**
 * ProjectDetail Component
 * Main project view with stage progression timeline
 */
import { useParams, Link } from '@tanstack/react-router'
import { ArrowLeft, CheckCircle2, Circle, Clock, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useArtifact } from '@/lib/api/hooks'
import type { ProjectContext, Stage } from '@/types/project'

const STAGES = [
  { id: 'project-setup', name: 'Project Setup', number: 0 },
  { id: 'problem-framing', name: 'Problem Framing', number: 1 },
  { id: 'research-questions', name: 'Research Questions', number: 2 },
  { id: 'search-concept-expansion', name: 'Search Expansion', number: 3 },
  { id: 'database-query-plan', name: 'Query Plan', number: 4 },
  { id: 'screening-criteria', name: 'Screening Criteria', number: 5 },
  { id: 'strategy-export', name: 'Export Strategy', number: 6 },
]

export default function ProjectDetail() {
  const { projectId } = useParams({ strict: false }) as { projectId: string }

  // Fetch project context
  const {
    data: projectContext,
    isLoading,
    error,
  } = useArtifact<ProjectContext>(projectId, 'ProjectContext')

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      </div>
    )
  }

  if (error || !projectContext) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <Card className="border-destructive">
          <CardContent className="pt-6">
            <p className="text-destructive">Failed to load project. Please try again.</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  const getStageStatus = (stageNumber: number): Stage['status'] => {
    // For now, only stage 0 is approved, others are not started
    // This should come from the backend in a real implementation
    if (stageNumber === 0 && projectContext.status === 'approved') {
      return 'approved'
    }
    if (stageNumber === 0 && projectContext.status === 'draft') {
      return 'draft'
    }
    return 'not_started'
  }

  const currentStageIndex = STAGES.findIndex(
    (stage) => getStageStatus(stage.number) === 'draft' || getStageStatus(stage.number) === 'not_started'
  )

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      {/* Back Button */}
      <Link to="/" className="inline-flex items-center text-muted-foreground hover:text-foreground mb-6">
        <ArrowLeft className="mr-2 h-4 w-4" />
        Back to Projects
      </Link>

      {/* Project Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">{projectContext.title}</h1>
        <p className="text-muted-foreground">{projectContext.background_summary}</p>
      </div>

      {/* Stage Timeline */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle>Pipeline Progress</CardTitle>
          <CardDescription>Complete each stage to unlock the next</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between gap-2">
            {STAGES.map((stage, index) => {
              const status = getStageStatus(stage.number)
              const isCompleted = status === 'approved'
              const isCurrent = index === currentStageIndex
              const isLocked = status === 'not_started' && !isCurrent

              return (
                <div key={stage.id} className="flex items-center flex-1">
                  <Link
                    to="/projects/$projectId/stages/$stageName"
                    params={{ projectId, stageName: stage.id }}
                    className={`flex flex-col items-center gap-2 flex-1 ${
                      isLocked ? 'cursor-not-allowed opacity-50' : 'hover:opacity-80'
                    }`}
                    disabled={isLocked}
                  >
                    <div
                      className={`w-12 h-12 rounded-full flex items-center justify-center border-2 transition-all ${
                        isCompleted
                          ? 'bg-green-500 border-green-500 text-white'
                          : isCurrent
                            ? 'bg-primary border-primary text-primary-foreground animate-pulse'
                            : 'bg-background border-muted-foreground text-muted-foreground'
                      }`}
                    >
                      {isCompleted ? (
                        <CheckCircle2 className="h-6 w-6" />
                      ) : isCurrent ? (
                        <Clock className="h-6 w-6" />
                      ) : (
                        <Circle className="h-6 w-6" />
                      )}
                    </div>
                    <div className="text-center">
                      <div className="text-xs font-medium">Stage {stage.number}</div>
                      <div className="text-xs text-muted-foreground max-w-[100px] truncate">
                        {stage.name}
                      </div>
                    </div>
                  </Link>
                  {index < STAGES.length - 1 && (
                    <div
                      className={`flex-1 h-0.5 ${
                        isCompleted ? 'bg-green-500' : 'bg-muted'
                      }`}
                    />
                  )}
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>

      {/* Project Details */}
      <div className="grid md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Research Domain</CardTitle>
          </CardHeader>
          <CardContent>
            <p>{projectContext.research_domain}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Expected Outcomes</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="list-disc list-inside space-y-1">
              {projectContext.expected_outcomes?.map((outcome, i) => (
                <li key={i}>{outcome}</li>
              ))}
            </ul>
          </CardContent>
        </Card>
      </div>

      {/* Current Stage Card */}
      <Card className="mt-6">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Current Stage: {STAGES[currentStageIndex]?.name}</CardTitle>
              <CardDescription>
                {currentStageIndex === 0
                  ? 'Review and approve your project setup to begin'
                  : 'Complete this stage to progress further'}
              </CardDescription>
            </div>
            <Link
              to="/projects/$projectId/stages/$stageName"
              params={{
                projectId,
                stageName: STAGES[currentStageIndex]?.id || 'project-setup',
              }}
            >
              <Button size="lg">
                {getStageStatus(STAGES[currentStageIndex]?.number) === 'approved'
                  ? 'View Stage'
                  : 'Continue'}
              </Button>
            </Link>
          </div>
        </CardHeader>
      </Card>
    </div>
  )
}

