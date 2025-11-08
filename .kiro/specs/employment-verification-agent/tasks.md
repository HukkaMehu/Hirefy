# Implementation Plan

- [x] 1. Set up project structure and dependencies





  - Create Python project directory structure with folders for core modules, handlers, and utilities
  - Create requirements.txt with elevenlabs SDK and python-dotenv dependencies
  - Create .env.example file with placeholder environment variables for API keys and configuration
  - Create main entry point script (main.py) with basic CLI argument parsing
  - _Requirements: 3.1, 3.2_

- [x] 2. Implement data models and core types





  - Create data models file (models.py) with CallResult, ConversationConfig, and CallTranscript dataclasses
  - Add type hints and validation logic to ensure data integrity
  - _Requirements: 3.2, 4.3_
-

- [x] 3. Build ElevenLabs client wrapper




  - Create ElevenLabsClient class that initializes the ElevenLabs SDK with API key
  - Implement start_conversation method to initiate phone calls using conversational AI API
  - Implement get_conversation_transcript method to retrieve call transcripts after completion
  - Add error handling for API connection failures and invalid responses
  - _Requirements: 1.1, 6.1, 6.4_

- [x] 4. Implement transcript management system





  - Create TranscriptManager class with save_transcript and format_transcript methods
  - Implement directory structure creation (transcripts/candidate_name/)
  - Implement transcript formatting with metadata header and conversation body
  - Generate filenames with call type and timestamp (e.g., hr_verification_2024-11-08_14-30-00.txt)
  - _Requirements: 1.4, 2.4, 4.2, 4.3, 4.4_

- [x] 5. Build HR verification call handler





  - Create HRVerificationHandler class with build_conversation_config method
  - Define HR verification conversation flow with introduction and structured questions
  - Implement execute_call method that uses ElevenLabsClient to place the call
  - Configure questions to ask about employment dates, job title, and employment confirmation
  - Return CallTranscript with complete conversation data
  - _Requirements: 1.1, 1.2, 1.3, 6.2, 6.3_

- [x] 6. Build reference call handler





  - Create ReferenceCallHandler class with build_conversation_config method
  - Define reference call conversation flow with introduction and structured questions
  - Implement execute_call method that uses ElevenLabsClient to place the call
  - Configure questions about projects, skills, motivation, performance, promotions, and areas for improvement
  - Return CallTranscript with complete conversation data
  - _Requirements: 2.1, 2.2, 2.3, 6.2, 6.3_

- [x] 7. Implement call orchestrator





  - Create CallOrchestrator class as main coordination layer
  - Implement initiate_hr_verification method with input validation
  - Implement initiate_reference_call method with input validation
  - Add routing logic to delegate to appropriate handler (HR or Reference)
  - Integrate TranscriptManager to save call results
  - Return CallResult with success status and transcript file path
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 4.1_

- [x] 8. Create CLI interface





  - Implement command-line argument parsing for call type selection (hr or reference)
  - Add arguments for candidate information (name, job title, dates)
  - Add arguments for contact information (phone number, reference name, relationship)
  - Implement call initiation logic that invokes CallOrchestrator
  - Display call status and transcript file path to user
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [x] 9. Add error handling and timeout management





  - Implement timeout configuration in ConversationConfig (10-minute maximum)
  - Add try-catch blocks for API errors in ElevenLabsClient
  - Implement graceful call termination when recipient requests to end call
  - Add logging for failed calls and partial transcripts
  - _Requirements: 1.5, 6.5_

- [x] 10. Create setup documentation





  - Write README.md with project overview and setup instructions
  - Document ElevenLabs account setup and agent configuration requirements
  - Provide example commands for running HR verification and reference calls
  - Include troubleshooting section for common issues
  - _Requirements: 6.1_

- [ ]* 11. Manual testing and validation
  - Test HR verification call with a test phone number
  - Test reference call with a test phone number
  - Verify transcript files are created with correct format and content
  - Validate conversation flows sound natural and complete
  - Test error scenarios (invalid phone, API failures)
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 2.4, 4.2, 4.3, 4.4_
