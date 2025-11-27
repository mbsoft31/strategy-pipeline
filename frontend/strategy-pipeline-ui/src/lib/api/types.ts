/**
 * TypeScript interfaces for API responses
 *
 */

// Common types
export interface ModelMetadata {
  model_name: string;
  mode: string;
  prompt_version?: string;
  generated_at: string;
  notes?: string;
}

export type ApprovalStatus = 'DRAFT' | 'UNDER_REVIEW' | 'APPROVED' | 'APPROVED_WITH_NOTES' | 'REQUIRES_REVISION';

// Project types
export interface ProjectSummary {
  id: string;
  title: string;
  short_description: string;
  created_at: string;
  updated_at: string;
  status: ApprovalStatus;
  current_stage?: string;
  discipline?: string;
}

export interface ProjectDetail extends ProjectSummary {
  subfield?: string;
  application_area?: string;
  constraints: Record<string, unknown>;
  initial_keywords: string[];
  artifacts: Record<string, ArtifactSummary>;
  available_stages: string[];
}

export interface ArtifactSummary {
  type: string;
  status: ApprovalStatus;
  generated_at: string;
  approved_at?: string;
}

// Stage execution types
export interface StageResult {
  stage_name: string;
  draft_artifact: unknown;
  metadata: ModelMetadata;
  prompts: string[];
  validation_errors: string[];
}

export interface StageRunRequest {
  inputs?: Record<string, unknown>;
}

export interface StageApprovalRequest {
  edits: Record<string, unknown>;
  notes?: string;
}

// Artifact types
export interface BaseArtifact {
  __class__: string;
  status?: ApprovalStatus;
  model_metadata?: ModelMetadata;
}

export interface ProjectContext extends BaseArtifact {
  id: string;
  title: string;
  short_description: string;
  discipline?: string;
  subfield?: string;
  application_area?: string;
  constraints: Record<string, unknown>;
  initial_keywords: string[];
  created_at: string;
  updated_at: string;
}

export interface Concept {
  id: string;
  label: string;
  type: string;
  description?: string;
  synonyms?: string[];
}

export interface ProblemFraming extends BaseArtifact {
  project_id: string;
  problem_statement: string;
  goals: string[];
  scope_in: string[];
  scope_out: string[];
  feasibility_notes?: string;
  risks?: string[];
}

export interface ConceptModel extends BaseArtifact {
  project_id: string;
  concepts: Concept[];
}

export interface ResearchQuestion {
  id: string;
  text: string;
  priority: 'must_have' | 'should_have' | 'nice_to_have';
  rationale?: string;
  linked_concepts?: string[];
}

export interface ResearchQuestionSet extends BaseArtifact {
  project_id: string;
  questions: ResearchQuestion[];
}

export interface SearchConceptBlock {
  id: string;
  label: string;
  terms_included: string[];
  terms_excluded?: string[];
  description?: string;
}

export interface SearchConceptBlocks extends BaseArtifact {
  project_id: string;
  blocks: SearchConceptBlock[];
}

export interface DatabaseQuery {
  id: string;
  database_name: string;
  boolean_query_string: string;
  query_blocks: string[];
  notes?: string;
  hit_count_estimate?: number;
  complexity_analysis?: Record<string, unknown>;
}

export interface DatabaseQueryPlan extends BaseArtifact {
  project_id: string;
  queries: DatabaseQuery[];
}

export interface ScreeningCriteria extends BaseArtifact {
  project_id: string;
  inclusion_criteria: string[];
  exclusion_criteria: string[];
}

export interface SearchResults extends BaseArtifact {
  project_id: string;
  total_results: number;
  deduplicated_count: number;
  databases_searched: string[];
  result_file_paths: string[];
  deduplication_stats: Record<string, unknown>;
  execution_time_seconds: number;
}

export interface StrategyExportBundle extends BaseArtifact {
  project_id: string;
  exported_files: string[];
  export_formats: string[];
  export_timestamp: string;
}

// API Response types
export interface ProjectListResponse {
  projects: ProjectSummary[];
}

export interface ProjectDetailResponse {
  project: ProjectDetail;
}

export interface ArtifactResponse<T extends BaseArtifact = BaseArtifact> {
  artifact: T;
}

export interface StageRunResponse {
  result: StageResult;
}

export interface StageApprovalResponse {
  success: boolean;
  message: string;
}

// Helper type for stage name to artifact type mapping
export type StageArtifactMap = {
  'project-setup': 'ProjectContext';
  'problem-framing': 'ProblemFraming' | 'ConceptModel';
  'research-questions': 'ResearchQuestionSet';
  'search-concept-expansion': 'SearchConceptBlocks';
  'database-query-plan': 'DatabaseQueryPlan';
  'screening-criteria': 'ScreeningCriteria';
  'query-execution': 'SearchResults';
  'strategy-export': 'StrategyExportBundle';
};

