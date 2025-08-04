# Global Sub-Agent Workflows for Multi-Project Development

## Overview

**Global sub-agents designed for your 7-project workspace with intelligent project detection and universal workflow patterns.**

Projects: `tylergohr.com`, `invoice-chaser`, `AI Orchestrator Platform`, `grow`, `idaho-adventures`, `snake-river-adventures`, `toast-of-the-town`

## Universal Sub-Agent Workflows

### 1. 🚀 Universal Development Environment Sub-Agent
**Priority**: CRITICAL | **Scope**: All Projects | **Timeout Risk**: Eliminated

**Trigger Patterns**: `start dev`, `development server`, `npm run dev`, `dev environment`

**Global Workflow**:
```
Use the Agent tool for intelligent multi-project development setup:

**Auto-Detection Strategy**:
1. Detect current project context from working directory
2. If not in project directory, prompt for project selection from:
   - tylergohr.com (Next.js + TypeScript)
   - invoice-chaser (React + Express + Supabase)  
   - AI Orchestrator Platform (Python + PRP)
   - grow/idaho-adventures/snake-river-adventures/toast-of-the-town (React + Vite)

**Universal Environment Setup**:
1. Navigate to detected/selected project directory
2. Project-specific server management:
   - **Next.js projects**: Use smart port allocation (dev-start <project>)
   - **Vite projects**: Standard npm run dev with port detection
   - **Express projects**: npm start for concurrent frontend/backend
   - **Python projects**: uv-based development commands

3. Environment validation:
   - Check dependencies (package.json vs requirements.txt)
   - Verify development server startup
   - Test accessibility in cloud environment
   - Set project-specific environment variables

4. Quality gates readiness:
   - Verify TypeScript configuration exists
   - Check linting setup (ESLint vs ruff)
   - Confirm testing framework availability

**Success Criteria**: Project running, accessible, with proper development context
**Adaptability**: Intelligent project detection with framework-specific handling
```

### 2. 🧪 Universal Testing & Quality Sub-Agent  
**Priority**: HIGH | **Scope**: All Projects | **Timeout Risk**: Eliminated

**Trigger Patterns**: `test`, `quality`, `validate`, `check`, `e2e`, `smoke`

**Global Workflow**:
```
Use the Agent tool for intelligent testing across any project:

**Project Detection & Setup**:
1. Auto-detect project type from current directory
2. Identify testing framework:
   - **Playwright** (tylergohr.com)
   - **Jest/Vitest** (React projects)
   - **pytest** (Python projects)
   - **Standard npm test** (fallback)

**Universal Quality Gates**:
1. **Type Checking**:
   - TypeScript projects: npm run typecheck
   - Python projects: mypy .
   - Report compilation errors with file/line context

2. **Code Quality**:
   - JavaScript/TypeScript: npm run lint (ESLint)
   - Python: ruff check --fix
   - Auto-fix what's possible, report remaining issues

3. **Testing Execution**:
   - **tylergohr.com**: npm run test:e2e:smoke (quick) or npm run test:e2e:dev
   - **React projects**: npm test or npm run test:unit
   - **Python projects**: uv run pytest tests/ -v
   - **Express projects**: Backend + frontend testing

4. **Build Validation**:
   - Frontend projects: npm run build
   - Python projects: verify package structure
   - Check bundle sizes and performance budgets

**Adaptive Results**:
- Project-specific success criteria
- Framework-appropriate error reporting  
- Next steps based on project type and results

**Success Criteria**: All quality gates pass for detected project type
```

### 3. 📦 Universal Build & Deploy Sub-Agent
**Priority**: MEDIUM | **Scope**: All Projects | **Pattern**: Production readiness

**Trigger Patterns**: `build`, `deploy`, `production`, `release`, `publish`

**Global Workflow**:
```
Use the Agent tool for universal build and deployment preparation:

**Project-Specific Build Strategy**:
1. **Next.js (tylergohr.com)**:
   - npm run validate (comprehensive quality gates)
   - npm run build (production build)
   - npm run bundle-check (<6MB budget)
   - Docker container readiness for Google Cloud Run

2. **React + Vite (personal projects)**:
   - npm run typecheck && npm run lint
   - npm run build (Vite production build)
   - npm run preview (test production build)

3. **React + Express (invoice-chaser)**:
   - Frontend: npm run build
   - Backend: TypeScript compilation check
   - Database migration validation (Supabase)

4. **Python (AI Orchestrator Platform)**:
   - ruff check --fix && mypy .
   - uv run pytest tests/ -v
   - Package structure validation

**Universal Deployment Prep**:
- Environment variable validation
- Dependency security audit
- Performance benchmarking
- Cloud platform readiness check

**Success Criteria**: Project ready for production deployment
```

### 4. 🔄 Universal Git Workflow Sub-Agent
**Priority**: HIGH | **Scope**: All Projects | **Pattern**: Quality → Review → Commit

**Trigger Patterns**: `commit`, `git`, `save changes`, `push`, `pull request`

**Global Workflow**:
```
Use the Agent tool for intelligent git operations across any project:

**Pre-Commit Quality Validation**:
1. Auto-detect project type and run appropriate quality gates
2. **Universal quality check**:
   - TypeScript projects: npm run typecheck
   - Python projects: ruff check --fix && mypy .
   - All projects: Run linting and basic tests

3. **Only proceed if quality gates pass**

**Intelligent Git Operations**:
1. **Change Analysis**:
   - git status --porcelain for file summary
   - Analyze scope: frontend, backend, config, docs
   - Identify breaking vs non-breaking changes

2. **Smart Commit Messages**:
   - Auto-detect change type: feat, fix, docs, refactor, test
   - Follow conventional commits format
   - Include project context when working across multiple projects

3. **Branch Management**:
   - Enforce ≤15 character branch names (Docker compatibility)
   - Suggest project-appropriate branch names
   - Handle multi-project workflows

**Cross-Project Awareness**:
- Detect if changes affect multiple projects
- Warn about cross-project dependencies
- Suggest appropriate commit scoping

**Success Criteria**: Clean commit with quality validation and proper messaging
```

## Global Slash Command Strategy

### Universal Slash Commands for All Projects

```bash
# High-priority global automation
/dev         → Universal Development Environment Sub-Agent
/test        → Universal Testing & Quality Sub-Agent  
/build       → Universal Build & Deploy Sub-Agent
/commit      → Universal Git Workflow Sub-Agent

# Specialized global automation
/switch      → Project switching with context preservation
/quality     → Quality gates across any project
/deploy      → Production deployment preparation
/sync        → Multi-project dependency synchronization
```

### Project-Aware Command Examples

```markdown
# Auto-detects current project and runs appropriate dev setup
User: "/dev"
Claude: [Detects tylergohr.com] → [Launches Next.js dev server with port allocation]

# Switches projects intelligently  
User: "/switch invoice-chaser"
Claude: [Preserves context] → [Switches to invoice-chaser] → [Sets up React+Express environment]

# Universal testing that adapts to project
User: "/test"
Claude: [Detects project type] → [Runs appropriate test suite] → [Reports project-specific results]

# Commit workflow with project-aware quality gates
User: "/commit add user authentication"
Claude: [Runs project-specific validation] → [Creates appropriate commit message] → [Commits with project context]
```

## Multi-Project Intelligence

### Project Detection Logic
```bash
# Auto-detection based on directory structure
/home/user/tylergohr.com/          → Next.js portfolio (Playwright testing)
/home/user/invoice-chaser/          → React+Express (Supabase integration)
/home/user/AI Orchestrator Platform/ → Python PRP (uv + pytest)
/home/user/my-development-projects/* → React+Vite (standard testing)
```

### Technology Stack Adaptation
```bash
# Framework-specific command mapping
Next.js:     npm run dev → npm run test:e2e:smoke → npm run validate
React+Vite:  npm run dev → npm test → npm run build  
Python:      uv commands → pytest → mypy + ruff
Express:     npm start → backend/frontend testing → build validation
```

### Smart Port Management
```bash
# Global port allocation system
dev-start tylergohr     → Port 3000+ with smart allocation
dev-start invoice       → Port 5000/5173 concurrent setup
dev-start grow          → Next available port from 3000+
dev-status              → Show all running projects globally
```

## Productivity Benefits of Global Approach

### Cross-Project Efficiency:
- **One set of slash commands** works across all 7 projects
- **Intelligent adaptation** to project-specific needs
- **Context preservation** when switching between projects
- **Consistent workflows** regardless of technology stack

### Reduced Cognitive Load:
- **No need to remember** project-specific commands
- **Automatic environment setup** for any project
- **Universal quality standards** across all codebases
- **Smart defaults** based on project detection

### Timeout Elimination:
- **Global environment handling** prevents cloud workstation timeouts
- **Project-aware retries** with appropriate fallbacks
- **Universal error handling** adapted to each technology stack

## Implementation Strategy

### Phase 1: Core Global Sub-Agents
1. **Universal Development Environment** - Highest ROI across all projects
2. **Universal Testing & Quality** - Critical for maintaining code quality

### Phase 2: Workflow Integration
1. **Universal Git Workflow** - Standardizes commit practices
2. **Universal Build & Deploy** - Production readiness across projects

### Phase 3: Advanced Multi-Project Features
1. **Project switching with context preservation**
2. **Cross-project dependency management**
3. **Multi-project deployment orchestration**

## Global Automation Benefits

### Measured Improvements Expected:
- **95%+ timeout elimination** across all projects
- **80% reduction** in project-switching overhead  
- **Unified development experience** regardless of project
- **Consistent quality standards** across entire codebase portfolio

### Universal Patterns:
1. **Project-agnostic entry points** (`/dev`, `/test`, `/commit`)
2. **Intelligent technology detection** and adaptation
3. **Consistent error handling** across all frameworks
4. **Smart environment management** for cloud development

---

**Focus**: One set of sub-agents that work intelligently across all 7 projects
**Benefit**: Seamless multi-project development with zero context switching overhead
**Goal**: Universal automation that adapts to any project in your workspace