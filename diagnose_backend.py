#!/usr/bin/env python3
"""Quick diagnostic to test backend API setup."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("="*60)
print("BACKEND API DIAGNOSTIC")
print("="*60)

# Test 1: Import check
print("\n1. Testing imports...")
try:
    from flask import Flask
    print("   ✅ Flask imported")
except ImportError as e:
    print(f"   ❌ Flask import failed: {e}")
    sys.exit(1)

try:
    from flask_cors import CORS
    print("   ✅ flask-cors imported")
except ImportError as e:
    print(f"   ❌ flask-cors import failed: {e}")
    print("   Run: pip install flask-cors==4.0.0")
    sys.exit(1)

try:
    from src.controller import PipelineController
    print("   ✅ PipelineController imported")
except ImportError as e:
    print(f"   ❌ PipelineController import failed: {e}")
    sys.exit(1)

try:
    from src.services import FilePersistenceService, SimpleModelService
    print("   ✅ Services imported")
except ImportError as e:
    print(f"   ❌ Services import failed: {e}")
    sys.exit(1)

# Test 2: Controller initialization
print("\n2. Testing controller...")
try:
    data_dir = project_root / 'data'
    data_dir.mkdir(exist_ok=True)

    controller = PipelineController(
        SimpleModelService(),
        FilePersistenceService(base_dir=str(data_dir))
    )
    print("   ✅ Controller initialized")
except Exception as e:
    print(f"   ❌ Controller initialization failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: List projects
print("\n3. Testing project listing...")
try:
    projects = controller.list_projects()
    print(f"   ✅ Found {len(projects)} projects")
    for pid in projects[:3]:  # Show first 3
        print(f"      - {pid}")
except Exception as e:
    print(f"   ❌ List projects failed: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Create test project
print("\n4. Testing project creation...")
try:
    result = controller.start_project(
        raw_idea="Test project for diagnostic purposes - AI hallucination reduction techniques"
    )
    project_id = result.draft_artifact.id
    print(f"   ✅ Created test project: {project_id}")
    print(f"      Title: {result.draft_artifact.title}")
except Exception as e:
    print(f"   ❌ Project creation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Artifact serialization
print("\n5. Testing artifact serialization...")
try:
    from dataclasses import asdict, is_dataclass

    artifact = result.draft_artifact

    # Try model_dump (Pydantic)
    if hasattr(artifact, 'model_dump'):
        data = artifact.model_dump()
        print("   ✅ Pydantic model_dump() works")
    # Try dict() method
    elif hasattr(artifact, 'dict'):
        data = artifact.dict()
        print("   ✅ dict() method works")
    # Try dataclass
    elif is_dataclass(artifact):
        data = asdict(artifact)
        print("   ✅ dataclass asdict() works")
    else:
        print("   ⚠️  Using __dict__ fallback")
        data = artifact.__dict__

    print(f"      Serialized {len(data)} fields")
except Exception as e:
    print(f"   ❌ Serialization failed: {e}")
    import traceback
    traceback.print_exc()

# Test 6: Flask app creation
print("\n6. Testing Flask app...")
try:
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": ["http://localhost:3000", "http://localhost:5173"]}})
    print("   ✅ Flask app created with CORS")
except Exception as e:
    print(f"   ❌ Flask app creation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Summary
print("\n" + "="*60)
print("DIAGNOSTIC COMPLETE")
print("="*60)
print("\n✅ All checks passed!")
print("\nYou can now start the backend:")
print("   python interfaces/web_app.py")
print("\nOr run the test script:")
print("   python test_api_endpoints.py")
print()

