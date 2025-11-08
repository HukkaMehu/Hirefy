# AGENTS.md - AI Agent Guidelines for Hackathon Ideation Workspace

## Project Overview
This is a documentation workspace for AGENTIC ERA hackathon (Helsinki, Nov 2025). Focus: generating winning multi-agent AI startup ideas that solve $50B+ B2B problems and are fundable by Nordic VCs.

## Architecture
- **Core Framework**: idea-generation-validation-prompt.md (master template)
- **Research Outputs**: Individual idea documents (*-ai-idea.md) and due diligence reports (*-due-diligence-report.md)
- **Format**: Markdown documentation only (no code yet)

## Content Style Guidelines
- **Validation First**: Always validate ideas against 6 filters (greenfield, market size, pain intensity, agentic fit, demo viability, VC fundability)
- **Data-Driven**: Include specific numbers ($XB TAM, X customers, Y hours saved, % market growth)
- **Structure**: Use the output template from idea-generation-validation-prompt.md (Problem → Solution → Market → Competition → Demo)
- **Scoring**: Rate ideas 1-10 using weighted rubric (9.0+ = build, <6.0 = pass)
- **Red Flags**: Skip crowded markets (5+ funded competitors), creator economy, pure cost-cutting, platform-dependent ideas

## Workflow Commands
No build/test/lint commands (documentation workspace). For new ideas, use the validation framework in idea-generation-validation-prompt.md.

## Naming Conventions
- Idea files: `[topic]-ai-idea.md`
- Research files: `[topic]-due-diligence-report.md`
- Use descriptive hyphenated lowercase names

## Key Constraints
- B2B SaaS focus ($50k-500k ACV)
- Multi-agent systems (4-7 agents coordinating)
- Greenfield markets (no AI-native competitors)
- 90-second demo viability
- $100M+ outcome potential
