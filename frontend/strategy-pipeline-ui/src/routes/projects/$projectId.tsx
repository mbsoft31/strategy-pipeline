import { createFileRoute } from '@tanstack/react-router'
import ProjectDetail from '@/components/ProjectDetail'

export const Route = createFileRoute('/projects/$projectId')({
  component: ProjectDetail,
})

