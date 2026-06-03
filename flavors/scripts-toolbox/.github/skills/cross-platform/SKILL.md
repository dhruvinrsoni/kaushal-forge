---
name: cross-platform
description: >
  Cross-platform scripting patterns — Windows (.cmd/.ps1) + Unix (.sh) parity,
  path handling, environment detection, and portable conventions.
metadata:
  version: "1.0.0"
  reasoning_mode: linear
---

# Cross-Platform Scripting

## File Convention

Every script should have both platform variants:

```
scripts/
  my-tool.sh        # Unix (bash)
  my-tool.ps1       # Windows (PowerShell)
  my-tool.cmd       # Windows (cmd) — optional, for simple wrappers
```

## Portable Patterns

### Environment detection
```bash
# Bash
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
  echo "Windows (Git Bash)"
elif [[ "$OSTYPE" == "darwin"* ]]; then
  echo "macOS"
else
  echo "Linux"
fi
```

```powershell
# PowerShell
if ($IsWindows) { "Windows" }
elseif ($IsMacOS) { "macOS" }
else { "Linux" }
```

### Path handling
```bash
# Always use forward slashes in bash, even on Windows Git Bash
CONFIG_DIR="$HOME/.config/my-tool"
```

```powershell
# PowerShell: use Join-Path for cross-platform paths
$configDir = Join-Path $HOME ".config" "my-tool"
```

## Script Header Convention

Every script should start with:
```bash
#!/usr/bin/env bash
set -euo pipefail
# Description: One-line purpose
# Usage: ./script.sh [args]
```

```powershell
#Requires -Version 7.0
<#
.SYNOPSIS
    One-line purpose
.EXAMPLE
    ./script.ps1 -Arg value
#>
[CmdletBinding()]
param()
```

## DRY: Single Source of Truth

If a script has logic shared between platforms, consider:
1. A `.logic` or `.conf` file with the core data (like git-sutras' `core.logic`)
2. Thin platform wrappers that read the shared file
