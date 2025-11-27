/**
 * useArtifact hook
 *
 * Fetches and caches a specific artifact for a project
 *
 * @param projectId - The ID of the project
 * @param artifactType - The type of artifact to fetch (e.g., 'ProjectContext', 'ProblemFraming')
 *
 * @example
 * const { data: artifact, isLoading } = useArtifact(projectId, 'ProblemFraming');
 *
 */

import { useQuery } from '@tanstack/react-query';
import { artifactsApi, type AnyArtifact } from '../api/artifacts';
import type { BaseArtifact } from '../api/types';

export const useArtifact = <T extends BaseArtifact = AnyArtifact>(
  projectId: string | undefined,
  artifactType: string | undefined
) => {
  return useQuery<T, Error>({
    queryKey: ['artifact', projectId, artifactType],
    queryFn: () => artifactsApi.get<T>(projectId!, artifactType!),
    enabled: !!projectId && !!artifactType,
    staleTime: 10000,
    gcTime: 5 * 60 * 1000,
  });
};

