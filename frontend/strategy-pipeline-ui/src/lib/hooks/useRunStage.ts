/**
 * useRunStage mutation hook
 *
 * Handles stage execution with automatic cache invalidation
 *
 * @param projectId - The ID of the project
 *
 * @example
 * const runStage = useRunStage(projectId);
 *
 * const handleRunStage = async () => {
 *   try {
 *     await runStage.mutateAsync({
 *       stageName: 'problem-framing',
 *       inputs: {} // optional stage-specific inputs
 *     });
 *     toast.success('Stage executed successfully!');
 *   } catch (error) {
 *     toast.error('Failed to execute stage');
 *   }
 * };
 *
 */

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { stagesApi } from '../api/stages';
import type { StageResult } from '../api/types';
import { stageToArtifacts } from './utils';

interface RunStageRequest {
  stageName: string;
  inputs?: Record<string, unknown>;
}

export const useRunStage = (projectId: string | undefined) => {
  const queryClient = useQueryClient();

  return useMutation<StageResult, Error, RunStageRequest>({
    mutationFn: ({ stageName, inputs }) => {
      if (!projectId) {
        throw new Error('Project ID is required');
      }
      return stagesApi.run(projectId, stageName, inputs);
    },
    onSuccess: (_data, variables) => {
      if (!projectId) return;

      // Invalidate project cache to update available stages
      queryClient.invalidateQueries({ queryKey: ['project', projectId] });

      // Invalidate artifact caches for all artifacts this stage generates
      const artifactTypes = stageToArtifacts(variables.stageName);
      artifactTypes.forEach(artifactType => {
        queryClient.invalidateQueries({
          queryKey: ['artifact', projectId, artifactType],
        });
      });

      // Invalidate all artifacts list
      queryClient.invalidateQueries({
        queryKey: ['artifacts', projectId],
      });
    },
  });
};

