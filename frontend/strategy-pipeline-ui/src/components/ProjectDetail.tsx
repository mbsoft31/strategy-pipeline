/**
 * ProjectDetail Component
 * Main project view with stage progression timeline
 */
import { useParams, Link } from '@tanstack/react-router'
import { ArrowLeft, Loader2, AlertCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { StageTimeline } from '@/components/StageTimeline'
import { useProject } from '@/lib/api/hooks'

const STAGES = [
  {
    id: 'project-setup',
    name: 'Project Setup',
    number: 0,
    description: 'Define your research idea and project context',
    status: 'approved' as const
  },
  {
    id: 'problem-framing',
    name: 'Problem Framing',
    number: 1,
    description: 'Frame the research problem with PICO elements',
    status: 'not_started' as const
  },
  {
    id: 'research-questions',
    name: 'Research Questions',
    number: 2,
    description: 'Generate structured research questions',
    status: 'not_started' as const
  },
  {
    id: 'search-concept-expansion',
    name: 'Search Expansion',
    number: 3,
    description: 'Expand search concepts with synonyms',
    status: 'not_started' as const
  },
  {
    id: 'database-query-plan',
    name: 'Query Plan',
    number: 4,
    description: 'Generate database-specific Boolean queries',
    status: 'not_started' as const
  },
]

export default function ProjectDetail() {
  const { projectId } = useParams({ strict: false }) as { projectId: string }

  // Fetch full project details
  const {
    data: project,
    isLoading,
    error,
  } = useProject(projectId)

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          <span className="ml-2 text-muted-foreground">Loading project...</span>
        </div>
      </div>
    )
  }

  if (error || !project) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            Failed to load project. Please try again.
          </AlertDescription>
        </Alert>
        <Button asChild className="mt-4">
          <Link to="/">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Dashboard
          </Link>
        </Button>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      {/* Back Button */}
      <Button asChild variant="ghost" className="mb-6">
        <Link to="/">
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Projects
        </Link>
      </Button>

      {/* Project Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">{project.title}</h1>
        {project.description && (
          <p className="text-lg text-muted-foreground">{project.description}</p>
        )}
      </div>

      {/* Stage Timeline - New Component! */}
      <StageTimeline
        projectId={projectId}
        stages={STAGES}
        currentStage={project.current_stage || 0}
      />
    </div>
  )
}

