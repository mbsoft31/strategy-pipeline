/**
 * Artifacts API module
 *
 * Handles artifact retrieval and management:
 * - Get specific artifact
 * - List project artifacts
 *
 */

import { apiClient } from './client';
import type {
  ArtifactResponse,
  BaseArtifact,
  ProjectContext,
  ProblemFraming,
  ConceptModel,
  ResearchQuestionSet,
  SearchConceptBlocks,
  DatabaseQueryPlan,
  ScreeningCriteria,
  SearchResults,
  StrategyExportBundle,
} from './types';

// Union type of all possible artifacts
export type AnyArtifact =
  | ProjectContext
  | ProblemFraming
  | ConceptModel
  | ResearchQuestionSet
  | SearchConceptBlocks
  | DatabaseQueryPlan
  | ScreeningCriteria
  | SearchResults
  | StrategyExportBundle;

export const artifactsApi = {
  /**
   * Get specific artifact by type
   * GET /api/projects/:projectId/artifacts/:artifactType
   */
  get: async <T extends BaseArtifact = AnyArtifact>(
    projectId: string,
    artifactType: string
  ): Promise<T> => {
    const response = await apiClient.get<ArtifactResponse<T>>(
      `/api/projects/${projectId}/artifacts/${artifactType}`
    );
    return response.artifact;
  },

  /**
   * List all artifacts for a project
   * GET /api/projects/:projectId/artifacts
   */
  list: async (projectId: string): Promise<Record<string, BaseArtifact>> => {
    const response = await apiClient.get<{ artifacts: Record<string, BaseArtifact> }>(
      `/api/projects/${projectId}/artifacts`
    );
    return response.artifacts;
  },
};