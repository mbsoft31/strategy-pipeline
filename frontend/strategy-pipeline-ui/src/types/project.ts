/**
 * Type Definitions for Strategy Pipeline
 * Mirrors backend Pydantic models and API specifications
 */

export type ApprovalStatus = 'draft' | 'approved' | 'rejected' | 'approved_with_notes' | 'requires_revision';
export type ProjectStatus = 'draft' | 'in_progress' | 'completed';
export type StageStatus = 'not_started' | 'draft' | 'approved' | 'requires_revision';

export interface Project {
  id: string;
  title: string;
  description?: string;
  status: ProjectStatus;
  created_at: string;
  updated_at?: string;
  current_stage?: number;
  total_stages?: number;
  artifacts?: Record<string, ApprovalStatus>;
}

export interface Stage {
  id: string;
  name: string;
  number: number;
  status: StageStatus;
  description?: string;
  artifact?: unknown;
  extra_artifacts?: Record<string, unknown>;
}

export interface ModelMetadata {
  model_name: string;
  mode: 'llm' | 'mock' | 'manual';
  prompt_version?: string;
  generated_at: string;
  notes?: string;
}

export interface ProjectContext {
  id: string;
  title: string;
  raw_idea?: string;
  short_description?: string;
  background_summary?: string;
  discipline?: string;
  subfield?: string;
  application_area?: string;
  constraints?: Record<string, string>;
  initial_keywords?: string[];
  research_domain?: string;
  expected_outcomes?: string[];
  status: ApprovalStatus;
  created_at: string;
  updated_at?: string;
  model_metadata?: ModelMetadata;
  user_notes?: string;
}

export interface ProblemFraming {
  project_id: string;
  problem_statement: string;
  goals: string[];
  scope_in?: string[];
  scope_out?: string[];
  pico_elements?: {
    population?: string;
    intervention?: string;
    comparison?: string;
    outcome?: string;
  };
  stakeholders?: string[];
  research_gap?: string;
  critique_report?: string;
  scope_boundaries?: string[];
  status: ApprovalStatus;
  created_at: string;
  updated_at?: string;
  model_metadata?: ModelMetadata;
  user_notes?: string;
}

export interface Concept {
  id: string;
  label: string;
  description: string;
  type: 'intervention' | 'outcome' | 'method' | 'population' | 'other';
  name?: string;
  synonyms?: string[];
  broader_terms?: string[];
  narrower_terms?: string[];
  related_terms?: string[];
}

export interface ConceptRelation {
  id: string;
  source_concept_id: string;
  target_concept_id: string;
  relation_type: string;
  concept_a?: string;
  concept_b?: string;
  relationship_type?: string;
}

export interface ConceptModel {
  project_id: string;
  concepts: Concept[];
  relations?: ConceptRelation[];
  relationships?: ConceptRelation[];
  core_concepts?: Concept[];
  status: ApprovalStatus;
  created_at: string;
  updated_at?: string;
  model_metadata?: ModelMetadata;
  user_notes?: string;
}

export interface ResearchQuestion {
  id: string;
  question_text: string;
  question_type: 'primary' | 'secondary';
  rationale: string;
}

export interface ResearchQuestionSet {
  project_id: string;
  primary_questions: ResearchQuestion[];
  secondary_questions: ResearchQuestion[];
  status: ApprovalStatus;
  created_at: string;
  updated_at?: string;
  model_metadata?: ModelMetadata;
  user_notes?: string;
}

export interface SearchConceptBlock {
  id: string;
  concept_name: string;
  core_term: string;
  search_terms: string[];
  synonyms: string[];
  variations?: string[];
}

export interface SearchConceptBlocks {
  project_id: string;
  blocks: SearchConceptBlock[];
  status: ApprovalStatus;
  created_at: string;
  updated_at?: string;
  model_metadata?: ModelMetadata;
  user_notes?: string;
}

export interface DatabaseQuery {
  database: string;
  query_string: string;
  syntax_validated: boolean;
  estimated_hits?: number;
}

export interface DatabaseQueryPlan {
  project_id: string;
  target_databases: string[];
  queries: DatabaseQuery[];
  query_complexity?: string;
  validation_report?: string;
  status: ApprovalStatus;
  created_at: string;
  updated_at?: string;
  model_metadata?: ModelMetadata;
  user_notes?: string;
}

export interface StageResult {
  stage_name: string;
  project_id?: string;
  draft_artifact: unknown;
  metadata?: ModelMetadata;
  prompts?: string[];
  validation_errors?: string[];
  critique_report?: string;
  extra_data?: Record<string, unknown>;
}

export interface ApiError {
  error: string;
  code?: string;
  details?: unknown;
}

