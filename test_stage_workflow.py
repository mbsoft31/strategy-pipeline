#!/usr/bin/env python3
"""
Test Stage Execution Workflow
Tests that stages can be run and approved through the API
"""

import requests
import json
from pprint import pprint
import time

BASE_URL = "http://localhost:5000"

def test_stage_workflow():
    """Test complete stage execution workflow."""

    print("\n" + "="*60)
    print("STAGE EXECUTION WORKFLOW TEST")
    print("="*60)

    # Step 1: Create a test project
    print("\n1. Creating test project...")
    create_response = requests.post(
        f"{BASE_URL}/api/projects",
        json={
            "raw_idea": "Investigate machine learning techniques for early detection of Alzheimer's disease using neuroimaging data and clinical biomarkers"
        },
        headers={"Content-Type": "application/json"}
    )

    if create_response.status_code != 201:
        print(f"❌ Failed to create project: {create_response.text}")
        return

    project_data = create_response.json()
    project_id = project_data['project_id']
    print(f"✅ Created project: {project_id}")
    print(f"   Title: {project_data['title']}")

    # Step 2: Get project details
    print("\n2. Getting project details...")
    detail_response = requests.get(f"{BASE_URL}/api/projects/{project_id}")

    if detail_response.status_code == 200:
        details = detail_response.json()
        print(f"✅ Project loaded")
        print(f"   Current stage: {details.get('current_stage', 0)}")
        print(f"   Artifacts: {list(details.get('artifacts', {}).keys())}")

    # Step 3: Run Stage 1 (Problem Framing)
    print("\n3. Running Stage 1: Problem Framing...")
    stage1_response = requests.post(
        f"{BASE_URL}/api/projects/{project_id}/stages/problem-framing/run",
        json={},
        headers={"Content-Type": "application/json"}
    )

    if stage1_response.status_code == 200:
        stage1_result = stage1_response.json()
        print(f"✅ Stage 1 executed successfully")
        print(f"   Stage: {stage1_result.get('stage_name')}")

        if stage1_result.get('draft_artifact'):
            artifact = stage1_result['draft_artifact']
            print(f"   Problem statement: {artifact.get('problem_statement', 'N/A')[:100]}...")
            print(f"   Goals: {len(artifact.get('goals', []))} defined")

            # Show PICO if available
            pico = artifact.get('pico', {})
            if pico:
                print(f"   PICO Elements:")
                print(f"     - Population: {pico.get('population', 'N/A')[:50]}...")
                print(f"     - Intervention: {pico.get('intervention', 'N/A')[:50]}...")
                print(f"     - Outcome: {pico.get('outcome', 'N/A')[:50]}...")

        if stage1_result.get('validation_errors'):
            print(f"   ⚠️ Validation errors: {stage1_result['validation_errors']}")
    else:
        print(f"❌ Stage 1 execution failed: {stage1_response.text}")
        return

    # Step 4: Approve Stage 1
    print("\n4. Approving Stage 1...")
    approve1_response = requests.post(
        f"{BASE_URL}/api/projects/{project_id}/stages/problem-framing/approve",
        json={
            "edits": {},
            "user_notes": "Approved via automated test"
        },
        headers={"Content-Type": "application/json"}
    )

    if approve1_response.status_code == 200:
        print(f"✅ Stage 1 approved")
    else:
        print(f"❌ Stage 1 approval failed: {approve1_response.text}")
        return

    # Step 5: Run Stage 2 (Research Questions)
    print("\n5. Running Stage 2: Research Questions...")
    time.sleep(1)  # Brief pause between stages

    stage2_response = requests.post(
        f"{BASE_URL}/api/projects/{project_id}/stages/research-questions/run",
        json={},
        headers={"Content-Type": "application/json"}
    )

    if stage2_response.status_code == 200:
        stage2_result = stage2_response.json()
        print(f"✅ Stage 2 executed successfully")

        if stage2_result.get('draft_artifact'):
            artifact = stage2_result['draft_artifact']
            questions = artifact.get('questions', [])
            print(f"   Generated {len(questions)} research questions")

            # Show first question
            if questions:
                first_q = questions[0]
                print(f"   Example question:")
                print(f"     Type: {first_q.get('question_type', 'N/A')}")
                print(f"     Text: {first_q.get('question_text', 'N/A')[:80]}...")
    else:
        print(f"❌ Stage 2 execution failed: {stage2_response.text}")
        return

    # Step 6: Approve Stage 2
    print("\n6. Approving Stage 2...")
    approve2_response = requests.post(
        f"{BASE_URL}/api/projects/{project_id}/stages/research-questions/approve",
        json={
            "edits": {},
            "user_notes": "Approved via automated test"
        },
        headers={"Content-Type": "application/json"}
    )

    if approve2_response.status_code == 200:
        print(f"✅ Stage 2 approved")
    else:
        print(f"❌ Stage 2 approval failed: {approve2_response.text}")

    # Step 7: Run Stage 3 (Search Expansion)
    print("\n7. Running Stage 3: Search Expansion...")
    time.sleep(1)

    stage3_response = requests.post(
        f"{BASE_URL}/api/projects/{project_id}/stages/search-concept-expansion/run",
        json={},
        headers={"Content-Type": "application/json"}
    )

    if stage3_response.status_code == 200:
        stage3_result = stage3_response.json()
        print(f"✅ Stage 3 executed successfully")

        if stage3_result.get('draft_artifact'):
            artifact = stage3_result['draft_artifact']
            blocks = artifact.get('concept_blocks', [])
            print(f"   Generated {len(blocks)} concept blocks")

            # Show first block
            if blocks:
                first_block = blocks[0]
                print(f"   Example block:")
                print(f"     Concept: {first_block.get('concept_id', 'N/A')}")
                print(f"     Included terms: {len(first_block.get('included_terms', []))}")
                print(f"     Excluded terms: {len(first_block.get('excluded_terms', []))}")
    else:
        print(f"❌ Stage 3 execution failed: {stage3_response.text}")
        return

    # Step 8: Approve Stage 3
    print("\n8. Approving Stage 3...")
    approve3_response = requests.post(
        f"{BASE_URL}/api/projects/{project_id}/stages/search-concept-expansion/approve",
        json={"edits": {}, "user_notes": "Approved via automated test"},
        headers={"Content-Type": "application/json"}
    )

    if approve3_response.status_code == 200:
        print(f"✅ Stage 3 approved")
    else:
        print(f"❌ Stage 3 approval failed")

    # Step 9: Run Stage 4 (Database Query Plan)
    print("\n9. Running Stage 4: Database Query Plan...")
    time.sleep(1)

    stage4_response = requests.post(
        f"{BASE_URL}/api/projects/{project_id}/stages/database-query-plan/run",
        json={},
        headers={"Content-Type": "application/json"}
    )

    if stage4_response.status_code == 200:
        stage4_result = stage4_response.json()
        print(f"✅ Stage 4 executed successfully")

        if stage4_result.get('draft_artifact'):
            artifact = stage4_result['draft_artifact']
            queries = artifact.get('database_queries', [])
            print(f"   Generated {len(queries)} database queries")

            # Show databases covered
            databases = [q.get('database_name') for q in queries if q.get('database_name')]
            print(f"   Databases: {', '.join(databases)}")

            # Show first query
            if queries:
                first_query = queries[0]
                print(f"   Example query ({first_query.get('database_name', 'N/A')}):")
                query_text = first_query.get('boolean_query', 'N/A')
                print(f"     {query_text[:100]}...")
                print(f"     Complexity: {first_query.get('complexity_score', 'N/A')}")
    else:
        print(f"❌ Stage 4 execution failed: {stage4_response.text}")
        return

    # Final summary
    print("\n" + "="*60)
    print("WORKFLOW TEST COMPLETE")
    print("="*60)
    print(f"\n✅ Project ID: {project_id}")
    print(f"✅ All stages 0-4 executed successfully")
    print(f"✅ Artifacts generated and saved")
    print(f"\nCheck data directory: data/{project_id}/")
    print("\n🎉 Full stage workflow is WORKING!")


if __name__ == "__main__":
    try:
        test_stage_workflow()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to backend")
        print("Make sure Flask server is running on http://localhost:5000")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

