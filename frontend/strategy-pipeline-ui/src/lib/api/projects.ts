/**
 * Projects API module
 *
 */

import { apiClient } from './client';
import type {
  ProjectListResponse,
  ProjectDetailResponse,
  ProjectSummary,
  ProjectDetail,
} from './types';

export interface CreateProjectRequest {
  raw_idea: string;
  title?: string;
}

export interface CreateProjectResponse {
  project_id: string;
  message: string;
}

export const projectsApi = {
  list: async (): Promise<ProjectSummary[]> => {
    const response = await apiClient.get<ProjectListResponse>('/api/projects');
    return response.projects;
  },

  create: async (request: CreateProjectRequest): Promise<CreateProjectResponse> => {
    return apiClient.post<CreateProjectResponse>('/api/projects', request);
  },

  get: async (projectId: string): Promise<ProjectDetail> => {
    const response = await apiClient.get<ProjectDetailResponse>(`/api/projects/${projectId}`);
    return response.project;
  },

  delete: async (projectId: string): Promise<void> => {
    return apiClient.delete<void>(`/api/projects/${projectId}`);
  },
};

