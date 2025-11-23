#!/usr/bin/env python3
"""Test script for JSON API endpoints.

Tests all the new JSON API endpoints to ensure they work correctly
before connecting the frontend.
"""

import requests
import json
from pprint import pprint

BASE_URL = "http://localhost:5000"

def test_list_projects():
    """Test GET /api/projects"""
    print("\n" + "="*60)
    print("TEST: List Projects")
    print("="*60)

    response = requests.get(f"{BASE_URL}/api/projects")
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Found {len(data.get('projects', []))} projects")
        pprint(data)
        return True
    else:
        print(f"Error: {response.text}")
        return False


def test_create_project():
    """Test POST /api/projects"""
    print("\n" + "="*60)
    print("TEST: Create Project")
    print("="*60)

    payload = {
        "raw_idea": "Investigate the effectiveness of retrieval-augmented generation techniques for reducing hallucinations in large language models, particularly in medical question-answering scenarios."
    }

    response = requests.post(
        f"{BASE_URL}/api/projects",
        json=payload,
        headers={"Content-Type": "application/json"}
    )

    print(f"Status: {response.status_code}")

    if response.status_code == 201:
        data = response.json()
        print(f"Created project: {data.get('project_id')}")
        print(f"Title: {data.get('title')}")
        pprint(data)
        return data.get('project_id')
    else:
        print(f"Error: {response.text}")
        return None


def test_get_project(project_id):
    """Test GET /api/projects/:id"""
    print("\n" + "="*60)
    print("TEST: Get Project Details")
    print("="*60)

    response = requests.get(f"{BASE_URL}/api/projects/{project_id}")
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Project: {data.get('title')}")
        print(f"Current Stage: {data.get('current_stage')}")
        print(f"Artifacts: {data.get('artifacts')}")
        pprint(data)
        return True
    else:
        print(f"Error: {response.text}")
        return False


def test_get_artifact(project_id, artifact_type):
    """Test GET /api/projects/:id/artifacts/:type"""
    print("\n" + "="*60)
    print(f"TEST: Get Artifact ({artifact_type})")
    print("="*60)

    response = requests.get(
        f"{BASE_URL}/api/projects/{project_id}/artifacts/{artifact_type}"
    )
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Artifact loaded successfully")
        pprint(data)
        return True
    else:
        print(f"Error: {response.text}")
        return False


def test_run_stage(project_id, stage_name):
    """Test POST /api/projects/:id/stages/:name/run"""
    print("\n" + "="*60)
    print(f"TEST: Run Stage ({stage_name})")
    print("="*60)

    response = requests.post(
        f"{BASE_URL}/api/projects/{project_id}/stages/{stage_name}/run",
        json={},
        headers={"Content-Type": "application/json"}
    )
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Stage executed: {data.get('stage_name')}")
        print(f"Validation errors: {data.get('validation_errors', [])}")
        pprint(data)
        return True
    else:
        print(f"Error: {response.text}")
        return False


def test_approve_stage(project_id, stage_name):
    """Test POST /api/projects/:id/stages/:name/approve"""
    print("\n" + "="*60)
    print(f"TEST: Approve Stage ({stage_name})")
    print("="*60)

    payload = {
        "edits": {},
        "user_notes": "Approved via API test"
    }

    response = requests.post(
        f"{BASE_URL}/api/projects/{project_id}/stages/{stage_name}/approve",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data.get('success')}")
        pprint(data)
        return True
    else:
        print(f"Error: {response.text}")
        return False


def main():
    """Run all tests in sequence."""
    print("\n" + "="*60)
    print("JSON API ENDPOINT TESTS")
    print("="*60)
    print("\nMake sure the Flask server is running on localhost:5000")
    print("Start it with: python interfaces/web_app.py")

    input("\nPress Enter to start tests...")

    # Test 1: List existing projects
    test_list_projects()

    # Test 2: Create new project
    project_id = test_create_project()

    if not project_id:
        print("\n❌ Failed to create project. Stopping tests.")
        return

    # Test 3: Get project details
    test_get_project(project_id)

    # Test 4: Get ProjectContext artifact
    test_get_artifact(project_id, "ProjectContext")

    # Test 5: Run problem-framing stage
    test_run_stage(project_id, "problem-framing")

    # Test 6: Get ProblemFraming artifact
    test_get_artifact(project_id, "ProblemFraming")

    # Test 7: Approve project-setup stage
    test_approve_stage(project_id, "project-setup")

    # Test 8: Approve problem-framing stage
    test_approve_stage(project_id, "problem-framing")

    # Test 9: Get updated project details
    test_get_project(project_id)

    print("\n" + "="*60)
    print("✅ ALL TESTS COMPLETED")
    print("="*60)
    print(f"\nTest Project ID: {project_id}")
    print(f"Check data directory: data/{project_id}/")


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to Flask server")
        print("Make sure the server is running: python interfaces/web_app.py")
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

