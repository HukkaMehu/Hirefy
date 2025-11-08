# Design Document

## Overview

The Email Messaging System extends the Employment Verification Agent by adding email communication capabilities as an alternative to phone calls. The system enables recruiters to send professional verification requests to HR departments and reference contacts via email, with customizable templates for each verification type.

The design integrates seamlessly with the existing Employment Verification Agent architecture, reusing the same data models, transcript storage structure, and CLI patterns. This ensures consistency across communication channels and minimizes learning curve for users.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CLI Interface (main.py)                  │
│  ┌──────────────────┐              ┌──────────────────┐    │
│  │  Phone Commands  │              │  Email Commands  │    │
│  │  (hr/reference)  │              │ (email-hr/email-│    │
│  │                  │              │  reference)      │    │
│  └────────┬─────────┘              └────────┬─────────┘    │
└───────────┼──────────────────────────────────┼──────────────┘
            │                                  │
            ▼                                  ▼
┌───────────────────────┐        ┌──────────────────────────┐
│  CallOrchestrator     │        │  EmailOrchestrator       │
│  (existing)           │        │  (new)                   │
│                       │        │                          │
│  - initiate_hr_call() │        │  - send_hr_email()       │
│  - initiate_ref_call()│        │  - send_reference_email()│
└───────────────────────┘        └────────┬─────────────────┘
                                          │
                    ┌─────────────────────┼─────────────────────┐
                    │                     │                     │
                    ▼                     ▼                     ▼
        ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
        │ EmailClient      │  │ TemplateManager  │  │ EmailLogger      │
        │                  │  │                  │  │                  │
        │ - send_email()   │  │ - load_template()│  │ - log_sent()     │
        │ - validate_addr()│  │ - render()       │  │ - get_history()  │
        └──────────────────┘  └──────────────────┘  └──────────────────┘
                    │                     │                     │
                    └─────────────────────┴─────────────────────┘
                                          │
                                          ▼
                              ┌──────────────────────┐
                              │  Transcript Storage  │
                              │  (existing)          │
                              │                      │
                              │  transcripts/        │
                              │    candidate_name/   │
                              │      - emails.log    │
                              └──────────────────────┘
```

### Component Interaction Flow

**Email Verification Request Flow:**

1. User executes CLI command: `python main.py email-hr --candidate "John Doe" --email "hr@company.com" ...`
2. CLI parser routes to EmailOrchestrator
3. EmailOrchestrator:
   - Validates input parameters
   - Loads appropriate template via TemplateManager
   - Renders template with candidate data
   - Calls EmailClient to send email
   - Logs result via EmailLogger
   - Returns result to CLI
4. CLI displays confirmation or error message

## Components and Interfaces

### 1. EmailOrchestrator

**Purpose:** Coordinates email-based verification requests, similar to CallOrchestrator for phone calls.

**Location:** `src/core/email_orchestrator.py`

**Key Methods:**

```python
class EmailOrchestrator:
    def __init__(self):
        """Initialize with EmailClient, TemplateManager, and EmailLogger."""
        
    def send_hr_verification_email(
        self,
        candidate_name: str,
        job_title: str,
        start_date: str,
        end_date: str,
        hr_email: str
    ) -> EmailResult:
        """
        Send HR verification email requesting employment dates and job title.
        
        Args:
            candidate_name: Full name of candidate
            job_title: Job title to verify
            start_date: Employment start date (YYYY-MM-DD)
            end_date: Employment end date (YYYY-MM-DD)
            hr_email: HR contact email address
            
        Returns:
            EmailResult with success status and details
            
        Raises:
            ValueError: If email address is invalid or dates are malformed
        """
        
    def send_reference_email(
        self,
        candidate_name: str,
        reference_name: str,
        reference_email: str,
        relationship: str
    ) -> EmailResult:
        """
        Send reference check email requesting qualitative feedback.
        
        Args:
            candidate_name: Full name of candidate
            reference_name: Name of reference contact
            reference_email: Reference email address
            relationship: Relationship to candidate (manager/coworker/supervisor)
            
        Returns:
            EmailResult with success status and details
            
        Raises:
            ValueError: If email address is invalid or relationship is not valid
        """
```

**Dependencies:**
- EmailClient (for sending emails)
- TemplateManager (for loading and rendering templates)
- EmailLogger (for logging sent emails)

### 2. EmailClient

**Purpose:** Handles SMTP connection and email sending with proper authentication.

**Location:** `src/core/email_client.py`

**Key Methods:**

```python
class EmailClient:
    def __init__(self):
        """Initialize with SMTP configuration from environment variables."""
        
    def send_email(
        self,
        to_address: str,
        subject: str,
        body: str,
        from_address: str = None
    ) -> bool:
        """
        Send an email via SMTP.
        
        Args:
            to_address: Recipient email address
            subject: Email subject line
            body: Email body content (plain text)
            from_address: Sender email (defaults to configured sender)
            
        Returns:
            True if email sent successfully, False otherwise
            
        Raises:
            SMTPException: If SMTP connection or authentication fails
            ValueError: If email address format is invalid
        """
        
    def validate_email_address(self, email: str) -> bool:
        """
        Validate email address format using regex.
        
        Args:
            email: Email address to validate
            
        Returns:
            True if valid, False otherwise
        """
```

**Configuration (from environment variables):**
- `SMTP_HOST`: SMTP server hostname (e.g., smtp.gmail.com)
- `SMTP_PORT`: SMTP server port (e.g., 587 for TLS)
- `SMTP_USERNAME`: SMTP authentication username
- `SMTP_PASSWORD`: SMTP authentication password
- `SMTP_FROM_EMAIL`: Default sender email address
- `SMTP_FROM_NAME`: Default sender name

**SMTP Provider Support:**
- Gmail (smtp.gmail.com:587)
- Outlook (smtp-mail.outlook.com:587)
- Custom SMTP servers

### 3. TemplateManager

**Purpose:** Loads and renders email templates with candidate-specific data.

**Location:** `src/utils/template_manager.py`

**Key Methods:**

```python
class TemplateManager:
    def __init__(self, template_dir: str = "templates"):
        """Initialize with template directory path."""
        
    def load_template(self, template_name: str) -> str:
        """
        Load email template from file.
        
        Args:
            template_name: Name of template file (without .txt extension)
            
        Returns:
            Template content as string
            
        Raises:
            FileNotFoundError: If template file doesn't exist
        """
        
    def render_template(
        self,
        template_content: str,
        variables: dict
    ) -> str:
        """
        Render template by replacing variables with actual values.
        
        Args:
            template_content: Template string with {variable} placeholders
            variables: Dictionary of variable names to values
            
        Returns:
            Rendered template string
            
        Raises:
            KeyError: If required variable is missing from variables dict
        """
```

**Template Variables:**

HR Verification Template:
- `{candidate_name}`: Candidate's full name
- `{job_title}`: Job title to verify
- `{start_date}`: Employment start date
- `{end_date}`: Employment end date
- `{sender_name}`: Recruiter/sender name
- `{sender_email}`: Recruiter/sender email

Reference Check Template:
- `{candidate_name}`: Candidate's full name
- `{reference_name}`: Reference contact's name
- `{relationship}`: Relationship to candidate
- `{sender_name}`: Recruiter/sender name
- `{sender_email}`: Recruiter/sender email

### 4. EmailLogger

**Purpose:** Logs sent emails for audit trail and tracking.

**Location:** `src/utils/email_logger.py`

**Key Methods:**

```python
class EmailLogger:
    def __init__(self, base_dir: str = "transcripts"):
        """Initialize with base transcript directory."""
        
    def log_sent_email(
        self,
        candidate_name: str,
        email_type: str,
        recipient: str,
        subject: str,
        success: bool,
        error_message: str = None
    ) -> str:
        """
        Log a sent email to the candidate's log file.
        
        Args:
            candidate_name: Candidate's full name
            email_type: Type of email (hr_verification or reference_check)
            recipient: Email recipient address
            subject: Email subject line
            success: Whether email was sent successfully
            error_message: Error message if send failed
            
        Returns:
            Path to log file
        """
        
    def get_email_history(self, candidate_name: str) -> list:
        """
        Retrieve email history for a candidate.
        
        Args:
            candidate_name: Candidate's full name
            
        Returns:
            List of email log entries
        """
```

**Log File Format:**

```
=== EMAIL LOG ===
Candidate: John Doe

[2024-11-08 14:30:00]
Type: HR Verification
Recipient: hr@company.com
Subject: Employment Verification Request for John Doe
Status: SENT
---

[2024-11-08 15:00:00]
Type: Reference Check
Recipient: manager@company.com
Subject: Reference Request for John Doe
Status: SENT
---
```

## Data Models

### EmailResult

**Purpose:** Represents the result of an email send operation.

**Location:** `src/core/models.py` (extend existing models)

```python
@dataclass
class EmailResult:
    """Result of an email send operation.
    
    Attributes:
        success: Whether the email was sent successfully
        email_id: Unique identifier for the email (timestamp-based)
        recipient: Email address of recipient
        log_path: File path where the email was logged
        error_message: Optional error message if send failed
    """
    success: bool
    email_id: str
    recipient: str
    log_path: str
    error_message: Optional[str] = None
    
    def __post_init__(self):
        """Validate EmailResult data integrity."""
        if not isinstance(self.success, bool):
            raise TypeError("success must be a boolean")
        
        if not self.email_id or not isinstance(self.email_id, str):
            raise ValueError("email_id must be a non-empty string")
        
        if not self.recipient or not isinstance(self.recipient, str):
            raise ValueError("recipient must be a non-empty string")
        
        if not self.log_path or not isinstance(self.log_path, str):
            raise ValueError("log_path must be a non-empty string")
        
        if self.error_message is not None and not isinstance(self.error_message, str):
            raise TypeError("error_message must be a string or None")
```

## Email Templates

### Template Storage

Templates are stored as plain text files in the `templates/` directory:

```
templates/
├── hr_verification.txt
└── reference_check.txt
```

### HR Verification Template

**File:** `templates/hr_verification.txt`

```
Subject: Employment Verification Request for {candidate_name}

Dear HR Team,

I am writing to verify employment information for {candidate_name}, who has listed your organization as a previous employer.

Could you please confirm the following details:

- Employee Name: {candidate_name}
- Job Title: {job_title}
- Employment Start Date: {start_date}
- Employment End Date: {end_date}

Please reply to this email with confirmation of these details or any corrections needed.

Thank you for your assistance with this verification request.

Best regards,
{sender_name}
{sender_email}
```

### Reference Check Template

**File:** `templates/reference_check.txt`

```
Subject: Reference Request for {candidate_name}

Dear {reference_name},

I hope this email finds you well. I am reaching out regarding {candidate_name}, who has listed you as a professional reference in their capacity as their {relationship}.

I would greatly appreciate your feedback on the following:

1. Can you confirm your working relationship with {candidate_name}?
2. What were {candidate_name}'s primary responsibilities in their role?
3. How would you describe their work quality and performance?
4. What strengths did {candidate_name} demonstrate in their work?
5. How would you describe their ability to work with team members?
6. Would you recommend {candidate_name} for future employment?

Please feel free to provide any additional insights you think would be helpful.

You can reply directly to this email with your feedback. Thank you for taking the time to provide this reference.

Best regards,
{sender_name}
{sender_email}
```

## Error Handling

### Email Validation Errors

**Scenario:** Invalid email address format

**Handling:**
- Validate email using regex pattern before sending
- Raise `ValueError` with descriptive message
- Display error to user via CLI
- Do not attempt to send email

### SMTP Connection Errors

**Scenario:** Cannot connect to SMTP server

**Handling:**
- Catch `SMTPException` from email client
- Log error with full details
- Return `EmailResult` with `success=False` and error message
- Display user-friendly error message suggesting configuration check

### SMTP Authentication Errors

**Scenario:** Invalid SMTP credentials

**Handling:**
- Catch authentication exceptions during SMTP login
- Log error without exposing credentials
- Return failure result with generic authentication error message
- Suggest user verify SMTP credentials in `.env` file

### Template Errors

**Scenario:** Template file not found or missing variables

**Handling:**
- Raise `FileNotFoundError` if template doesn't exist
- Raise `KeyError` if required variable is missing
- Display clear error message indicating which template or variable is missing
- Provide guidance on template location and format

### Missing Configuration

**Scenario:** Required environment variables not set

**Handling:**
- Validate configuration at EmailClient initialization
- Raise `ValueError` with list of missing variables
- Display error message with instructions to configure `.env` file
- Prevent email sending until configuration is complete

## Testing Strategy

### Unit Tests

**EmailClient Tests:**
- Test email address validation with valid and invalid formats
- Test SMTP connection with mock SMTP server
- Test authentication with valid and invalid credentials
- Test email sending with various content types

**TemplateManager Tests:**
- Test template loading from files
- Test template rendering with complete variable sets
- Test error handling for missing templates
- Test error handling for missing variables

**EmailLogger Tests:**
- Test log file creation and appending
- Test log entry formatting
- Test candidate directory creation
- Test email history retrieval

**EmailOrchestrator Tests:**
- Test HR verification email flow end-to-end
- Test reference check email flow end-to-end
- Test input validation for all parameters
- Test error propagation from dependencies

### Integration Tests

**End-to-End Email Flow:**
- Test complete HR verification email send with real SMTP (test account)
- Test complete reference check email send
- Verify log files are created correctly
- Verify email content matches templates

**CLI Integration:**
- Test CLI commands for email-hr and email-reference
- Test parameter parsing and validation
- Test output formatting and error messages

### Manual Testing

**SMTP Provider Testing:**
- Test with Gmail SMTP
- Test with Outlook SMTP
- Test with custom SMTP server
- Verify emails are received and formatted correctly

**Template Testing:**
- Send test emails and verify formatting
- Check that all variables are replaced correctly
- Verify professional appearance and tone

## Security Considerations

### Credential Storage

- All SMTP credentials stored in environment variables
- Never log or display passwords in error messages
- Use `.env` file with `.gitignore` to prevent credential commits
- Support for app-specific passwords (Gmail, Outlook)

### Email Content

- Sanitize all user input before including in emails
- Prevent email injection attacks via header validation
- Use plain text emails to avoid HTML injection risks
- Validate all email addresses before sending

### Logging

- Log email metadata but not full content
- Avoid logging sensitive information
- Store logs with appropriate file permissions
- Provide option to disable logging if needed

## Performance Considerations

### SMTP Connection Pooling

- Reuse SMTP connection for multiple emails in same session
- Close connections properly after use
- Implement connection timeout handling

### Template Caching

- Load templates once and cache in memory
- Avoid repeated file I/O for same templates
- Clear cache if templates are modified

### Async Considerations (Future Enhancement)

- Current implementation is synchronous (sufficient for hackathon)
- Future: Consider async email sending for bulk operations
- Future: Implement email queue for retry logic

## Integration with Existing System

### CLI Extension

Add new subcommands to `main.py`:

```python
# Email HR Verification subcommand
email_hr_parser = subparsers.add_parser('email-hr', help='Send HR verification email')
email_hr_parser.add_argument('--candidate', required=True)
email_hr_parser.add_argument('--job-title', required=True)
email_hr_parser.add_argument('--start-date', required=True)
email_hr_parser.add_argument('--end-date', required=True)
email_hr_parser.add_argument('--email', required=True, help='HR contact email address')

# Email Reference subcommand
email_ref_parser = subparsers.add_parser('email-reference', help='Send reference check email')
email_ref_parser.add_argument('--candidate', required=True)
email_ref_parser.add_argument('--reference-name', required=True)
email_ref_parser.add_argument('--email', required=True, help='Reference email address')
email_ref_parser.add_argument('--relationship', required=True, choices=['manager', 'coworker', 'supervisor'])
```

### Shared Components

- Reuse existing transcript directory structure
- Reuse existing data validation patterns
- Reuse existing CLI output formatting
- Maintain consistency with phone call interface

### Environment Configuration

Extend `.env.example` with SMTP settings:

```env
# SMTP Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_FROM_EMAIL=your_email@gmail.com
SMTP_FROM_NAME=Your Name
```

## Future Enhancements

### Phase 2 (Post-Hackathon)

- Email response monitoring and parsing
- Automated follow-up reminders
- HTML email templates with better formatting
- Attachment support for verification forms
- Email tracking (open rates, click rates)

### Phase 3 (Advanced Features)

- WhatsApp Business API integration
- LinkedIn messaging integration
- Multi-channel orchestration (try email, then phone, etc.)
- Response analytics and reporting
- Integration with ATS (Applicant Tracking Systems)
