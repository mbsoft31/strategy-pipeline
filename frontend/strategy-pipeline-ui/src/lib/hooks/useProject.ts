/**
 * useProject hook
 *
 * Fetches and caches a single project's details
 *
 * @param projectId - The ID of the project to fetch
 *
 * @example
 * const { data: project, isLoading, error } = useProject(projectId);
 *
 */

import { useQuery } from '@tanstack/react-query';
import { projectsApi } from '../api/projects';
import type { ProjectDetail } from '../api/types';

export const useProject = (projectId: string | undefined) => {
  return useQuery<ProjectDetail, Error>({
    queryKey: ['project', projectId],
    queryFn: () => projectsApi.get(projectId!),
    enabled: !!projectId, // Only run query if projectId is defined
    staleTime: 10000, // 10 seconds
    gcTime: 5 * 60 * 1000,
  });
};

