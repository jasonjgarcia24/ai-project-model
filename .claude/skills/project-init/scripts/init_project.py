#!/usr/bin/env python3
"""
AI Project Model — Project Initializer

Creates a new AI project directory with a starter project.yaml from the
unified template. Pre-fills the project name and prints next-steps instructions.

Usage:
    python init_project.py "<project_name>" [--dir <parent_directory>]

Examples:
    python init_project.py "AI-Powered Support Ticket Triage"
    python init_project.py "Customer Churn Predictor" --dir /home/user/projects
"""

import argparse
import re
import shutil
import sys
from pathlib import Path


def slugify(name: str) -> str:
    """Convert a project name to a directory-safe slug."""
    slug = name.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    slug = slug.strip('-')
    return slug


def find_project_root() -> Path:
    """Find the AI Project Model root by looking for templates/project.yaml."""
    # Walk up from this script's location
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / "templates" / "project.yaml").exists():
            return current
        current = current.parent

    # Fallback: try common locations
    candidates = [
        Path.home() / "Documents" / "ai-project-model",
        Path.cwd(),
    ]
    for candidate in candidates:
        if (candidate / "templates" / "project.yaml").exists():
            return candidate

    return None


def init_project(project_name: str, parent_dir: str = None) -> Path:
    """
    Initialize a new AI project directory.

    Args:
        project_name: Human-readable project name
        parent_dir: Parent directory for the project (defaults to cwd)

    Returns:
        Path to the created project directory, or None on error
    """
    # Find the framework root
    framework_root = find_project_root()
    if framework_root is None:
        print("Error: Could not find AI Project Model framework root.")
        print("Expected to find templates/project.yaml in a parent directory.")
        return None

    template_path = framework_root / "templates" / "project.yaml"
    if not template_path.exists():
        print(f"Error: Template not found at {template_path}")
        return None

    # Determine project directory
    slug = slugify(project_name)
    if not slug:
        print("Error: Project name produced an empty slug.")
        return None

    parent = Path(parent_dir).resolve() if parent_dir else Path.cwd()
    project_dir = parent / slug

    # Create project directory
    if project_dir.exists():
        print(f"Error: Directory already exists: {project_dir}")
        print("Choose a different name or remove the existing directory.")
        return None

    project_dir.mkdir(parents=True)

    # Copy template
    dest_yaml = project_dir / "project.yaml"
    shutil.copy2(template_path, dest_yaml)

    # Pre-fill project name in the YAML
    content = dest_yaml.read_text()
    content = content.replace(
        'project_name: ""',
        f'project_name: "{project_name}"',
        1  # Only replace the first occurrence (in metadata)
    )
    dest_yaml.write_text(content)

    # Print results
    print(f"Project initialized: {project_dir}")
    print(f"  project.yaml created with project name: {project_name}")
    print()
    print("=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print()
    print(f"1. Open {dest_yaml}")
    print("   Fill out these sections first:")
    print("   - metadata        (authors, date)")
    print("   - problem_statement (target user, problem, desired outcome)")
    print("   - ai_justification  (why AI is warranted)")
    print("   - success_metrics   (technical, human-centered, business)")
    print("   - roles             (team members and responsibilities)")
    print("   - responsible_ai    (potential harms, bias risks, privacy)")
    print("   - risks             (project risks and mitigations)")
    print("   - timeline          (phase start/end dates)")
    print()
    print("2. Generate artifacts in order:")
    print()
    print("   Phase 1 - Kickoff:")
    print("     Run the kickoff-populate skill to generate the kick-off Google Doc")
    print()
    print("   Phase 1-3 - Requirements:")
    print("     Fill out the 'requirements' section in project.yaml")
    print("     Run the requirements-populate skill to generate the requirements Google Doc")
    print()
    print("   Ongoing - Tracking:")
    print("     Fill out milestones, sprints, tasks, resource_matrix, decisions")
    print("     Run the tracking-populate skill to generate the tracking Google Sheet")
    print()
    print("   Each Sprint - Engineering Review:")
    print("     Fill out the 'sprint_review' section with current sprint data")
    print("     Run the eng-review-populate skill to generate the sprint review deck")
    print()
    print("   Each Phase Gate - Leadership Review:")
    print("     Fill out project_health, escalations, budget")
    print("     Run the leadership-review-populate skill for the strategic update deck")
    print()
    print("3. Reference example:")
    print(f"   {framework_root / 'templates' / 'examples' / 'project_example_support_triage.yaml'}")
    print()
    print("=" * 70)

    return project_dir


def main():
    parser = argparse.ArgumentParser(
        description="Initialize a new AI project with the AI Project Model framework"
    )
    parser.add_argument(
        "project_name",
        help="Human-readable project name (e.g., 'AI-Powered Support Ticket Triage')"
    )
    parser.add_argument(
        "--dir",
        dest="parent_dir",
        default=None,
        help="Parent directory for the project (defaults to current directory)"
    )

    args = parser.parse_args()

    result = init_project(args.project_name, args.parent_dir)
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
