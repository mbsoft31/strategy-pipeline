#!/usr/bin/env python3
"""
Run Stage 1 (Problem Framing) for project_031edc5f
"""
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.controller import PipelineController
from src.services import FilePersistenceService, SimpleModelService

def main():
    # Initialize
    data_dir = project_root / 'data'
    controller = PipelineController(
        SimpleModelService(),
        FilePersistenceService(str(data_dir))
    )

    # Run Stage 1
    project_id = 'project_031edc5f'

    print("="*60)
    print("RUNNING STAGE 1: PROBLEM FRAMING")
    print("="*60)
    print(f"\nProject ID: {project_id}")
    print(f"Stage: problem-framing")
    print("\nGenerating artifact...")

    result = controller.run_stage('problem-framing', project_id)

    print(f"\n✅ Stage executed successfully!")
    print(f"\nStage: {result.stage_name}")
    print(f"\nProblem Statement:")
    print(f"  {result.draft_artifact.problem_statement}")

    print(f"\nPICO Elements:")
    if hasattr(result.draft_artifact, 'pico_elements') and result.draft_artifact.pico_elements:
        pico = result.draft_artifact.pico_elements
        print(f"  Population: {pico.get('population', 'N/A')}")
        print(f"  Intervention: {pico.get('intervention', 'N/A')}")
        print(f"  Comparison: {pico.get('comparison', 'N/A')}")
        print(f"  Outcome: {pico.get('outcome', 'N/A')}")

    print(f"\nGoals ({len(result.draft_artifact.goals)}):")
    for i, goal in enumerate(result.draft_artifact.goals, 1):
        print(f"  {i}. {goal}")

    if result.validation_errors:
        print(f"\n⚠️  Validation errors: {result.validation_errors}")
    else:
        print(f"\n✅ No validation errors")

    # Save location
    artifact_path = data_dir / project_id / 'ProblemFraming.json'
    print(f"\n📁 Artifact saved to:")
    print(f"   {artifact_path}")

    # Ask if user wants to approve
    print("\n" + "="*60)
    approve = input("Approve this stage? (y/n): ").lower().strip()

    if approve == 'y':
        print("\nApproving stage...")
        controller.approve_stage(
            'problem-framing',
            project_id,
            edits={},
            user_notes="Approved via script"
        )
        print("✅ Stage 1 approved!")
        print("\n🎉 Ready to move to Stage 2: Research Questions")
    else:
        print("\n⏸️  Stage left as DRAFT. You can approve later via web UI.")

    print("\n" + "="*60)
    print("COMPLETE")
    print("="*60)
    print("\nNext steps:")
    print("1. View in web UI: http://localhost:3000/projects/project_031edc5f")
    print("2. Or run Stage 2: python run_stage2.py")
    print()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

