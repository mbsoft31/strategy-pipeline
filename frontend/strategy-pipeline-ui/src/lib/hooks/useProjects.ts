/**
 * useProjects hook
 *
 * Fetches and caches the list of all projects
 *
 * @example
 * const { data: projects, isLoading, error, refetch } = useProjects();
 *
 */

import { useQuery } from '@tanstack/react-query';
import { projectsApi } from '../api/projects';
import type { ProjectSummary } from '../api/types';

export const useProjects = () => {
  return useQuery<ProjectSummary[], Error>({
    queryKey: ['projects'],
    queryFn: projectsApi.list,
    staleTime: 30000, // 30 seconds - projects don't change often
    gcTime: 5 * 60 * 1000, // 5 minutes garbage collection
  });
};

