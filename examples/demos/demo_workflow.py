"""Complete workflow demo: Stage 0 -> Stage 1 using the CLI.

Parses JSON output from the CLI commands to automatically detect the project_id,
run problem-framing, approve artifacts, and show project state.
"""
import subprocess
import sys
import json
from pathlib import Path

CLI_MODULE = "interfaces.cli"


def run_cli_json(*args):
    cmd = [sys.executable, "-m", CLI_MODULE] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.stderr:
        print("STDERR:", result.stderr, file=sys.stderr)
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        print("Failed to parse JSON from CLI. Raw output:\n", result.stdout)
        return None, result.returncode
    return data, result.returncode

print("=" * 60)
print("COMPLETE WORKFLOW DEMO: Stage 0 -> Stage 1")
print("=" * 60)

# Step 1: Start a project
print("\n[Step 1] Starting new project...")
idea = "Exploring the impact of remote work on team collaboration and innovation"
start_data, code = run_cli_json("start", idea)
if code != 0 or not start_data:
    print("ERROR: Failed to start project")
    sys.exit(1)
project_id = start_data.get("project_id")
print(f"Project created: {project_id}")

# Step 2: Approve ProjectContext
print("\n[Step 2] Approving ProjectContext artifact...")
approve_ctx_data, code = run_cli_json("approve", project_id, "ProjectContext", "--edits", json.dumps({"title": start_data.get("title") + " (approved)"}))
if code != 0:
    print("ERROR: Failed to approve ProjectContext")
    sys.exit(1)
print("ProjectContext approved.")

# Step 3: Run Stage 1 (problem-framing)
print("\n[Step 3] Running problem-framing stage...")
framing_data, code = run_cli_json("run-stage", "problem-framing", project_id)
if code != 0:
    print("ERROR: Failed to run problem-framing stage")
    sys.exit(1)
print("ProblemFraming draft generated.")

# Step 4: Approve ProblemFraming
print("\n[Step 4] Approving ProblemFraming artifact...")
approve_pf_data, code = run_cli_json("approve", project_id, "ProblemFraming")
if code != 0:
    print("ERROR: Failed to approve ProblemFraming")
    sys.exit(1)
print("ProblemFraming approved.")

# Step 5: Show project summary
print("\n[Step 5] Showing project details...")
show_data, code = run_cli_json("show", project_id)
if code != 0:
    print("ERROR: Failed to show project details")
    sys.exit(1)
print(json.dumps(show_data, indent=2))

print("\n=" * 60)
print("Demo complete! Review artifacts under ./data/", project_id)
print("=" * 60)
