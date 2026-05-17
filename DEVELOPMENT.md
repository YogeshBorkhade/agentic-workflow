# Development Guide

## Branch Strategy

This project uses **individual feature branches** for clear, focused development.

### Why Individual Branches?

Each feature branch shows ONLY that feature's work:
- feature/research-agent → Shows ONLY research agent commits
- feature/validator-agent → Shows ONLY validator commits
- Clean, focused, easy to review

### Available Tools

#### Git Branch Reorganization
```bash
python tools/git/organize_branches.py
```

This script:
- Creates individual feature branches
- Each branch shows only its commits
- Perfect for portfolio showcase
- See docs/development/branch_strategy.md for details

### Branch List

- feature/foundation - Core infrastructure (config, logging, errors)
- feature/data-layer - Data abstraction layer
- feature/clarity-agent - ClarityAgent implementation
- feature/orchestration - LangGraph orchestration
- feature/research-agent - ResearchAgent implementation
- feature/validator-agent - ValidatorAgent with retry logic
- feature/synthesis-agent - SynthesisAgent formatting
- feature/pipeline-integration - Complete agent pipeline
- feature/groq-integration - Groq LLM testing
- feature/deployment - Deployment configuration

### Working with Feature Branches

```bash
# View a specific feature
git checkout feature/research-agent
git log --oneline

# Compare features
git diff feature/clarity-agent feature/research-agent

# Return to main
git checkout master
```

## Development Workflow

1. Clone repository
2. Choose a feature to work on
3. Make changes
4. Merge to master

## Documentation

- README.md - Project overview
- DEVELOPMENT.md - This file
- docs/development/branch_strategy.md - Detailed branch strategy
- tools/git/ - Git organization scripts
