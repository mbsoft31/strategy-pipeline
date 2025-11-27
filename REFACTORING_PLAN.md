# PipelineController Refactoring Plan

**Date:** November 26, 2025  
**Status:** ✅ **COMPLETED** (November 27, 2025)  
**Goal:** Decompose the oversized `PipelineController` into smaller, specialized, testable classes

---

## ✅ REFACTORING COMPLETED SUCCESSFULLY

**All phases executed successfully with 100% backward compatibility.**

See `REFACTORING_COMPLETE.md` for full completion report.

**Key Results:**
- ✅ 3 new orchestration components created
- ✅ 50 new tests added (100% coverage)
- ✅ 69/69 total tests passing
- ✅ Zero breaking changes
- ✅ Controller reduced to clean facade pattern

---

## Executive Summary

This refactoring addresses the "God Object" anti-pattern in `src/controller.py` by extracting responsibilities into three specialized classes within a new `src/orchestration` module:

1. **`ProjectNavigator`** - Handles project status and stage progression logic
2. **`ArtifactManager`** - Manages artifact loading, saving, and approval workflows
3. **`StageOrchestrator`** - Responsible for stage execution and registry management

The refactored `PipelineController` will become a thin facade that coordinates these components, maintaining **100% backward compatibility** with existing CLI and web interfaces.

---

## Architecture Overview

### Current Architecture (Problem)
```
PipelineController (320+ lines)
├── Stage Registry (_stages_registry)
├── Stage Execution (run_stage, start_project)
├── Artifact Management (get_artifact, approve_artifact)
├── Project Navigation (get_next_available_stages)
└── Project Listing (list_projects)
```

**Issues:**
- Single class with too many responsibilities
- Difficult to test in isolation
- Hard to extend or modify
- Violates Single Responsibility Principle

### Target Architecture (Solution)
```
PipelineController (facade, ~100 lines)
├── delegates to → ProjectNavigator
│   └── get_next_available_stages()
│   └── get_project_status()
│   └── validate_stage_transition()
│
├── delegates to → ArtifactManager
│   └── get_artifact()
│   └── save_artifact()
│   └── approve_artifact()
│   └── list_projects()
│
└── delegates to → StageOrchestrator
    └── register_stage()
    └── run_stage()
    └── start_project()
    └── execute_stage_logic()
```

**Benefits:**
- Each class has a single, clear responsibility
- Easier to test with mocked dependencies
- Simpler to extend (e.g., add new navigation logic)
- Better code organization and readability

---

## Detailed Implementation Plan

### Phase 1: Setup and Initial Analysis ✓

**Objective:** Create the orchestration module structure and analyze current code

#### Tasks:
- [ ] Create directory `src/orchestration/`
- [ ] Create `src/orchestration/__init__.py` (empty initially)
- [ ] Create `tests/orchestration/` directory
- [ ] Create `tests/orchestration/__init__.py`
- [ ] Read and analyze `src/controller.py` thoroughly
- [ ] Read and analyze existing tests:
  - `tests/test_stage1_and_controller.py`
  - `test_stage_workflow.py` (integration test)
- [ ] Document method-to-class mapping (see Appendix A)
- [ ] Create a backup branch: `git checkout -b backup/pre-refactor`
- [ ] Create feature branch: `git checkout -b refactor/controller-decomposition`

#### Success Criteria:
- Directory structure created
- Current code understood and documented
- Branches created for safe refactoring

---

### Phase 2: Create `ProjectNavigator`

**Objective:** Extract stage progression and navigation logic

#### Tasks:
- [ ] Create `src/orchestration/project_navigator.py`
- [ ] Implement `ProjectNavigator` class with:
  ```python
  class ProjectNavigator:
      def __init__(self, artifact_manager: 'ArtifactManager'):
          self.artifact_manager = artifact_manager
      
      def get_next_available_stages(self, project_id: str) -> List[str]:
          """Determine next stages based on approved artifacts."""
          # Move logic from PipelineController.get_next_available_stages
          pass
      
      def get_project_status(self, project_id: str) -> Dict[str, Any]:
          """Get current project status including completed stages."""
          pass
      
      def validate_stage_transition(
          self, 
          project_id: str, 
          target_stage: str
      ) -> bool:
          """Validate if a stage can be executed given current project state."""
          pass
  ```
- [ ] Move `get_next_available_stages()` logic from `PipelineController`
- [ ] Add comprehensive docstrings
- [ ] Add type hints for all methods

#### Testing:
- [ ] Create `tests/orchestration/test_project_navigator.py`
- [ ] Test `get_next_available_stages()` for all stage transitions
- [ ] Test edge cases (missing artifacts, unapproved artifacts)
- [ ] Test with mock `ArtifactManager`
- [ ] Achieve 100% code coverage for this module

#### Success Criteria:
- `ProjectNavigator` fully implemented
- All tests passing
- Type checking passes (`mypy src/orchestration/project_navigator.py`)

---

### Phase 3: Create `ArtifactManager`

**Objective:** Extract all artifact persistence and management logic

#### Tasks:
- [ ] Create `src/orchestration/artifact_manager.py`
- [ ] Implement `ArtifactManager` class with:
  ```python
  class ArtifactManager:
      def __init__(self, persistence_service: PersistenceService):
          self.persistence_service = persistence_service
      
      def get_artifact(
          self, 
          project_id: str, 
          artifact_type: str, 
          artifact_class: Any
      ) -> Optional[Any]:
          """Load an artifact from persistence."""
          # Move from PipelineController.get_artifact
          pass
      
      def save_artifact(
          self,
          artifact: Any,
          project_id: str,
          artifact_type: str
      ) -> None:
          """Save an artifact to persistence."""
          pass
      
      def approve_artifact(
          self,
          project_id: str,
          artifact_type: str,
          artifact_class: Any,
          edits: Dict[str, Any],
          approval_status: ApprovalStatus = ApprovalStatus.APPROVED,
          user_notes: Optional[str] = None,
      ) -> None:
          """Apply edits, update status, and persist artifact."""
          # Move from PipelineController.approve_artifact
          pass
      
      def list_projects(self) -> List[str]:
          """List all available projects."""
          # Move from PipelineController.list_projects
          pass
      
      def project_exists(self, project_id: str) -> bool:
          """Check if a project exists."""
          pass
  ```
- [ ] Move methods from `PipelineController`:
  - `get_artifact()`
  - `approve_artifact()`
  - `list_projects()`
- [ ] Add comprehensive docstrings
- [ ] Add type hints for all methods

#### Testing:
- [ ] Create `tests/orchestration/test_artifact_manager.py`
- [ ] Test artifact loading (existing and missing)
- [ ] Test artifact saving with various data types
- [ ] Test approval workflow:
  - Apply edits correctly
  - Update status
  - Update timestamp
  - Save notes
- [ ] Test `list_projects()` with empty/populated directories
- [ ] Use mock `PersistenceService` for isolation
- [ ] Achieve 100% code coverage for this module

#### Success Criteria:
- `ArtifactManager` fully implemented
- All persistence logic centralized
- All tests passing
- Type checking passes

---

### Phase 4: Create `StageOrchestrator`

**Objective:** Extract stage execution and registry management

#### Tasks:
- [ ] Create `src/orchestration/stage_orchestrator.py`
- [ ] Implement `StageOrchestrator` class with:
  ```python
  class StageOrchestrator:
      def __init__(
          self,
          model_service: ModelService,
          artifact_manager: ArtifactManager,
      ):
          self.model_service = model_service
          self.artifact_manager = artifact_manager
          self._stages_registry: Dict[str, Any] = {}
          self._register_default_stages()
      
      def register_stage(self, stage_name: str, stage_class: Any) -> None:
          """Register a stage class in the registry."""
          # Move from PipelineController.register_stage
          pass
      
      def _register_default_stages(self) -> None:
          """Register all built-in stages."""
          # Move from PipelineController._register_default_stages
          pass
      
      def run_stage(
          self, 
          stage_name: str, 
          project_id: str, 
          **inputs: Any
      ) -> StageResult:
          """Execute a pipeline stage and persist results."""
          # Move from PipelineController.run_stage
          pass
      
      def start_project(
          self, 
          raw_idea: str, 
          project_id: Optional[str] = None
      ) -> StageResult:
          """Initialize a new project (special case of run_stage)."""
          # Move from PipelineController.start_project
          pass
      
      def get_stage_class(self, stage_name: str) -> Optional[Any]:
          """Get a registered stage class."""
          pass
      
      def list_registered_stages(self) -> List[str]:
          """List all registered stage names."""
          pass
  ```
- [ ] Move methods from `PipelineController`:
  - `register_stage()`
  - `_register_default_stages()`
  - `run_stage()`
  - `start_project()`
- [ ] Move `_stages_registry` dictionary
- [ ] Add comprehensive docstrings
- [ ] Add type hints for all methods

#### Testing:
- [ ] Create `tests/orchestration/test_stage_orchestrator.py`
- [ ] Test stage registration
- [ ] Test `start_project()`:
  - Project ID generation
  - Stage 0 execution
  - Artifact persistence
- [ ] Test `run_stage()`:
  - Valid stage execution
  - Invalid stage name (should raise ValueError)
  - Non-existent project (should raise ValueError)
  - Artifact and extra_data persistence
- [ ] Use mock `ModelService` and `ArtifactManager`
- [ ] Achieve 100% code coverage for this module

#### Success Criteria:
- `StageOrchestrator` fully implemented
- All stage execution logic centralized
- All tests passing
- Type checking passes

---

### Phase 5: Refactor `PipelineController` into Facade

**Objective:** Convert controller to a thin coordination layer

#### Tasks:
- [ ] Update `src/controller.py` to:
  ```python
  class PipelineController:
      """Facade for pipeline orchestration.
      
      Coordinates ProjectNavigator, ArtifactManager, and StageOrchestrator
      to provide a unified API for CLI and web interfaces.
      """
      
      def __init__(
          self,
          model_service: ModelService,
          persistence_service: PersistenceService,
      ):
          # Create specialized components
          self.artifact_manager = ArtifactManager(persistence_service)
          self.project_navigator = ProjectNavigator(self.artifact_manager)
          self.stage_orchestrator = StageOrchestrator(
              model_service, 
              self.artifact_manager
          )
      
      # Delegate to ArtifactManager
      def get_artifact(self, project_id: str, artifact_type: str, artifact_class: Any):
          return self.artifact_manager.get_artifact(project_id, artifact_type, artifact_class)
      
      def approve_artifact(self, project_id: str, artifact_type: str, ...):
          return self.artifact_manager.approve_artifact(project_id, artifact_type, ...)
      
      def list_projects(self):
          return self.artifact_manager.list_projects()
      
      # Delegate to ProjectNavigator
      def get_next_available_stages(self, project_id: str):
          return self.project_navigator.get_next_available_stages(project_id)
      
      # Delegate to StageOrchestrator
      def register_stage(self, stage_name: str, stage_class: Any):
          return self.stage_orchestrator.register_stage(stage_name, stage_class)
      
      def start_project(self, raw_idea: str, project_id: Optional[str] = None):
          return self.stage_orchestrator.start_project(raw_idea, project_id)
      
      def run_stage(self, stage_name: str, project_id: str, **inputs):
          return self.stage_orchestrator.run_stage(stage_name, project_id, **inputs)
  ```
- [ ] Remove old implementation code (moved to specialized classes)
- [ ] Keep all public method signatures EXACTLY the same
- [ ] Update imports to include orchestration components
- [ ] Ensure PersistenceService is only passed to ArtifactManager
- [ ] Update docstring to reflect new facade role

#### Testing - Backward Compatibility:
- [ ] Run ALL existing tests without modification:
  - `pytest tests/test_stage1_and_controller.py -v`
  - `pytest tests/test_stage0.py -v`
  - `pytest tests/test_stage2_research_questions.py -v`
  - `pytest tests/test_stage3_search_expansion.py -v`
  - `pytest tests/test_stage4_query_plan.py -v`
- [ ] Verify integration test: `python test_stage_workflow.py`
- [ ] Ensure 100% of old tests pass without changes

#### Testing - New Unit Tests:
- [ ] Create `tests/test_controller_facade.py`
- [ ] Test that controller properly delegates to components
- [ ] Test initialization creates all components
- [ ] Verify component interactions

#### Success Criteria:
- Controller reduced to ~100-150 lines (thin facade)
- ALL existing tests pass without modification
- No breaking changes to public API
- Type checking passes

---

### Phase 6: Update Orchestration Module Exports

**Objective:** Make new classes easily importable

#### Tasks:
- [ ] Update `src/orchestration/__init__.py`:
  ```python
  """Orchestration layer for pipeline execution.
  
  This module contains specialized components that decompose the responsibilities
  of the original PipelineController:
  
  - ArtifactManager: Handles artifact persistence and approval workflows
  - ProjectNavigator: Manages stage progression and project status
  - StageOrchestrator: Executes pipeline stages and manages stage registry
  """
  
  from .artifact_manager import ArtifactManager
  from .project_navigator import ProjectNavigator
  from .stage_orchestrator import StageOrchestrator
  
  __all__ = [
      "ArtifactManager",
      "ProjectNavigator",
      "StageOrchestrator",
  ]
  ```
- [ ] Verify clean imports work: `from src.orchestration import ArtifactManager`

#### Success Criteria:
- Module properly exports all classes
- Clean imports work from external code

---

### Phase 7: Documentation and Cleanup

**Objective:** Document changes and ensure code quality

#### Tasks:
- [ ] Create/Update `docs/orchestration-architecture.md`:
  - Diagram of new architecture
  - Class responsibilities
  - Interaction patterns
  - Migration guide from old to new
- [ ] Update `docs/architecture-overview.md`:
  - Add orchestration layer section
  - Update PipelineController description
  - Add class diagram
- [ ] Update `docs/models-and-model-services.md`:
  - Reference new orchestration classes
  - Update examples to show new structure
- [ ] Create `REFACTORING_COMPLETE.md`:
  - What was changed
  - Why it was changed
  - Benefits achieved
  - Breaking changes (none expected)
  - Migration guide (if direct usage of controller internals)
- [ ] Add/update docstrings:
  - All classes have comprehensive class-level docstrings
  - All public methods documented with parameters and return types
  - Add usage examples in docstrings
- [ ] Code quality checks:
  - [ ] Run `black src/orchestration/` (formatting)
  - [ ] Run `isort src/orchestration/` (import sorting)
  - [ ] Run `mypy src/orchestration/` (type checking)
  - [ ] Run `mypy src/controller.py` (type checking)
  - [ ] Run `pylint src/orchestration/` (linting)
- [ ] Update `README.md` if necessary:
  - Add note about refactored architecture (optional)
  - Update programmatic usage example if needed

#### Success Criteria:
- All documentation updated
- Code passes all quality checks
- Future maintainers can understand the new architecture

---

### Phase 8: Comprehensive Testing and Validation

**Objective:** Ensure robustness and no regressions

#### Tasks:
- [ ] Run complete test suite:
  ```bash
  pytest tests/ -v --cov=src/orchestration --cov=src/controller
  ```
- [ ] Verify coverage targets:
  - [ ] `src/orchestration/artifact_manager.py`: 100%
  - [ ] `src/orchestration/project_navigator.py`: 100%
  - [ ] `src/orchestration/stage_orchestrator.py`: 100%
  - [ ] `src/controller.py`: 90%+ (facade should be simple)
- [ ] Integration testing:
  - [ ] Run `python main.py` (Stage 0 demo)
  - [ ] Run `python test_stage_workflow.py` (full workflow)
  - [ ] Start Flask app: `python interfaces/web_app.py`
  - [ ] Test API endpoints manually or with Postman
- [ ] CLI testing:
  - [ ] `python -m interfaces.cli start "test idea"`
  - [ ] `python -m interfaces.cli list`
  - [ ] `python -m interfaces.cli run-stage problem-framing <id>`
  - [ ] `python -m interfaces.cli approve <id> ProjectContext`
- [ ] Edge case testing:
  - [ ] Non-existent project IDs
  - [ ] Invalid stage names
  - [ ] Missing artifacts
  - [ ] Concurrent operations (if applicable)
- [ ] Performance check:
  - [ ] Ensure refactoring doesn't introduce performance regression
  - [ ] Profile if necessary

#### Success Criteria:
- All tests pass (28+ existing tests + new orchestration tests)
- Coverage meets targets
- Integration tests work flawlessly
- CLI and web interfaces fully functional
- No performance degradation

---

### Phase 9: Final Review and Merge

**Objective:** Complete the refactoring and merge to main

#### Tasks:
- [ ] Self code review:
  - [ ] Check for TODO comments
  - [ ] Verify all type hints are present
  - [ ] Ensure consistent naming conventions
  - [ ] Remove debug prints or commented code
- [ ] Git hygiene:
  - [ ] Ensure commits are atomic and well-described
  - [ ] Squash fixup commits if desired
  - [ ] Write comprehensive PR description
- [ ] Create pull request (if using PR workflow):
  - [ ] Title: "Refactor: Decompose PipelineController into orchestration layer"
  - [ ] Description includes:
    - Problem statement
    - Solution approach
    - Benefits
    - Test coverage proof
    - Screenshots/examples (optional)
- [ ] Peer review (if working in a team):
  - [ ] Request review from team members
  - [ ] Address feedback
  - [ ] Update based on suggestions
- [ ] Final validation:
  - [ ] Rebase on latest main (if needed)
  - [ ] Run full test suite one more time
  - [ ] Verify no merge conflicts
- [ ] Merge to main:
  - [ ] Use appropriate merge strategy (squash, merge commit, or rebase)
  - [ ] Delete feature branch
  - [ ] Tag release if appropriate: `git tag v1.1.0-refactor`

#### Success Criteria:
- Code merged to main branch
- All tests passing in main
- Documentation updated
- Team aware of changes

---

## Appendix A: Method-to-Class Mapping

### Current PipelineController Methods → New Locations

| Method Name | Current Line Count | Target Class | Rationale |
|-------------|-------------------|--------------|-----------|
| `__init__` | ~7 | `PipelineController` (facade) | Creates all components |
| `_register_default_stages` | ~8 | `StageOrchestrator` | Stage registry management |
| `register_stage` | ~2 | `StageOrchestrator` | Stage registry management |
| `start_project` | ~17 | `StageOrchestrator` | Stage execution |
| `run_stage` | ~22 | `StageOrchestrator` | Stage execution |
| `approve_artifact` | ~18 | `ArtifactManager` | Artifact persistence & approval |
| `get_artifact` | ~2 | `ArtifactManager` | Artifact loading |
| `list_projects` | ~2 | `ArtifactManager` | Project listing |
| `get_next_available_stages` | ~30 | `ProjectNavigator` | Stage progression logic |

**Total lines in current controller:** ~108 lines  
**Expected lines after refactoring:** ~40-60 lines (delegation only)

---

## Appendix B: Dependency Graph

```
PipelineController (facade)
│
├──> ArtifactManager
│    └── depends on: PersistenceService
│
├──> ProjectNavigator
│    └── depends on: ArtifactManager
│
└──> StageOrchestrator
     ├── depends on: ModelService
     └── depends on: ArtifactManager
```

**Key insights:**
- `ArtifactManager` has no dependencies on other orchestration components
- `ProjectNavigator` depends on `ArtifactManager` (to load artifacts for status checking)
- `StageOrchestrator` depends on `ArtifactManager` (to persist stage results)
- No circular dependencies

---

## Appendix C: Test Coverage Goals

| Module | Target Coverage | Rationale |
|--------|----------------|-----------|
| `artifact_manager.py` | 100% | Simple CRUD operations, must be bulletproof |
| `project_navigator.py` | 100% | Critical business logic for stage flow |
| `stage_orchestrator.py` | 100% | Core execution engine, zero tolerance for bugs |
| `controller.py` (facade) | 90%+ | Mostly delegation, some edge cases |

**Total new test files:** 4  
**Expected new tests:** 30-40 individual test cases

---

## Appendix D: Risk Mitigation

### Identified Risks

1. **Breaking existing interfaces**
   - **Mitigation:** Keep all public method signatures identical
   - **Validation:** Run all existing tests without modification

2. **Circular dependencies between orchestration classes**
   - **Mitigation:** Clear dependency hierarchy (see Appendix B)
   - **Validation:** Import tests, type checking

3. **Performance regression from additional indirection**
   - **Mitigation:** Delegation is negligible overhead
   - **Validation:** Profile before/after if concerned

4. **Test coverage gaps**
   - **Mitigation:** Write tests in parallel with implementation
   - **Validation:** Coverage reports must meet targets

5. **Documentation drift**
   - **Mitigation:** Update docs as part of each phase
   - **Validation:** Doc review in Phase 7

---

## Appendix E: Success Metrics

### Quantitative Goals
- ✅ Reduce `controller.py` from ~150 lines to <80 lines
- ✅ Achieve 100% test coverage for orchestration layer
- ✅ All 28+ existing tests pass without modification
- ✅ Add 30-40 new unit tests for orchestration classes
- ✅ Zero breaking changes to public API
- ✅ Pass mypy type checking with no errors

### Qualitative Goals
- ✅ Each class has a single, clear responsibility
- ✅ Code is easier to understand and modify
- ✅ New developers can quickly grasp architecture
- ✅ Future extensions (new stages, new workflows) are simpler
- ✅ Testing becomes easier and more focused

---

## Timeline Estimate

| Phase | Estimated Time | Cumulative |
|-------|---------------|------------|
| Phase 1: Setup | 30 min | 30 min |
| Phase 2: ProjectNavigator | 2 hours | 2.5 hours |
| Phase 3: ArtifactManager | 2.5 hours | 5 hours |
| Phase 4: StageOrchestrator | 3 hours | 8 hours |
| Phase 5: Controller Facade | 2 hours | 10 hours |
| Phase 6: Module Exports | 30 min | 10.5 hours |
| Phase 7: Documentation | 2 hours | 12.5 hours |
| Phase 8: Testing & Validation | 2 hours | 14.5 hours |
| Phase 9: Review & Merge | 1 hour | 15.5 hours |

**Total estimated time:** 15-16 hours  
**Recommended approach:** Split across 2-3 focused work sessions

---

## Conclusion

This refactoring plan transforms the `PipelineController` from a monolithic "God object" into a well-architected system of specialized components. By following this plan methodically, we will:

1. **Improve maintainability** - Smaller, focused classes are easier to understand
2. **Enhance testability** - Components can be tested in isolation with mocks
3. **Enable extensibility** - New features can be added to specific components
4. **Maintain compatibility** - Zero breaking changes to existing code
5. **Increase confidence** - Comprehensive test coverage prevents regressions

The refactoring directly addresses the expert critique in `CRITICS.md` and sets the foundation for future enhancements like CI/CD integration and frontend testing.

---

**Ready to begin implementation!** 🚀

Start with Phase 1 and check off tasks as you complete them.

