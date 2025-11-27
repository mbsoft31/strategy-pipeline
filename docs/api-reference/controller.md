# PipelineController

Main entry point for the Strategy Pipeline. Use this to orchestrate all pipeline stages.

## Overview

The `PipelineController` provides a facade pattern that coordinates the `StageOrchestrator`, `ArtifactManager`, and other services to provide a unified API for CLI and web interfaces.

## Usage Example

```python
from src.controller import PipelineController
from src.services import IntelligentModelService, FilePersistenceService

# Initialize controller
controller = PipelineController(
    IntelligentModelService(),
    FilePersistenceService(base_dir="./data")
)

# Start a new project
result = controller.start_project("Systematic review of LLM hallucination mitigation")
project_id = result.draft_artifact.id

# Run stages
result = controller.run_stage("problem-framing", project_id=project_id)

# Approve artifacts
controller.approve_artifact(project_id, "ProblemFraming")
```

## Class Reference

::: src.controller.PipelineController
    options:
      show_source: true
      heading_level: 2
      show_signature_annotations: true
      separate_signature: true
      members_order: source
      show_root_heading: false
      show_category_heading: true

