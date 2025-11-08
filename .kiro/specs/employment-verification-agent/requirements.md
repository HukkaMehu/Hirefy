# Requirements Document

## Introduction

The Employment Verification Agent is an AI-powered phone calling system that automates employment verification and reference checking processes. The system uses ElevenLabs voice AI to conduct two types of verification calls: (1) HR verification calls to confirm employment dates and job titles, and (2) reference calls to managers/coworkers to gather qualitative feedback about the candidate's work performance, skills, and professional conduct. All conversations are recorded and saved as text transcripts for later analysis.

## Glossary

- **Verification Agent**: The AI-powered system that conducts automated phone calls for employment verification
- **ElevenLabs API**: The voice AI service used to generate natural-sounding speech and handle phone conversations
- **HR Verification Call**: A phone call to a company's HR department to verify factual employment information
- **Reference Call**: A phone call to a former manager, coworker, or supervisor to gather qualitative feedback
- **Candidate**: The person whose employment history is being verified
- **Verification Record**: A structured data object containing the candidate's claimed employment information
- **Call Transcript**: A text file containing the complete conversation from a verification or reference call
- **Call Session**: A single phone call interaction from initiation to completion

## Requirements

### Requirement 1

**User Story:** As a hiring manager, I want to verify a candidate's employment history with their previous employer's HR department, so that I can confirm the accuracy of their resume claims.

#### Acceptance Criteria

1. WHEN the user initiates an HR verification call, THE Verification Agent SHALL place a phone call to the provided HR contact number
2. THE Verification Agent SHALL ask the HR representative to confirm the candidate's employment start date, end date, and official job title
3. WHEN the HR representative provides information, THE Verification Agent SHALL capture and structure the response data
4. THE Verification Agent SHALL save the complete call conversation as a text transcript file with .txt extension
5. IF the call cannot be completed within 10 minutes, THEN THE Verification Agent SHALL terminate the call and log the incomplete status

### Requirement 2

**User Story:** As a hiring manager, I want to conduct reference calls with a candidate's former managers or coworkers, so that I can gather insights about their work performance and professional behavior.

#### Acceptance Criteria

1. WHEN the user initiates a reference call, THE Verification Agent SHALL place a phone call to the provided reference contact number
2. THE Verification Agent SHALL ask structured questions about the candidate's work projects, technical skills, marketing initiatives, motivation level, performance quality, promotions received, and areas for improvement
3. WHEN the reference provides responses, THE Verification Agent SHALL capture the complete conversation in real-time
4. THE Verification Agent SHALL save the complete call conversation as a text transcript file with .txt extension
5. THE Verification Agent SHALL structure the transcript to enable AI analysis of the reference's feedback

### Requirement 3

**User Story:** As a system administrator, I want to configure the verification agent with candidate information and contact details, so that the agent can conduct targeted verification calls.

#### Acceptance Criteria

1. THE Verification Agent SHALL accept input parameters including candidate name, job title, employment start date, employment end date, and contact phone number
2. THE Verification Agent SHALL validate that all required parameters are provided before initiating a call
3. WHERE an HR verification call is requested, THE Verification Agent SHALL accept HR department contact information
4. WHERE a reference call is requested, THE Verification Agent SHALL accept reference contact information and relationship type (manager, coworker, or supervisor)
5. THE Verification Agent SHALL store the input parameters for inclusion in the call transcript metadata

### Requirement 4

**User Story:** As a compliance officer, I want all verification calls to be properly documented and stored, so that we maintain records for audit and legal purposes.

#### Acceptance Criteria

1. THE Verification Agent SHALL generate a unique identifier for each Call Session
2. THE Verification Agent SHALL save each Call Transcript with a filename that includes the candidate name, call type, and timestamp
3. THE Verification Agent SHALL include metadata in each Call Transcript including call date, call duration, contact information, and call outcome
4. THE Verification Agent SHALL store all Call Transcripts in a designated directory structure organized by candidate
5. THE Verification Agent SHALL ensure Call Transcripts are saved in plain text format compatible with AI analysis tools

### Requirement 5

**User Story:** As a hiring manager, I want the AI agent to sound natural and professional during calls, so that HR representatives and references are comfortable providing honest information.

#### Acceptance Criteria

1. THE Verification Agent SHALL use ElevenLabs API to generate natural-sounding voice output during calls
2. THE Verification Agent SHALL introduce itself at the beginning of each call with its purpose and the candidate's name
3. THE Verification Agent SHALL handle conversational interruptions and clarification requests from the call recipient
4. THE Verification Agent SHALL maintain a professional and courteous tone throughout the Call Session
5. WHEN the call recipient asks to end the call, THE Verification Agent SHALL politely conclude the conversation and save the partial transcript
