# Sub-Agent Workflow Designs for Productivity Optimization

## Overview

Based on conversation analytics, this document provides specific sub-agent workflows designed to automate your most common development patterns and eliminate timeout issues.

## High-Priority Sub-Agent Workflows

### 1. Testing Automation Sub-Agent
**Priority**: HIGH | **Frequency**: Very High | **Timeout Risk**: Critical

**Trigger Patterns**: `test:e2e`, `playwright`, `screenshot`, `e2e`, `smoke tests`

**Automated Workflow**:
```
Use the Agent tool to execute comprehensive testing workflow:

**Context**: Tyler Gohr Portfolio testing with tylergohr.com project
**Environment**: Cloud Workstations with port auto-detection

**Tasks**:
1. Navigate to /home/user/tylergohr.com project directory
2. Detect active development server using ./scripts/detect-active-port.sh
3. Set environment variables: eval "$(./scripts/detect-active-port.sh quiet export)"
4. Verify server accessibility with curl test
5. Execute npm run test:e2e:smoke for essential validation
6. If screenshots requested: npx playwright test e2e/quick-screenshots.spec.ts --project=chromium
7. Check screenshots/quick-review/ directory for generated files
8. Handle any Framer Motion animation timing issues
9. Provide detailed analysis of failures with specific error context
10. Recommend next steps based on results

**Success Criteria**: Tests pass without timeout, screenshots generated successfully
**Fallback**: If timeout occurs, restart with environment reset
```

### 2. Development Environment Sub-Agent  
**Priority**: HIGH | **Frequency**: High | **Timeout Risk**: Critical

**Trigger Patterns**: `npm run dev`, `server`, `environment`, `port`, `development setup`

**Automated Workflow**:
```
Use the Agent tool to handle complete environment setup:

**Context**: Tyler Gohr Portfolio development environment
**Environment**: Google Cloud Workstations with smart port allocation

**Tasks**:
1. Navigate to /home/user/tylergohr.com project directory
2. Check for existing dev servers: ps aux | grep "next-server\|npm run dev"
3. Kill conflicting servers if found: pkill -f "next-server|npm run dev"
4. Run port detection: ./scripts/detect-active-port.sh
5. Set environment variables for current session
6. Start development server: npm run dev (with smart port allocation)
7. Wait for server startup (monitor for "Ready on" message)
8. Verify server accessibility with health check
9. Test environment with quick curl request
10. Provide environment summary (port, URL, status)

**Success Criteria**: Dev server running, accessible, environment variables set
**Fallback**: Try alternative ports if conflicts detected
```

## Medium-Priority Sub-Agent Workflows

### 3. Quality Gates Automation Sub-Agent
**Priority**: MEDIUM | **Frequency**: Medium | **Pattern**: Pre-commit validation

**Trigger Patterns**: `validate`, `typecheck`, `lint`, `quality`, `before commit`

**Automated Workflow**:
```
Use the Agent tool to execute quality validation workflow:

**Context**: Tyler Gohr Portfolio quality assurance
**Goal**: Ensure code quality before commits

**Tasks**:
1. Navigate to /home/user/tylergohr.com project directory
2. Run TypeScript validation: npm run typecheck
3. Execute code quality checks: npm run lint
4. Test production build: npm run build
5. Check bundle size: npm run bundle-check (verify <6MB limit)
6. Analyze results and categorize issues:
   - CLEAN: All checks pass, ready to commit
   - ERRORS: TypeScript/build errors that must be fixed
   - WARNINGS: Lint warnings that should be addressed
7. Provide summary of quality gate status
8. Recommend specific next steps based on results
9. If clean: suggest commit workflow
10. If errors: provide specific error context and fixes needed

**Success Criteria**: Quality status determined, actionable recommendations provided
**Output Format**: Clear PASS/FAIL with specific next steps
```

### 4. Git Workflow Automation Sub-Agent
**Priority**: MEDIUM | **Frequency**: Medium | **Pattern**: Quality → Review → Commit

**Trigger Patterns**: `commit`, `git`, `push`, `workflow`, `git add`

**Automated Workflow**:
```
Use the Agent tool to handle complete git workflow:

**Context**: Tyler Gohr Portfolio git operations with quality gates
**Prerequisite**: Quality validation should be run first

**Tasks**:
1. Navigate to /home/user/tylergohr.com project directory
2. Run quality gates first: npm run validate
3. If quality fails, stop and report issues
4. If quality passes, continue with git workflow:
5. Check git status and review changes: git status --porcelain
6. Show changed files summary for user review
7. Add appropriate files to staging (user confirmation)
8. Analyze changes to create descriptive commit message following conventions
9. Execute commit with proper conventional format
10. Ask user if they want to push to remote
11. If yes, execute git push with branch tracking

**Success Criteria**: Code committed with quality validation, proper commit message
**Safety**: Always validate quality before committing
```

## Slash Command Automation Ideas

### /test - Quick Testing Command
```markdown
**Purpose**: Automated testing workflow with environment setup
**Implementation**: Launches Testing Automation Sub-Agent

**Flow**:
1. Auto-detects if in tylergohr.com project
2. Launches testing sub-agent with environment validation
3. Executes smoke tests automatically  
4. Generates screenshots if visual review needed
5. Reports results with next steps

**Usage**: Simply type `/test` in Claude Code
```

### /dev - Development Setup Command
```markdown
**Purpose**: Automated development environment setup
**Implementation**: Launches Development Environment Sub-Agent

**Flow**:
1. Auto-detects project context
2. Handles port conflicts and server cleanup
3. Starts development server with proper configuration
4. Validates environment health
5. Provides environment summary

**Usage**: Simply type `/dev` in Claude Code
```

### /commit - Commit Workflow Command  
```markdown
**Purpose**: Automated commit workflow with quality gates
**Implementation**: Launches Quality Gates + Git Workflow Sub-Agents sequentially

**Flow**:
1. Runs quality validation first
2. If quality passes, proceeds with git workflow
3. Reviews changes with user
4. Creates proper commit message
5. Offers to push to remote

**Usage**: Simply type `/commit` in Claude Code
```

### /screenshot - Visual Testing Command
```markdown
**Purpose**: Automated screenshot generation for visual review  
**Implementation**: Launches Testing Sub-Agent focused on screenshots

**Flow**:
1. Validates environment and server status
2. Generates desktop and mobile screenshots
3. Saves to screenshots/quick-review/ directory
4. Reports generation status with file paths
5. Offers immediate visual analysis

**Usage**: Simply type `/screenshot` in Claude Code
```

## Implementation Strategy

### Phase 1: Core Sub-Agent Templates
1. **Testing Automation Sub-Agent** - Highest ROI due to timeout frequency
2. **Development Environment Sub-Agent** - Critical for cloud environments

### Phase 2: Workflow Integration  
1. **Quality Gates Automation Sub-Agent** - Streamlines pre-commit process
2. **Git Workflow Automation Sub-Agent** - Completes development cycle

### Phase 3: Slash Command Creation
1. Create Claude Code slash commands using sub-agent templates
2. Test with tylergohr.com project workflows
3. Refine based on usage patterns

## Productivity Benefits

### Measured Improvements Expected:
- **Timeout Elimination**: 90%+ reduction in 2-minute timeout failures
- **Context Switching**: Reduced manual environment setup by ~80%
- **Quality Assurance**: Automated validation prevents broken commits
- **Workflow Consistency**: Standardized processes across sessions

### Key Automation Patterns:
1. **Environment-First Approach**: Always validate environment before executing commands
2. **Quality Gates Integration**: Never commit without validation
3. **Intelligent Fallbacks**: Handle timeouts and errors gracefully
4. **Context Preservation**: Maintain project context across sub-agent executions

## Next Steps

1. **Test High-Priority Sub-Agents**: Start with Testing and Development Environment workflows
2. **Create Slash Commands**: Implement `/test` and `/dev` for immediate productivity gains  
3. **Measure Impact**: Track timeout reduction and workflow efficiency
4. **Iterate and Expand**: Add additional sub-agents based on usage patterns

---

**Focus**: Eliminate timeouts, automate repetitive workflows, maintain quality standards
**Target**: 80%+ reduction in manual development workflow overhead
**Benefit**: Seamless development experience with intelligent automation