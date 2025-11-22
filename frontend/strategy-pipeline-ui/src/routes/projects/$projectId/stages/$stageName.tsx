import { createFileRoute } from '@tanstack/react-router'
import StageView from '@/components/StageView'

export const Route = createFileRoute('/projects/$projectId/stages/$stageName')({
  component: StageView,
})

