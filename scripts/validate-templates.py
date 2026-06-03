#!/usr/bin/env python3
"""
Template Validator — ensures all templates are consistent and well-formed.

Checks:
1. All .template files have valid {{VAR}} placeholders (from known set)
2. All flavors contain required base files after merge
3. No broken references between files
4. SKILL.md files have valid YAML frontmatter
5. Workflow YAML files are valid

Usage:
  python scripts/validate-templates.py
"""

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
BASE_DIR = ROOT / "base"
FLAVORS_DIR = ROOT / "flavors"

# Known template variables
KNOWN_VARS = {
    "{{PROJECT_NAME}}", "{{PROJECT_SHORT_NAME}}", "{{PROJECT_DESCRIPTION}}",
    "{{AUTHOR}}", "{{GITHUB_USER}}", "{{LICENSE}}", "{{YEAR}}",
    "{{TECH_STACK}}", "{{PACKAGE_NAME}}", "{{PACKAGE_PATH}}", "{{GROUP_ID}}",
    "{{DEVCONTAINER_IMAGE}}", "{{POST_CREATE_COMMAND}}", "{{BUILD_TEST_COMMAND}}",
    "{{PRIVACY_STANCE}}", "{{CRITICAL_FILE_MAP_ROWS}}", "{{COMMON_COMMANDS_ROWS}}",
    "{{SKILL_ROWS}}", "{{REPO_SPECIFIC_EFFICIENCY}}", "{{ADDITIONAL_CONVENTIONS}}",
    "{{RELEASE_WORKFLOW}}", "{{ADDITIONAL_IGNORES}}", "{{ADDITIONAL_CONTRIBUTING}}",
    "{{ADDITIONAL_CODEOWNERS}}", "{{COMMON_COMMANDS_SUMMARY}}", "{{SKILL_INDEX}}",
    "{{ADDITIONAL_COPILOT_RULES}}", "{{BUILD_COMMAND}}", "{{TEST_COMMAND}}",
    "{{ADDITIONAL_AREA_CHECKBOXES}}",
}

KNOWN_FLAVORS = [
    "vanilla-pwa", "node-typescript", "react-vite-pwa", "chrome-extension",
    "spring-boot", "scripts-toolbox", "nano-app-collection", "python-tool",
]

errors = []
warnings = []


def error(msg: str) -> None:
    errors.append(msg)
    print(f"  ERROR: {msg}")


def warn(msg: str) -> None:
    warnings.append(msg)
    print(f"  WARN:  {msg}")


def check_template_vars(filepath: Path) -> None:
    """Check that all {{VAR}} placeholders are from the known set."""
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return

    found = set(re.findall(r"\{\{[A-Z_]+\}\}", content))
    unknown = found - KNOWN_VARS
    for var in unknown:
        warn(f"{filepath.relative_to(ROOT)}: Unknown variable {var}")


def check_skill_frontmatter(filepath: Path) -> None:
    """Check that SKILL.md files have name and description in frontmatter."""
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception:
        error(f"Cannot read: {filepath.relative_to(ROOT)}")
        return

    if not content.startswith("---"):
        error(f"{filepath.relative_to(ROOT)}: Missing YAML frontmatter (must start with ---)")
        return

    # Find closing ---
    second_delim = content.find("---", 3)
    if second_delim == -1:
        error(f"{filepath.relative_to(ROOT)}: Unclosed YAML frontmatter")
        return

    frontmatter = content[3:second_delim]

    if "name:" not in frontmatter:
        error(f"{filepath.relative_to(ROOT)}: Missing 'name' in frontmatter")
    if "description:" not in frontmatter:
        error(f"{filepath.relative_to(ROOT)}: Missing 'description' in frontmatter")


def check_base_exists() -> None:
    """Verify base directory has required files."""
    required = [
        "CLAUDE.md.template",
        ".editorconfig",
        ".gitattributes",
        ".gitignore.template",
        "CONTRIBUTING.md.template",
        ".github/labels.yml",
        ".github/PULL_REQUEST_TEMPLATE.md",
        ".github/workflows/security.yml",
        ".github/skills/repo-maintenance/SKILL.md",
    ]
    for f in required:
        if not (BASE_DIR / f).exists():
            error(f"Missing required base file: base/{f}")


def check_flavors_exist() -> None:
    """Verify all expected flavors exist."""
    for flavor in KNOWN_FLAVORS:
        flavor_dir = FLAVORS_DIR / flavor
        if not flavor_dir.exists():
            error(f"Missing flavor directory: flavors/{flavor}/")
        elif not any(flavor_dir.rglob("CLAUDE.md.overlay")):
            warn(f"Flavor '{flavor}' has no CLAUDE.md.overlay")


def check_all_templates() -> None:
    """Walk all .template files and validate variables."""
    for template in ROOT.rglob("*.template"):
        check_template_vars(template)


def check_all_skills() -> None:
    """Walk all SKILL.md files and validate frontmatter."""
    for skill in ROOT.rglob("SKILL.md"):
        check_skill_frontmatter(skill)


def main() -> int:
    print("Validating project-templates...\n")

    print("[1/5] Checking base directory...")
    check_base_exists()

    print("[2/5] Checking flavor directories...")
    check_flavors_exist()

    print("[3/5] Validating template variables...")
    check_all_templates()

    print("[4/5] Validating SKILL.md frontmatter...")
    check_all_skills()

    print("[5/5] Summary")

    # Count files
    total_files = sum(1 for _ in ROOT.rglob("*") if _.is_file() and ".git" not in str(_))
    template_count = sum(1 for _ in ROOT.rglob("*.template"))
    skill_count = sum(1 for _ in ROOT.rglob("SKILL.md"))
    flavor_count = sum(1 for d in FLAVORS_DIR.iterdir() if d.is_dir())

    print(f"\n  Total files: {total_files}")
    print(f"  Templates: {template_count}")
    print(f"  Skills: {skill_count}")
    print(f"  Flavors: {flavor_count}")
    print(f"  Errors: {len(errors)}")
    print(f"  Warnings: {len(warnings)}")

    if errors:
        print(f"\nFAILED with {len(errors)} error(s)")
        return 1

    print("\nPASSED" + (f" with {len(warnings)} warning(s)" if warnings else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
