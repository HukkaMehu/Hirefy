# Demo Scenarios for AI-Powered Recruitment Verification Platform

This directory contains three complete demo scenarios to test the end-to-end verification flow.

## Scenarios

### 1. Green Scenario - Sarah Chen (Clean Candidate)
- **Risk Score**: GREEN
- **Profile**: Senior Software Engineer with verified employment, strong GitHub presence, positive references
- **Test Focus**: Happy path, all verifications pass, no fraud flags

### 2. Yellow Scenario - Michael Rodriguez (Minor Concerns)
- **Risk Score**: YELLOW  
- **Profile**: Mid-level developer with employment gap, moderate GitHub activity, mixed references
- **Test Focus**: Employment gap handling, partial verification, minor inconsistencies

### 3. Red Scenario - David Thompson (Major Flags)
- **Risk Score**: RED
- **Profile**: Candidate with timeline conflicts, unverifiable credentials, GitHub activity mismatch
- **Test Focus**: Fraud detection, timeline conflicts, technical misrepresentation

## Running the Demos

```bash
# Run the complete end-to-end demo
python demo_end_to_end.py

# Run individual scenario tests
python demo_end_to_end.py --scenario green
python demo_end_to_end.py --scenario yellow
python demo_end_to_end.py --scenario red
```

## Test Coverage

Each scenario tests:
- Document upload and processing
- Conversational clarification flow
- Employment verification
- Reference checks
- GitHub analysis
- Fraud detection
- Report generation
- UI interactions
