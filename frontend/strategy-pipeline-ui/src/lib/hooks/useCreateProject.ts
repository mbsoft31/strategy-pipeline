/**
 * useCreateProject mutation hook
 *
 * Handles project creation with automatic cache invalidation
 *
 * @example
 * const createProject = useCreateProject();
 *
 * const handleSubmit = async (data) => {
 *   try {
 *     const result = await createProject.mutateAsync({
 *       raw_idea: data.idea,
 *       title: data.title
 *     });
 *     navigate(`/projects/${result.project_id}`);
 *   } catch (error) {
 *     toast.error('Failed to create project');
 *   }
 * };
 *
 */

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { projectsApi, type CreateProjectRequest, type CreateProjectResponse } from '../api/projects';

export const useCreateProject = () => {
  const queryClient = useQueryClient();

  return useMutation<CreateProjectResponse, Error, CreateProjectRequest>({
    mutationFn: projectsApi.create,
    onSuccess: () => {
      // Invalidate projects list to trigger refetch
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });
};

