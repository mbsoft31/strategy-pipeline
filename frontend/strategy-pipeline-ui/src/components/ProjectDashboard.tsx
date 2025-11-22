/**
 * ProjectDashboard Component
 * Displays list of all projects with search/filter capabilities
 */
import { useState } from 'react'
import { Link } from '@tanstack/react-router'
import { Search, Plus, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { useProjects } from '@/lib/api/hooks'
import NewProjectDialog from './NewProjectDialog'
import type { Project } from '@/types/project'

export default function ProjectDashboard() {
  const [searchQuery, setSearchQuery] = useState('')
  const [filterStatus, setFilterStatus] = useState<'all' | 'draft' | 'in_progress' | 'completed'>('all')
  const [showNewProject, setShowNewProject] = useState(false)

  const { data: projects, isLoading, error } = useProjects()

  // Filter projects based on search and status
  const filteredProjects = projects?.filter((project) => {
    const matchesSearch = project.title.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesFilter = filterStatus === 'all' || project.status === filterStatus
    return matchesSearch && matchesFilter
  }) || []

  const getStatusBadge = (status: Project['status']) => {
    const variants = {
      draft: 'outline',
      in_progress: 'warning',
      completed: 'success',
    } as const

    return (
      <Badge variant={variants[status]}>
        {status.replace('_', ' ').toUpperCase()}
      </Badge>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-4xl font-bold text-foreground">Strategy Pipeline</h1>
          <p className="text-muted-foreground mt-2">
            Intelligent SLR Automation Platform
          </p>
        </div>
        <Button size="lg" onClick={() => setShowNewProject(true)}>
          <Plus className="mr-2 h-5 w-5" />
          New Project
        </Button>
      </div>

      {/* Search and Filters */}
      <div className="flex gap-4 mb-6">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search projects..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>
        <div className="flex gap-2">
          {(['all', 'draft', 'in_progress', 'completed'] as const).map((status) => (
            <Button
              key={status}
              variant={filterStatus === status ? 'default' : 'outline'}
              onClick={() => setFilterStatus(status)}
            >
              {status === 'all' ? 'All' : status.replace('_', ' ')}
            </Button>
          ))}
        </div>
      </div>

      {/* Project List */}
      {isLoading && (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      )}

      {error && (
        <Card className="border-destructive">
          <CardContent className="pt-6">
            <p className="text-destructive">Failed to load projects. Please try again.</p>
          </CardContent>
        </Card>
      )}

      {!isLoading && !error && filteredProjects.length === 0 && (
        <Card>
          <CardContent className="pt-6 text-center py-12">
            <p className="text-muted-foreground mb-4">
              {searchQuery || filterStatus !== 'all'
                ? 'No projects found matching your criteria.'
                : 'No projects yet. Create your first project to get started!'}
            </p>
            {!searchQuery && filterStatus === 'all' && (
              <Button onClick={() => setShowNewProject(true)}>
                <Plus className="mr-2 h-4 w-4" />
                Create First Project
              </Button>
            )}
          </CardContent>
        </Card>
      )}

      {!isLoading && !error && filteredProjects.length > 0 && (
        <div className="grid gap-4">
          {filteredProjects.map((project) => (
            <Card key={project.id} className="hover:shadow-md transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-xl mb-2">
                      <Link
                        to="/projects/$projectId"
                        params={{ projectId: project.id }}
                        className="hover:underline"
                      >
                        {project.title}
                      </Link>
                    </CardTitle>
                    {project.description && (
                      <CardDescription>{project.description}</CardDescription>
                    )}
                  </div>
                  {getStatusBadge(project.status)}
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between text-sm text-muted-foreground">
                  <div className="flex items-center gap-4">
                    {project.current_stage && (
                      <span>Current: {project.current_stage}</span>
                    )}
                    <span>
                      Created {new Date(project.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  <Link to="/projects/$projectId" params={{ projectId: project.id }}>
                    <Button variant="outline" size="sm">
                      Open Project
                    </Button>
                  </Link>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* New Project Dialog */}
      <NewProjectDialog open={showNewProject} onOpenChange={setShowNewProject} />
    </div>
  )
}

