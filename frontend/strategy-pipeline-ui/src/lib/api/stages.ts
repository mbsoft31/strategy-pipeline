/**
 * Stages API module
 *
 * Handles pipeline stage execution and approval:
 * - Run stage
 * - Approve stage artifact
 * - Get stage status
 *
 */

import { apiClient } from './client';
import type {
  StageRunRequest,
  StageRunResponse,
  StageApprovalRequest,
  StageApprovalResponse,
  StageResult,
} from './types';

export const stagesApi = {
  /**
   * Execute a pipeline stage
   * POST /api/projects/:projectId/stages/:stageName/run
   */
  run: async (
    projectId: string,
    stageName: string,
    inputs?: Record<string, unknown>
  ): Promise<StageResult> => {
    const request: StageRunRequest = { inputs };
    const response = await apiClient.post<StageRunResponse>(
      `/api/projects/${projectId}/stages/${stageName}/run`,
      request
    );
    return response.result;
  },

  /**
   * Approve a stage artifact
   * POST /api/projects/:projectId/stages/:stageName/approve
   */
  approve: async (
    projectId: string,
    stageName: string,
    edits: Record<string, unknown>,
    notes?: string
  ): Promise<StageApprovalResponse> => {
    const request: StageApprovalRequest = { edits, notes };
    return apiClient.post<StageApprovalResponse>(
      `/api/projects/${projectId}/stages/${stageName}/approve`,
      request
    );
  },

  /**
   * Get available stages for a project
   * GET /api/projects/:projectId/stages
   */
  available: async (projectId: string): Promise<string[]> => {
    const response = await apiClient.get<{ stages: string[] }>(
      `/api/projects/${projectId}/stages`
    );
    return response.stages;
  },
};

