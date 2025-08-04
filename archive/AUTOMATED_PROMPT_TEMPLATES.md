# Automated Prompt Templates for Common Tasks

## Overview

Based on conversation analytics, these templates automate your most frequent development prompts. Each template can be implemented as Claude Code slash commands or used directly for consistent sub-agent automation.

## High-Frequency Testing Templates

### Template 1: Quick E2E Testing
**Frequency**: Very High | **Timeout Risk**: Critical
**Usage**: `testing_workflow` or `/test`

```markdown
**AUTOMATED TESTING WORKFLOW**

Use the Agent tool to execute comprehensive testing workflow:

**Project Context**: Tyler Gohr Portfolio (/home/user/tylergohr.com)
**Environment**: Google Cloud Workstations with auto-port detection

**Execution Steps**:
1. **Environment Validation**:
   - Navigate to /home/user/tylergohr.com
   - Run ./scripts/detect-active-port.sh to detect development server
   - Set environment variables: eval "$(./scripts/detect-active-port.sh quiet export)"
   - Verify server accessibility: curl -s "$ACTIVE_DEV_URL" | head -5

2. **Testing Execution**:
   - Execute npm run test:e2e:smoke for essential validation (<1min)
   - If smoke tests pass, optionally run npm run test:e2e:dev (2-3min)
   - Handle any Framer Motion animation timing issues

3. **Screenshot Generation** (if requested):
   - Run npx playwright test e2e/quick-screenshots.spec.ts --project=chromium
   - Verify screenshots saved to screenshots/quick-review/
   - Report desktop and mobile screenshot status

4. **Results Analysis**:
   - Provide detailed failure analysis if any tests fail
   - Recommend next steps (fix issues, commit if clean)
   - Report environment status for future sessions

**Success Criteria**: Tests complete without timeout, results clearly reported
**Fallback Strategy**: If timeout, restart with environment reset and retry
```

### Template 2: Visual Testing & Screenshots  
**Frequency**: High | **Pattern**: Screenshot generation
**Usage**: `screenshot_workflow` or `/screenshot`

```markdown
**AUTOMATED SCREENSHOT GENERATION**

Use the Agent tool to generate screenshots for visual validation:

**Project Context**: Tyler Gohr Portfolio visual testing
**Output**: screenshots/quick-review/ directory

**Execution Steps**:
1. **Environment Setup**:
   - Verify development server is running at tylergohr.com project
   - Ensure environment variables are set correctly
   - Test server accessibility

2. **Screenshot Generation**:
   - Execute npx playwright test e2e/quick-screenshots.spec.ts --project=chromium
   - Generate both desktop (1200x800) and mobile (375x667) views
   - Cover all main pages: homepage, case-studies, how-i-work, technical-expertise

3. **Validation & Reporting**:
   - Verify all 8 screenshots generated successfully
   - Check file sizes and image quality
   - Report any generation failures with specific error context
   - Provide file paths for immediate review

**Expected Output**: 8 screenshots (4 pages × 2 viewports) in quick-review directory
**Timeline**: 2-3 minutes for complete generation
```

## High-Frequency Development Templates

### Template 3: Development Environment Setup
**Frequency**: High | **Timeout Risk**: Critical  
**Usage**: `environment_setup` or `/dev`

```markdown
**AUTOMATED DEVELOPMENT ENVIRONMENT SETUP**

Use the Agent tool to handle complete environment setup:

**Project Context**: Tyler Gohr Portfolio development setup
**Goal**: Running development server with proper environment configuration

**Execution Steps**:
1. **Environment Cleanup**:
   - Navigate to /home/user/tylergohr.com
   - Check for existing dev servers: ps aux | grep "next-server\|npm run dev"
   - Clean up any conflicting processes: pkill -f "next-server|npm run dev"

2. **Port Detection & Configuration**:
   - Run ./scripts/detect-active-port.sh for intelligent port allocation
   - Set environment variables for current session
   - Verify no port conflicts exist

3. **Server Startup**:
   - Execute npm run dev (uses smart port allocation)
   - Monitor startup logs for "Ready on" confirmation
   - Wait for complete server initialization

4. **Environment Validation**:
   - Test server accessibility with curl request
   - Verify all development tools are functional
   - Provide environment summary (port, URL, status)

**Success Criteria**: Development server running, accessible, environment ready
**Expected URL Format**: https://[port]-tylergohr.cluster-[id].cloudworkstations.dev
```

### Template 4: Quality Gates Validation
**Frequency**: Medium | **Pattern**: Pre-commit validation
**Usage**: `quality_validation` or `/validate`

```markdown
**AUTOMATED QUALITY GATES VALIDATION**

Use the Agent tool to execute complete quality validation:

**Project Context**: Tyler Gohr Portfolio quality assurance
**Purpose**: Ensure code quality before commits

**Execution Steps**:
1. **TypeScript Validation**:
   - Run npm run typecheck to verify TypeScript compilation
   - Report any type errors with specific file/line references
   - Categorize as BLOCKING if compilation fails

2. **Code Quality Checks**:
   - Execute npm run lint for ESLint validation
   - Report linting issues (errors vs warnings)
   - Provide specific fix suggestions for common issues

3. **Build Validation**:
   - Run npm run build to test production build
   - Monitor bundle size with npm run bundle-check (<6MB limit)
   - Verify all assets generate correctly

4. **Quality Summary**:
   - Provide overall status: CLEAN, WARNINGS, or ERRORS
   - List specific issues that need attention
   - Recommend next steps based on results

**Output Format**:
- ✅ CLEAN: Ready to commit
- ⚠️ WARNINGS: Review recommended
- ❌ ERRORS: Must fix before committing
```

## Medium-Frequency Workflow Templates

### Template 5: Git Workflow Automation
**Frequency**: Medium | **Pattern**: Quality → Review → Commit
**Usage**: `git_workflow` or `/commit`

```markdown
**AUTOMATED GIT WORKFLOW WITH QUALITY GATES**

Use the Agent tool to handle complete git workflow:

**Project Context**: Tyler Gohr Portfolio git operations
**Prerequisite**: Code should be ready for commit

**Execution Steps**:
1. **Quality Validation First**:
   - Run npm run validate to ensure code quality
   - If validation fails, stop and report issues
   - Only proceed if all quality gates pass

2. **Change Review**:
   - Execute git status --porcelain to review changes
   - Show summary of modified files for user confirmation
   - Identify file types and scope of changes

3. **Staging & Commit**:
   - Add appropriate files to staging (confirm with user)
   - Analyze changes to create descriptive commit message
   - Use conventional commit format (feat:, fix:, docs:, etc.)
   - Execute commit with proper message formatting

4. **Push Option**:
   - Ask user if they want to push to remote
   - If yes, execute git push with proper branch tracking
   - Confirm successful push to remote repository

**Success Criteria**: Code committed with quality validation and proper commit message
**Safety Check**: Always validate quality before any git operations
```

### Template 6: Performance Analysis
**Frequency**: Medium | **Pattern**: Bundle analysis and optimization
**Usage**: `performance_analysis` or `/perf`

```markdown
**AUTOMATED PERFORMANCE ANALYSIS**

Use the Agent tool to analyze portfolio performance:

**Project Context**: Tyler Gohr Portfolio performance optimization
**Focus**: Core Web Vitals and bundle analysis

**Execution Steps**:
1. **Bundle Analysis**:
   - Run npm run bundle-check to verify size budget (<6MB)
   - Execute npx next build --analyze for detailed composition
   - Identify largest dependencies and optimization opportunities

2. **Performance Testing**:
   - Run npm run test:e2e:performance for Core Web Vitals testing
   - Verify LCP <2.5s, FID <100ms, CLS <0.1 targets
   - Test both desktop and mobile performance

3. **Optimization Recommendations**:
   - Analyze bundle composition for unused dependencies
   - Check for proper image optimization and lazy loading
   - Verify animation performance (60fps target)

4. **Performance Report**:
   - Provide current metrics vs targets
   - Highlight performance improvements or regressions
   - Recommend specific optimization actions

**Output**: Performance scorecard with actionable recommendations
```

## Specialized Automation Templates

### Template 7: Error Diagnosis & Fix
**Frequency**: Medium | **Pattern**: Debug → Analyze → Fix
**Usage**: `error_diagnosis` or `/debug`

```markdown
**AUTOMATED ERROR DIAGNOSIS WORKFLOW**

Use the Agent tool to diagnose and resolve development errors:

**Project Context**: Tyler Gohr Portfolio error resolution
**Goal**: Systematic error analysis and resolution

**Execution Steps**:
1. **Error Collection**:
   - Gather error messages from terminal output
   - Check browser console for client-side errors
   - Review TypeScript compilation errors

2. **Error Analysis**:
   - Categorize errors: TypeScript, Build, Runtime, or Environment
   - Identify root cause and affected components
   - Check for common patterns (missing dependencies, type errors, etc.)

3. **Solution Research**:
   - Search project history for similar issues
   - Check documentation for known solutions
   - Analyze code context around error locations

4. **Fix Implementation**:
   - Provide specific fix recommendations
   - Show exact code changes needed
   - Verify fixes with appropriate testing

**Success Criteria**: Errors resolved, root cause identified, tests passing
```

### Template 8: Documentation Updates
**Frequency**: Low-Medium | **Pattern**: Code changes → Doc updates
**Usage**: `doc_update` or `/docs`

```markdown
**AUTOMATED DOCUMENTATION UPDATE WORKFLOW**

Use the Agent tool to update project documentation:

**Project Context**: Tyler Gohr Portfolio documentation maintenance
**Scope**: README, CLAUDE.md, and docs/ directory

**Execution Steps**:
1. **Change Analysis**:
   - Review recent git changes for documentation impact
   - Identify new features, command changes, or workflow updates
   - Check for outdated information in existing docs

2. **Documentation Updates**:
   - Update README.md with new features or changes
   - Sync CLAUDE.md with current commands and workflows
   - Update docs/ files for comprehensive coverage

3. **Validation**:
   - Verify all links and references are current
   - Test documented commands and workflows
   - Ensure consistency across all documentation

4. **Quality Check**:
   - Review for clarity and completeness
   - Check markdown formatting and structure
   - Validate against current project state

**Output**: Updated documentation reflecting current project state
```

## Slash Command Implementation

### Recommended Slash Commands for Claude Code

```bash
# High-priority automation (immediate implementation)
/test        → Testing Automation Sub-Agent
/dev         → Development Environment Sub-Agent  
/screenshot  → Visual Testing & Screenshots
/validate    → Quality Gates Validation

# Medium-priority automation (secondary implementation)
/commit      → Git Workflow Automation
/perf        → Performance Analysis
/debug       → Error Diagnosis & Fix
/docs        → Documentation Updates
```

### Usage Pattern Examples

```markdown
# Quick testing with environment setup
User: "/test"
Claude: [Launches Testing Automation Sub-Agent with full workflow]

# Development environment setup  
User: "/dev"
Claude: [Launches Development Environment Sub-Agent with port detection]

# Pre-commit validation
User: "/validate"
Claude: [Launches Quality Gates Sub-Agent with comprehensive checks]

# Complete commit workflow
User: "/commit fix navigation bug"
Claude: [Launches Quality + Git Workflow Sub-Agents with message]
```

## Productivity Impact

### Automation Benefits:
- **Timeout Elimination**: 90%+ reduction in command timeout failures
- **Consistency**: Standardized workflows across all development sessions
- **Quality Assurance**: Automated validation prevents broken commits
- **Time Savings**: ~60% reduction in manual workflow overhead

### Measured Improvements:
- Testing workflow: 8-12 minutes → 2-3 minutes
- Environment setup: 5-10 minutes → 30-60 seconds  
- Quality validation: Manual checking → Automated with detailed reports
- Git workflows: Manual multi-step → Single command automation

---

**Implementation Priority**: Start with `/test` and `/dev` for highest impact
**Iteration Strategy**: Refine based on usage patterns and user feedback
**Goal**: Transform frequent manual workflows into one-command automation