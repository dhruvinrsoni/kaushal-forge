#!/usr/bin/env node

/**
 * Project Template Generator
 *
 * Merges base/ + flavors/<flavor>/ into a new project directory,
 * replacing {{TEMPLATE_VARS}} with user-provided values.
 *
 * Usage:
 *   node scripts/init-project.mjs --flavor <flavor> --name <project-name> [options]
 *
 * Options:
 *   --flavor       Template flavor (required)
 *   --name         Project name in kebab-case (required)
 *   --description  One-line project description (default: "A new project")
 *   --author       Author name (default: "Dhruvin Rupesh Soni")
 *   --github-user  GitHub username (default: "dhruvinrsoni")
 *   --license      MIT | Apache-2.0 (default: "MIT")
 *   --output       Output directory (default: ../../<name>/)
 *   --dry-run      Show what would be generated without writing
 *
 * Zero external dependencies — Node.js built-ins only.
 */

import { existsSync, mkdirSync, readdirSync, readFileSync, statSync, writeFileSync, copyFileSync } from 'node:fs';
import { basename, dirname, join, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const ROOT = resolve(__dirname, '..');

// ─── Argument Parsing ───────────────────────────────────────────────

function parseArgs(argv) {
  const args = {};
  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    if (arg === '--dry-run') {
      args.dryRun = true;
    } else if (arg.startsWith('--')) {
      const key = arg.slice(2).replace(/-([a-z])/g, (_, c) => c.toUpperCase());
      args[key] = argv[++i];
    }
  }
  return args;
}

const FLAVORS = [
  'vanilla-pwa', 'node-typescript', 'react-vite-pwa', 'chrome-extension',
  'spring-boot', 'scripts-toolbox', 'nano-app-collection', 'python-tool',
];

function printUsage() {
  console.log(`
Project Template Generator

Usage:
  node scripts/init-project.mjs --flavor <flavor> --name <project-name> [options]

Flavors:
  ${FLAVORS.join(', ')}

Options:
  --flavor       Template flavor (required)
  --name         Project name in kebab-case (required)
  --description  One-line project description
  --author       Author name (default: "Dhruvin Rupesh Soni")
  --github-user  GitHub username (default: "dhruvinrsoni")
  --license      MIT | Apache-2.0 (default: "MIT")
  --output       Output directory (default: ../../<name>/)
  --dry-run      Show what would be generated without writing

Examples:
  node scripts/init-project.mjs --flavor vanilla-pwa --name my-cool-app
  node scripts/init-project.mjs --flavor react-vite-pwa --name dashboard --description "Admin dashboard" --dry-run
  node scripts/init-project.mjs --flavor spring-boot --name api-server --license Apache-2.0
`);
}

// ─── Template Variable Resolution ───────────────────────────────────

function buildVariables(args) {
  const name = args.name;
  const year = new Date().getFullYear().toString();

  // Convert kebab-case to PascalCase for class names
  const pascalName = name.replace(/(^|-)([a-z])/g, (_, __, c) => c.toUpperCase());

  // Convert to package name (Python: underscores, Java: dots)
  const pythonPkg = name.replace(/-/g, '_');
  const javaPkg = `com.${args.githubUser || 'dhruvinrsoni'}.${name.replace(/-/g, '')}`;
  const javaPath = javaPkg.replace(/\./g, '/');

  return {
    '{{PROJECT_NAME}}': name,
    '{{PROJECT_SHORT_NAME}}': pascalName,
    '{{PROJECT_DESCRIPTION}}': args.description || 'A new project',
    '{{AUTHOR}}': args.author || 'Dhruvin Rupesh Soni',
    '{{GITHUB_USER}}': args.githubUser || 'dhruvinrsoni',
    '{{LICENSE}}': args.license || 'MIT',
    '{{YEAR}}': year,
    '{{TECH_STACK}}': getFlavorStack(args.flavor),
    '{{PACKAGE_NAME}}': args.flavor === 'python-tool' ? pythonPkg :
                        args.flavor === 'spring-boot' ? javaPkg : name,
    '{{PACKAGE_PATH}}': javaPath,
    '{{GROUP_ID}}': `com.${args.githubUser || 'dhruvinrsoni'}`,
    '{{DEVCONTAINER_IMAGE}}': getDevcontainerImage(args.flavor),
    '{{POST_CREATE_COMMAND}}': getPostCreateCommand(args.flavor),
    '{{BUILD_TEST_COMMAND}}': getBuildTestCommand(args.flavor),
    '{{PRIVACY_STANCE}}': '**All data stays on device.** Zero telemetry.',
    // Placeholder sections — user fills these in
    '{{CRITICAL_FILE_MAP_ROWS}}': '| Entry point | `src/` |',
    '{{COMMON_COMMANDS_ROWS}}': '| (fill in) | (fill in) | (fill in) |',
    '{{SKILL_ROWS}}': '',
    '{{REPO_SPECIFIC_EFFICIENCY}}': '',
    '{{ADDITIONAL_CONVENTIONS}}': '',
    '{{RELEASE_WORKFLOW}}': '',
    '{{ADDITIONAL_IGNORES}}': getAdditionalIgnores(args.flavor),
    '{{ADDITIONAL_CONTRIBUTING}}': '',
    '{{ADDITIONAL_CODEOWNERS}}': '',
    '{{COMMON_COMMANDS_SUMMARY}}': '',
    '{{SKILL_INDEX}}': '',
    '{{ADDITIONAL_COPILOT_RULES}}': '',
  };
}

function getFlavorStack(flavor) {
  const stacks = {
    'vanilla-pwa': 'HTML · CSS · Vanilla JavaScript · PWA',
    'node-typescript': 'Node.js · TypeScript · Vitest · ESLint · Prettier',
    'react-vite-pwa': 'React · TypeScript · Vite · Tailwind CSS · PWA',
    'chrome-extension': 'TypeScript · esbuild · Vitest · Chrome MV3',
    'spring-boot': 'Java 21 · Spring Boot 3 · Gradle Kotlin DSL · JUnit 5',
    'scripts-toolbox': 'Bash · PowerShell · Python · Cross-platform',
    'nano-app-collection': 'HTML · CSS · Vanilla JavaScript · Zero dependencies',
    'python-tool': 'Python 3.10+ · pytest · mypy · ruff',
  };
  return stacks[flavor] || '';
}

function getDevcontainerImage(flavor) {
  const images = {
    'spring-boot': 'mcr.microsoft.com/devcontainers/java:21',
    'python-tool': 'mcr.microsoft.com/devcontainers/python:3.12',
    'scripts-toolbox': 'mcr.microsoft.com/devcontainers/base:ubuntu',
  };
  return images[flavor] || 'mcr.microsoft.com/devcontainers/javascript-node:22';
}

function getPostCreateCommand(flavor) {
  const cmds = {
    'spring-boot': './gradlew dependencies --no-daemon',
    'python-tool': 'pip install -e \".[dev]\"',
    'scripts-toolbox': 'echo \"Ready\"',
    'vanilla-pwa': 'echo \"Ready — open index.html\"',
    'nano-app-collection': 'echo \"Ready — open index.html\"',
  };
  return cmds[flavor] || 'npm ci';
}

function getBuildTestCommand(flavor) {
  const cmds = {
    'spring-boot': './gradlew build',
    'python-tool': 'make all',
    'scripts-toolbox': 'echo \"No build step\"',
    'vanilla-pwa': 'echo \"No build step — test manually\"',
    'nano-app-collection': 'echo \"No build step — test manually\"',
  };
  return cmds[flavor] || 'npm test && npm run build';
}

function getAdditionalIgnores(flavor) {
  const ignores = {
    'chrome-extension': '# Chrome extension\nextension.zip\ndist/\nrelease/\nplaywright-report/\ntest-results/',
    'spring-boot': '# Gradle\n.gradle/\nbuild/\n!gradle/wrapper/gradle-wrapper.jar',
    'python-tool': '# Python\n*.egg-info/\n.mypy_cache/\n.ruff_cache/',
  };
  return ignores[flavor] || '';
}

// ─── File Operations ────────────────────────────────────────────────

function walkDir(dir) {
  const results = [];
  if (!existsSync(dir)) return results;

  for (const entry of readdirSync(dir)) {
    const fullPath = join(dir, entry);
    const stat = statSync(fullPath);
    if (stat.isDirectory()) {
      results.push(...walkDir(fullPath));
    } else {
      results.push(fullPath);
    }
  }
  return results;
}

function replaceVars(content, vars) {
  let result = content;
  for (const [key, value] of Object.entries(vars)) {
    result = result.split(key).join(value);
  }
  return result;
}

function isTextFile(filePath) {
  const textExtensions = new Set([
    '.md', '.txt', '.yml', '.yaml', '.json', '.xml', '.html', '.css', '.js', '.mjs',
    '.ts', '.tsx', '.jsx', '.java', '.kt', '.kts', '.py', '.sh', '.ps1', '.cmd',
    '.bat', '.toml', '.cfg', '.ini', '.properties', '.gradle', '.template', '.overlay',
    '.webmanifest', '.gitignore', '.gitattributes', '.editorconfig', '.eslintrc',
    '.prettierrc', '.env', '.dockerignore',
  ]);
  const ext = filePath.substring(filePath.lastIndexOf('.'));
  // Also check dot-files like .gitkeep, .gitignore
  const base = basename(filePath);
  return textExtensions.has(ext) || base.startsWith('.') || !ext.includes('.');
}

// ─── Main Generator ─────────────────────────────────────────────────

function generate(args) {
  const flavor = args.flavor;
  const name = args.name;
  const dryRun = args.dryRun || false;
  const output = args.output ? resolve(args.output) : resolve(ROOT, '..', name);

  // Validate
  if (!FLAVORS.includes(flavor)) {
    console.error(`Error: Unknown flavor "${flavor}". Available: ${FLAVORS.join(', ')}`);
    process.exit(1);
  }

  if (!name || !/^[a-z][a-z0-9-]*$/.test(name)) {
    console.error('Error: --name must be kebab-case (e.g., "my-project")');
    process.exit(1);
  }

  if (existsSync(output) && readdirSync(output).length > 0) {
    console.error(`Error: Output directory already exists and is not empty: ${output}`);
    process.exit(1);
  }

  const vars = buildVariables(args);
  const baseDir = join(ROOT, 'base');
  const flavorDir = join(ROOT, 'flavors', flavor);

  console.log(`\nGenerating "${name}" from flavor "${flavor}"`);
  console.log(`Output: ${output}`);
  if (dryRun) console.log('DRY RUN — no files will be written\n');

  const generated = [];
  const overlays = [];

  // Phase 1: Copy base files
  for (const srcPath of walkDir(baseDir)) {
    const relPath = relative(baseDir, srcPath);
    processFile(srcPath, relPath, output, vars, dryRun, generated, overlays);
  }

  // Phase 2: Copy flavor files (overwrites base where they overlap)
  for (const srcPath of walkDir(flavorDir)) {
    const relPath = relative(flavorDir, srcPath);
    processFile(srcPath, relPath, output, vars, dryRun, generated, overlays);
  }

  // Phase 3: Apply overlays (append to existing files)
  for (const { targetPath, content } of overlays) {
    if (dryRun) {
      console.log(`  [overlay] ${relative(output, targetPath)}`);
    } else {
      const existing = existsSync(targetPath) ? readFileSync(targetPath, 'utf-8') : '';
      writeFileSync(targetPath, existing + content);
    }
  }

  // Summary
  console.log(`\n${dryRun ? 'Would generate' : 'Generated'} ${generated.length} files + ${overlays.length} overlays`);

  if (!dryRun) {
    console.log(`\nNext steps:`);
    console.log(`  cd ${output}`);
    console.log(`  git init`);
    console.log(`  # Review and customize CLAUDE.md`);
    console.log(`  # Fill in {{TEMPLATE_VARS}} placeholders if any remain`);
    const setupCmds = {
      'vanilla-pwa': '  python -m http.server 8000',
      'node-typescript': '  npm install\n  npm test',
      'react-vite-pwa': '  npm install\n  npm run dev',
      'chrome-extension': '  npm install\n  npm run build:dev',
      'spring-boot': '  ./gradlew bootRun',
      'python-tool': '  make dev\n  make all',
      'scripts-toolbox': '  # Ready to go — add your scripts',
      'nano-app-collection': '  python -m http.server 8000',
    };
    console.log(setupCmds[flavor] || '');
  }
}

function processFile(srcPath, relPath, output, vars, dryRun, generated, overlays) {
  let destRelPath = relPath;
  const isOverlay = relPath.endsWith('.overlay');
  const isTemplate = relPath.endsWith('.template');

  // Strip .template suffix from destination
  if (isTemplate) {
    destRelPath = relPath.slice(0, -'.template'.length);
  }

  // Replace path-level variables (for Java package paths etc.)
  destRelPath = replaceVars(destRelPath, {
    '{{PACKAGE_PATH}}': vars['{{PACKAGE_PATH}}'],
    '{{PACKAGE_NAME}}': vars['{{PACKAGE_NAME}}'],
  });

  // Handle "pkg" placeholder in python-tool (src/pkg/ → src/<package_name>/)
  if (destRelPath.includes('/pkg/') || destRelPath.includes('\\pkg\\')) {
    destRelPath = destRelPath.replace(/[/\\]pkg[/\\]/, `/${vars['{{PACKAGE_NAME}}']}/`);
  }

  const destPath = join(output, destRelPath);

  if (isOverlay) {
    // Queue overlay to be applied after all base files are written
    const targetFileName = destRelPath.slice(0, -'.overlay'.length);
    const targetPath = join(output, targetFileName);
    let content = readFileSync(srcPath, 'utf-8');
    content = replaceVars(content, vars);
    overlays.push({ targetPath, content });
    return;
  }

  if (dryRun) {
    console.log(`  ${destRelPath}`);
    generated.push(destRelPath);
    return;
  }

  // Create directory
  const destDir = dirname(destPath);
  if (!existsSync(destDir)) {
    mkdirSync(destDir, { recursive: true });
  }

  // Text files: replace variables. Binary files: copy as-is.
  if (isTextFile(srcPath)) {
    let content = readFileSync(srcPath, 'utf-8');
    content = replaceVars(content, vars);
    writeFileSync(destPath, content);
  } else {
    copyFileSync(srcPath, destPath);
  }

  generated.push(destRelPath);
}

// ─── Entry Point ────────────────────────────────────────────────────

const args = parseArgs(process.argv.slice(2));

if (!args.flavor || !args.name) {
  printUsage();
  process.exit(args.flavor || args.name ? 1 : 0);
}

generate(args);
