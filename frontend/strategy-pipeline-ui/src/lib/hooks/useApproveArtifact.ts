/**
 * useApproveArtifact mutation hook
 *
 * Handles artifact approval with automatic cache invalidation
 *
 * @param projectId - The ID of the project
 *
 * @example
 * const approveArtifact = useApproveArtifact(projectId);
 *
 * const handleApprove = async (edits) => {
 *   try {
 *     await approveArtifact.mutateAsync({
 *       stageName: 'problem-framing',
 *       edits: edits,
 *       notes: 'Looks good!'
 *     });
 *     toast.success('Artifact approved!');
 *   } catch (error) {
 *     toast.error('Failed to approve artifact');
 *   }
 * };
 *
 */

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { stagesApi } from '../api/stages';
import type { StageApprovalResponse } from '../api/types';
import { stageToArtifacts } from './utils';

interface ApproveArtifactRequest {
  stageName: string;
  edits: Record<string, unknown>;
  notes?: string;
}

export const useApproveArtifact = (projectId: string | undefined) => {
  const queryClient = useQueryClient();

  return useMutation<StageApprovalResponse, Error, ApproveArtifactRequest>({
    mutationFn: ({ stageName, edits, notes }) => {
      if (!projectId) {
        throw new Error('Project ID is required');
      }
      return stagesApi.approve(projectId, stageName, edits, notes);
    },
    onSuccess: (_data, variables) => {
      if (!projectId) return;

      // Invalidate project cache (approval may enable next stages)
      queryClient.invalidateQueries({ queryKey: ['project', projectId] });

      // Invalidate artifact caches
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

