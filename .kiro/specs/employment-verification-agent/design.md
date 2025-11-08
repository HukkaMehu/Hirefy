# Design Document: Employment Verification Agent

## Overview

The Employment Verification Agent is a Python-based application that leverages ElevenLabs' Conversational AI API to conduct automated phone calls for employment verification. The system supports two distinct call types: HR verification calls (factual employment data) and reference calls (qualitative performance feedback). The architecture is designed for rapid prototyping with a focus on core functionality.

### Key Design Decisions

1. **ElevenLabs Conversational AI**: Using ElevenLabs' conversational AI API (not just text-to-speech) to enable real-time, interactive phone conversations with dynamic response handling
2. **Python Implementation**: Python provides excellent SDK support for ElevenLabs and simplifies rapid development
3. **Simple File-Based Storage**: Transcripts saved as .txt files in organized directories - no database needed for MVP
4. **Synchronous Processing**: Calls handled one at a time to simplify implementation and debugging during hackathon
5. **Configuration-Based Call Scripts**: Predefined question templates for HR and reference calls, customizable per call type

## Architecture

### High-Level Architecture

```
┌─────────────────┐
│   User Input    │
│  (CLI/Script)   │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│   Call Orchestrator             │
│  - Validates input              │
│  - Routes to call type handler  │
│  - Manages call lifecycle       │
└────────┬────────────────────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌─────────┐ ┌──────────────┐
│   HR    │ │  Reference   │
│ Handler │ │   Handler    │
└────┬────┘ └──────┬───────┘
     │             │
     └──────┬──────┘
            ▼
┌────────────────────────────┐
│  ElevenLabs Client         │
│  - Initiates phone call    │
│  - Streams conversation    │
│  - Captures responses      │
└────────┬───────────────────┘
         │
         ▼
┌────────────────────────────┐
│  Transcript Manager        │
│  - Formats conversation    │
│  - Saves to .txt file      │
│  - Organizes by candidate  │
└────────────────────────────┘
```

## Components and Interfaces

### 1. Call Orchestrator

**Responsibility**: Main entry point that coordinates the entire verification process

**Interface**:
```python
class CallOrchestrator:
    def initiate_hr_verification(
        self,
        candidate_name: str,
        job_title: str,
        start_date: str,
        end_date: str,
        hr_phone: str
    ) -> CallResult
    
    def initiate_reference_call(
        self,
        candidate_name: str,
        reference_name: str,
        reference_phone: str,
        relationship: str  # "manager", "coworker", "supervisor"
    ) -> CallResult
```

**Key Methods**:
- Input validation
- Call type routing
- Result aggregation

### 2. HR Verification Handler

**Responsibility**: Manages HR verification call flow and question sequence

**Interface**:
```python
class HRVerificationHandler:
    def build_conversation_config(
        self,
        candidate_name: str,
        job_title: str,
        start_date: str,
        end_date: str
    ) -> ConversationConfig
    
    def execute_call(
        self,
        phone_number: str,
        config: ConversationConfig
    ) -> CallTranscript
```

**Conversation Flow**:
1. Introduction: "Hello, this is an automated employment verification call regarding [Candidate Name]"
2. Ask: "Can you confirm if [Candidate Name] worked at your organization?"
3. Ask: "What was their official job title?"
4. Ask: "What were their employment start and end dates?"
5. Closing: "Thank you for your time"

### 3. Reference Call Handler

**Responsibility**: Manages reference call flow with structured questions

**Interface**:
```python
class ReferenceCallHandler:
    def build_conversation_config(
        self,
        candidate_name: str,
        reference_name: str,
        relationship: str
    ) -> ConversationConfig
    
    def execute_call(
        self,
        phone_number: str,
        config: ConversationConfig
    ) -> CallTranscript
```

**Conversation Flow**:
1. Introduction: "Hello [Reference Name], this is an automated reference check call for [Candidate Name]"
2. Ask: "What projects did [Candidate Name] work on during their time with you?"
3. Ask: "What programming languages or technical skills did they use?"
4. Ask: "Can you describe their motivation and work ethic?"
5. Ask: "How would you rate their overall performance?"
6. Ask: "Did they receive any promotions or recognition?"
7. Ask: "What areas could they improve in?"
8. Closing: "Thank you for your valuable feedback"

### 4. ElevenLabs Client

**Responsibility**: Interfaces with ElevenLabs Conversational AI API for phone calls

**Interface**:
```python
class ElevenLabsClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = ElevenLabs(api_key=api_key)
    
    def start_conversation(
        self,
        phone_number: str,
        agent_id: str,
        conversation_config: dict
    ) -> ConversationSession
    
    def get_conversation_transcript(
        self,
        conversation_id: str
    ) -> str
```

**Key Features**:
- Uses ElevenLabs' conversational AI agents (pre-configured with voice and behavior)
- Handles real-time phone call initiation
- Streams conversation and captures responses
- Retrieves full transcript after call completion

### 5. Transcript Manager

**Responsibility**: Formats and persists call transcripts

**Interface**:
```python
class TranscriptManager:
    def save_transcript(
        self,
        candidate_name: str,
        call_type: str,  # "hr_verification" or "reference"
        transcript: str,
        metadata: dict
    ) -> str  # Returns file path
    
    def format_transcript(
        self,
        raw_transcript: str,
        metadata: dict
    ) -> str
```

**File Structure**:
```
transcripts/
├── john_doe/
│   ├── hr_verification_2024-11-08_14-30-00.txt
│   └── reference_manager_2024-11-08_15-00-00.txt
└── jane_smith/
    ├── hr_verification_2024-11-08_16-00-00.txt
    └── reference_coworker_2024-11-08_16-30-00.txt
```

**Transcript Format**:
```
=== EMPLOYMENT VERIFICATION CALL ===
Candidate: John Doe
Call Type: HR Verification
Date: 2024-11-08 14:30:00
Duration: 3m 45s
Contact: +1-555-0100

--- CONVERSATION ---

[Agent]: Hello, this is an automated employment verification call regarding John Doe...

[HR Rep]: Yes, how can I help you?

[Agent]: Can you confirm if John Doe worked at your organization?

[HR Rep]: Yes, he did work here.

...

--- END CONVERSATION ---
```

## Data Models

### CallResult
```python
@dataclass
class CallResult:
    success: bool
    call_id: str
    transcript_path: str
    duration_seconds: int
    error_message: Optional[str] = None
```

### ConversationConfig
```python
@dataclass
class ConversationConfig:
    agent_id: str  # ElevenLabs agent ID
    first_message: str
    questions: List[str]
    max_duration_seconds: int = 600  # 10 minutes
```

### CallTranscript
```python
@dataclass
class CallTranscript:
    conversation_id: str
    raw_transcript: str
    start_time: datetime
    end_time: datetime
    participant_phone: str
```

## Error Handling

### Connection Failures
- If phone call fails to connect, log error and return CallResult with success=False
- No automatic retries in MVP (can be added post-hackathon)

### API Errors
- Catch ElevenLabs API exceptions and wrap in custom VerificationError
- Log full error details for debugging
- Return user-friendly error message

### Timeout Handling
- Set 10-minute maximum call duration in conversation config
- ElevenLabs API will automatically terminate call after timeout
- Save partial transcript if available

### Invalid Input
- Validate phone numbers (basic format check)
- Validate required fields are non-empty
- Raise ValueError with clear message for invalid input

## Testing Strategy

### Manual Testing
- Test HR verification call with a test phone number
- Test reference call with a test phone number
- Verify transcript files are created correctly
- Validate conversation flow sounds natural

### Integration Testing
- Test ElevenLabs API connection with valid credentials
- Test phone call initiation and completion
- Test transcript retrieval and saving

### Edge Cases to Test
- Call recipient hangs up early
- Call goes to voicemail
- Invalid phone number format
- Missing required parameters

## Configuration

### Environment Variables
```
ELEVENLABS_API_KEY=<your_api_key>
ELEVENLABS_HR_AGENT_ID=<agent_id_for_hr_calls>
ELEVENLABS_REFERENCE_AGENT_ID=<agent_id_for_reference_calls>
TRANSCRIPT_OUTPUT_DIR=./transcripts
```

### ElevenLabs Agent Setup
Two conversational AI agents need to be pre-configured in ElevenLabs dashboard:
1. **HR Verification Agent**: Professional, concise, focused on factual data collection
2. **Reference Call Agent**: Friendly, conversational, designed to elicit detailed responses

## Dependencies

- `elevenlabs` - Official ElevenLabs Python SDK
- `python-dotenv` - Environment variable management
- `dataclasses` - Data structure definitions (built-in Python 3.7+)
- `datetime` - Timestamp handling (built-in)

## Implementation Notes

### ElevenLabs Conversational AI Setup
- Requires ElevenLabs account with conversational AI access
- Agents must be created via ElevenLabs dashboard before use
- Each agent needs phone calling capability enabled
- Agent prompts should be configured to follow the conversation flows defined above

### Phone Number Format
- Accept phone numbers in E.164 format: +[country code][number]
- Example: +1-555-0100 for US numbers

### Transcript Parsing for AI Analysis
- Transcripts use clear speaker labels: [Agent] and [HR Rep]/[Reference]
- Each exchange on a new line for easy parsing
- Metadata section at top for context
- Plain text format compatible with any LLM for analysis

## Future Enhancements (Post-Hackathon)

- Web UI for initiating calls and viewing transcripts
- Automatic retry logic for failed calls
- Real-time call status dashboard
- Structured data extraction from transcripts (JSON output)
- Multi-language support
- Call recording audio files (in addition to transcripts)
- Integration with ATS (Applicant Tracking Systems)
