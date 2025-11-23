import { CheckCircle, Circle, Lock, Loader2, ChevronRight } from 'lucide-react';
import { Link } from '@tanstack/react-router';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/utils';

interface Stage {
  id: string;
  name: string;
  number: number;
  status: 'not_started' | 'in_progress' | 'draft' | 'approved' | 'locked';
  description: string;
}

interface StageTimelineProps {
  projectId: string;
  stages: Stage[];
  currentStage: number;
}

export function StageTimeline({ projectId, stages, currentStage }: StageTimelineProps) {
  const completedStages = stages.filter(s => s.status === 'approved').length;
  const progressPercentage = (completedStages / stages.length) * 100;

  const getStatusIcon = (stage: Stage) => {
    if (stage.status === 'approved') {
      return <CheckCircle className="h-6 w-6 text-green-600" />;
    }
    if (stage.status === 'in_progress' || stage.status === 'draft') {
      return <Loader2 className="h-6 w-6 text-blue-600 animate-spin" />;
    }
    if (stage.status === 'locked') {
      return <Lock className="h-6 w-6 text-gray-400" />;
    }
    return <Circle className="h-6 w-6 text-gray-400" />;
  };

  const getStatusBadge = (stage: Stage) => {
    const variants: Record<string, 'default' | 'secondary' | 'destructive' | 'outline'> = {
      approved: 'default',
      draft: 'secondary',
      in_progress: 'secondary',
      not_started: 'outline',
      locked: 'outline',
    };

    return (
      <Badge variant={variants[stage.status] || 'outline'} className="ml-auto">
        {stage.status.replace('_', ' ')}
      </Badge>
    );
  };

  return (
    <div className="space-y-6">
      {/* Progress Overview */}
      <Card>
        <CardContent className="pt-6">
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="font-medium">Overall Progress</span>
              <span className="text-muted-foreground">
                {completedStages} of {stages.length} stages complete
              </span>
            </div>
            <Progress value={progressPercentage} className="h-2" />
          </div>
        </CardContent>
      </Card>

      {/* Stage Timeline */}
      <div className="space-y-4">
        {stages.map((stage, index) => {
          const isActive = stage.number === currentStage;
          const isAccessible = stage.status !== 'locked';

          return (
            <Card
              key={stage.id}
              className={cn(
                "transition-all",
                isActive && "border-primary shadow-md",
                !isAccessible && "opacity-60"
              )}
            >
              <CardContent className="p-4">
                <div className="flex items-start gap-4">
                  {/* Icon */}
                  <div className="flex-shrink-0">
                    {getStatusIcon(stage)}
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-semibold text-lg">
                        Stage {stage.number}: {stage.name}
                      </h3>
                      {getStatusBadge(stage)}
                    </div>
                    <p className="text-sm text-muted-foreground mb-3">
                      {stage.description}
                    </p>

                    {/* Action Buttons */}
                    {isAccessible && (
                      <div className="flex gap-2">
                        <Button
                          asChild
                          variant={isActive ? "default" : "outline"}
                          size="sm"
                        >
                          <Link
                            to="/projects/$projectId/stages/$stageName"
                            params={{ projectId, stageName: stage.id }}
                          >
                            {stage.status === 'approved' ? 'View' : 'Continue'}
                            <ChevronRight className="ml-2 h-4 w-4" />
                          </Link>
                        </Button>

                        {stage.status === 'not_started' && (
                          <Button
                            asChild
                            variant="ghost"
                            size="sm"
                          >
                            <Link
                              to="/projects/$projectId/stages/$stageName"
                              params={{ projectId, stageName: stage.id }}
                              search={{ action: 'run' }}
                            >
                              Run Stage
                            </Link>
                          </Button>
                        )}
                      </div>
                    )}
                  </div>

                  {/* Connector Line */}
                  {index < stages.length - 1 && (
                    <div className="absolute left-[2.1rem] top-14 w-0.5 h-12 bg-border -z-10" />
                  )}
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}

