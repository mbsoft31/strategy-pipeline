"""
Automated import fixer for SLR integration.

This script automatically updates import statements in the SLR codebase
from 'slr.' to 'src.slr.' without manual file editing.

Usage:
    python scripts/fix_slr_imports.py

Strategic Advantage:
    - Zero manual errors
    - Handles all Python files automatically
    - Preserves relative imports (from .base import)
    - Only fixes absolute imports (from slr.core import)
"""
import re
from pathlib import Path
import sys


def fix_imports_in_file(filepath: Path) -> tuple[bool, str]:
    """
    Fix imports in a single Python file.

    Returns:
        (changed, reason) tuple
    """
    try:
        content = filepath.read_text(encoding='utf-8')
        original = content
        changes = []

        # Pattern 1: from slr.module import ...
        # Example: from slr.core.models import Paper
        # Becomes: from src.slr.core.models import Paper
        new_content, count = re.subn(
            r'\bfrom slr\.([a-zA-Z_][a-zA-Z0-9_\.]*)',
            r'from src.slr.\1',
            content
        )
        if count > 0:
            changes.append(f"Fixed {count} 'from slr.*' imports")
            content = new_content

        # Pattern 2: import slr.module
        # Example: import slr.providers
        # Becomes: import src.slr.providers
        new_content, count = re.subn(
            r'\bimport slr\.([a-zA-Z_][a-zA-Z0-9_\.]*)',
            r'import src.slr.\1',
            content
        )
        if count > 0:
            changes.append(f"Fixed {count} 'import slr.*' imports")
            content = new_content

        # Write back if changed
        if content != original:
            filepath.write_text(content, encoding='utf-8')
            return True, '; '.join(changes)

        return False, "No changes needed"

    except Exception as e:
        return False, f"Error: {str(e)}"


def main():
    """Fix all Python files in src/slr/."""
    slr_dir = Path('src/slr')

    # Verify SLR directory exists
    if not slr_dir.exists():
        print("❌ ERROR: src/slr/ not found")
        print("📝 Run this first: cp -r docs/next-steps/scratch_project/slr src/slr")
        sys.exit(1)

    print("🔍 Scanning for Python files in src/slr/...")
    print(f"📁 Directory: {slr_dir.absolute()}\n")

    # Find all Python files
    py_files = list(slr_dir.rglob('*.py'))

    if not py_files:
        print("⚠️  No Python files found!")
        sys.exit(1)

    print(f"Found {len(py_files)} Python files\n")

    # Process each file
    fixed_count = 0
    skipped_count = 0
    error_count = 0

    print("Processing files:")
    print("-" * 80)

    for py_file in py_files:
        relative_path = py_file.relative_to(slr_dir)
        changed, reason = fix_imports_in_file(py_file)

        if changed:
            print(f"✅ {relative_path}: {reason}")
            fixed_count += 1
        elif "Error" in reason:
            print(f"❌ {relative_path}: {reason}")
            error_count += 1
        else:
            # Only show skipped files in verbose mode
            skipped_count += 1

    # Summary
    print("-" * 80)
    print(f"\n📊 Summary:")
    print(f"  ✅ Fixed: {fixed_count} files")
    print(f"  ⏭️  Skipped: {skipped_count} files (no changes needed)")
    print(f"  ❌ Errors: {error_count} files")
    print(f"  📁 Total: {len(py_files)} files")

    if fixed_count > 0:
        print(f"\n🎉 Successfully updated {fixed_count} files!")
        print(f"✅ SLR imports are now using 'src.slr.*' paths")

    if error_count > 0:
        print(f"\n⚠️  {error_count} files had errors - please review manually")

    # Verification step
    print(f"\n🔬 Verification:")
    print(f"Run this to test imports:")
    print(f"  python -c \"from src.slr.providers import OpenAlexProvider; print('✅ Imports working!')\"")


if __name__ == '__main__':
    main()

