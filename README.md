# Employment Verification Agent

An AI-powered verification system that automates employment verification and reference checking processes using both phone calls (ElevenLabs conversational AI) and email communication.

## Overview

The Employment Verification Agent conducts two types of automated verifications through multiple channels:

1. **HR Verification** - Confirm employment dates, job titles, and factual employment information with HR departments
2. **Reference Checks** - Gather qualitative feedback about work performance, skills, and professional conduct from former managers or coworkers

**Communication Channels:**
- 📞 **Phone Calls** - AI-powered voice conversations using ElevenLabs
- 📧 **Email** - Professional email requests with customizable templates

All interactions are logged and saved as text files for later analysis.

## Features

### Phone Call Features
- 🤖 Natural-sounding AI voice conversations using ElevenLabs
- 📞 Automated phone calls to HR departments and references
- 📝 Complete conversation transcripts saved as text files
- ⏱️ Automatic timeout management (10-minute maximum)
- 💬 Professional, conversational AI agents

### Email Features
- 📧 Professional email templates for HR and reference requests
- ✉️ SMTP support for Gmail, Outlook, and custom servers
- 📋 Customizable email templates with variable substitution
- 📊 Email delivery tracking and audit logs
- 🔒 Secure credential management via environment variables

### General Features
- 🗂️ Organized storage by candidate (transcripts and email logs)
- 🛡️ Input validation and error handling
- 📁 Consistent logging across all communication channels

## Prerequisites

- Python 3.7 or higher
- **For Phone Calls:**
  - ElevenLabs account with Conversational AI access
  - Valid phone numbers in E.164 format (e.g., +1-555-0100)
- **For Email:**
  - SMTP email account (Gmail, Outlook, or custom SMTP server)
  - Valid email addresses for recipients

## Installation

### 1. Clone or Download the Project

```bash
git clone <repository-url>
cd employment-verification-agent
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `elevenlabs` - Official ElevenLabs Python SDK
- `python-dotenv` - Environment variable management

### 3. Set Up Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your configuration:

```env
# ElevenLabs API Configuration (for phone calls)
ELEVENLABS_API_KEY=your_actual_api_key_here

# ElevenLabs Agent IDs (for phone calls)
ELEVENLABS_HR_AGENT_ID=your_hr_agent_id_here
ELEVENLABS_REFERENCE_AGENT_ID=your_reference_agent_id_here

# SMTP Email Configuration (for email functionality)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_FROM_EMAIL=your_email@gmail.com
SMTP_FROM_NAME=Your Name

# Transcript Storage (optional, defaults to ./transcripts)
TRANSCRIPT_OUTPUT_DIR=./transcripts
```

## ElevenLabs Account Setup

### 1. Create an ElevenLabs Account

1. Go to [ElevenLabs](https://elevenlabs.io/)
2. Sign up for an account
3. Ensure you have access to the Conversational AI feature (may require a paid plan)

### 2. Get Your API Key

1. Log in to your ElevenLabs dashboard
2. Navigate to your profile settings
3. Find the API Keys section
4. Copy your API key and add it to your `.env` file

### 3. Create Conversational AI Agents

You need to create two separate agents in the ElevenLabs dashboard:

#### HR Verification Agent

1. Go to the Conversational AI section in your ElevenLabs dashboard
2. Click "Create New Agent"
3. Configure the agent:
   - **Name**: HR Verification Agent
   - **Voice**: Choose a professional, clear voice
   - **Behavior**: Professional, concise, focused on factual data collection
   - **System Prompt**: Configure the agent to ask about employment dates, job titles, and confirmation
   - **Phone Calling**: Enable phone calling capability
4. Save the agent and copy the Agent ID
5. Add the Agent ID to your `.env` file as `ELEVENLABS_HR_AGENT_ID`

#### Reference Call Agent

1. Create another new agent
2. Configure the agent:
   - **Name**: Reference Call Agent
   - **Voice**: Choose a friendly, conversational voice
   - **Behavior**: Friendly, conversational, designed to elicit detailed responses
   - **System Prompt**: Configure the agent to ask about work performance, skills, and professional feedback
   - **Phone Calling**: Enable phone calling capability
3. Save the agent and copy the Agent ID
4. Add the Agent ID to your `.env` file as `ELEVENLABS_REFERENCE_AGENT_ID`

### Agent Configuration Tips

- Use clear, natural-sounding voices
- Configure agents to handle interruptions gracefully
- Set appropriate conversation timeouts
- Test agents with sample calls before production use

## SMTP Email Setup

The email functionality allows you to send verification requests via email as an alternative to phone calls. This section covers how to configure SMTP for popular email providers.

### Gmail SMTP Configuration

Gmail requires an "App Password" for SMTP access when using 2-factor authentication.

#### Step 1: Enable 2-Factor Authentication

1. Go to your Google Account settings: https://myaccount.google.com/
2. Navigate to **Security**
3. Enable **2-Step Verification** if not already enabled

#### Step 2: Generate App Password

1. In Google Account settings, go to **Security**
2. Under "2-Step Verification", find **App passwords**
3. Click **App passwords** (you may need to sign in again)
4. Select **Mail** as the app and **Other** as the device
5. Enter a name like "Employment Verification Agent"
6. Click **Generate**
7. Copy the 16-character password (remove spaces)

#### Step 3: Configure .env File

Add these settings to your `.env` file:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_16_char_app_password
SMTP_FROM_EMAIL=your_email@gmail.com
SMTP_FROM_NAME=Your Name or Company Name
```

**Important Gmail Notes:**
- Use the App Password, NOT your regular Gmail password
- Port 587 uses TLS encryption (recommended)
- Alternative port: 465 (SSL) - requires code modification
- Gmail has sending limits: 500 emails/day for free accounts, 2000/day for Google Workspace

### Outlook/Office 365 SMTP Configuration

Outlook.com and Office 365 support SMTP with your regular account password.

#### Step 1: Verify SMTP Access

1. Log in to your Outlook account
2. Go to **Settings** > **Mail** > **Sync email**
3. Ensure "Let devices and apps use POP" is enabled (this also enables SMTP)

#### Step 2: Configure .env File

Add these settings to your `.env` file:

```env
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USERNAME=your_email@outlook.com
SMTP_PASSWORD=your_outlook_password
SMTP_FROM_EMAIL=your_email@outlook.com
SMTP_FROM_NAME=Your Name or Company Name
```

**For Office 365 / Microsoft 365:**

```env
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
SMTP_USERNAME=your_email@yourdomain.com
SMTP_PASSWORD=your_office365_password
SMTP_FROM_EMAIL=your_email@yourdomain.com
SMTP_FROM_NAME=Your Name or Company Name
```

**Important Outlook Notes:**
- Use your regular account password (no app password needed)
- Port 587 uses STARTTLS encryption
- Outlook.com has sending limits: ~300 emails/day
- Office 365 limits: 10,000 emails/day (varies by plan)

### Custom SMTP Server Configuration

If you're using a custom SMTP server or another email provider:

```env
SMTP_HOST=smtp.yourprovider.com
SMTP_PORT=587
SMTP_USERNAME=your_username
SMTP_PASSWORD=your_password
SMTP_FROM_EMAIL=your_email@yourdomain.com
SMTP_FROM_NAME=Your Name or Company Name
```

**Common SMTP Ports:**
- **587** - STARTTLS (recommended, most compatible)
- **465** - SSL/TLS (requires code modification)
- **25** - Unencrypted (not recommended, often blocked)

### Testing Your SMTP Configuration

After configuring your SMTP settings, test the connection with a simple email:

```bash
python main.py email-hr \
  --candidate "Test User" \
  --job-title "Software Engineer" \
  --start-date "2020-01-15" \
  --end-date "2023-06-30" \
  --email "your_test_email@example.com"
```

If successful, you should see:
```
✓ Email sent successfully to your_test_email@example.com
Email logged to: transcripts/test_user/emails.log
```

## Usage

### HR Verification Call

Verify employment dates and job title with an HR department:

```bash
python main.py hr \
  --candidate "John Doe" \
  --job-title "Software Engineer" \
  --start-date "2020-01-15" \
  --end-date "2023-06-30" \
  --phone "+1-555-0100"
```

**Parameters:**
- `--candidate`: Full name of the candidate
- `--job-title`: Job title to verify
- `--start-date`: Employment start date (YYYY-MM-DD format)
- `--end-date`: Employment end date (YYYY-MM-DD format)
- `--phone`: HR contact phone number in E.164 format

### Reference Call

Conduct a reference check with a former manager or coworker:

```bash
python main.py reference \
  --candidate "Jane Smith" \
  --reference-name "Bob Johnson" \
  --phone "+1-555-0200" \
  --relationship "manager"
```

**Parameters:**
- `--candidate`: Full name of the candidate
- `--reference-name`: Name of the reference contact
- `--phone`: Reference phone number in E.164 format
- `--relationship`: Relationship to candidate (choices: `manager`, `coworker`, `supervisor`)

### Phone Number Format

All phone numbers must be in E.164 format:
- Format: `+[country code][number]`
- US Example: `+1-555-0100` or `+15550100`
- UK Example: `+44-20-7123-4567`

---

## Email Usage

The email functionality provides an alternative to phone calls when email communication is preferred or phone contact is not available.

### HR Verification Email

Send an email to HR requesting employment verification:

```bash
python main.py email-hr \
  --candidate "John Doe" \
  --job-title "Software Engineer" \
  --start-date "2020-01-15" \
  --end-date "2023-06-30" \
  --email "hr@company.com"
```

**Parameters:**
- `--candidate`: Full name of the candidate
- `--job-title`: Job title to verify
- `--start-date`: Employment start date (YYYY-MM-DD format)
- `--end-date`: Employment end date (YYYY-MM-DD format)
- `--email`: HR contact email address

**Email Content:**
The HR verification email includes:
- Professional subject line with candidate name
- Request for confirmation of employment dates and job title
- Specific details to be verified
- Clear instructions for responding
- Your contact information

### Reference Check Email

Send an email to a reference requesting feedback:

```bash
python main.py email-reference \
  --candidate "Jane Smith" \
  --reference-name "Bob Johnson" \
  --email "bob.johnson@company.com" \
  --relationship "manager"
```

**Parameters:**
- `--candidate`: Full name of the candidate
- `--reference-name`: Name of the reference contact
- `--email`: Reference email address
- `--relationship`: Relationship to candidate (choices: `manager`, `coworker`, `supervisor`)

**Email Content:**
The reference check email includes:
- Personalized greeting with reference name
- Context about the candidate and relationship
- Questions about work performance, skills, and teamwork
- Request for qualitative feedback and examples
- Your contact information

### Email Template Customization

Email templates are stored in the `templates/` directory and can be customized to match your organization's tone and requirements.

#### Template Files

- `templates/hr_verification.txt` - HR verification email template
- `templates/reference_check.txt` - Reference check email template

#### Template Variables

Templates use `{variable_name}` syntax for dynamic content replacement.

**HR Verification Template Variables:**
- `{candidate_name}` - Candidate's full name
- `{job_title}` - Job title to verify
- `{start_date}` - Employment start date
- `{end_date}` - Employment end date
- `{sender_name}` - Your name (from SMTP_FROM_NAME)
- `{sender_email}` - Your email (from SMTP_FROM_EMAIL)

**Reference Check Template Variables:**
- `{candidate_name}` - Candidate's full name
- `{reference_name}` - Reference contact's name
- `{relationship}` - Relationship to candidate
- `{sender_name}` - Your name (from SMTP_FROM_NAME)
- `{sender_email}` - Your email (from SMTP_FROM_EMAIL)

#### Customizing Templates

1. Open the template file in a text editor:
   ```bash
   notepad templates/hr_verification.txt
   # or on Mac/Linux:
   nano templates/hr_verification.txt
   ```

2. Edit the content while preserving the `{variable}` placeholders

3. Save the file

4. Test with a sample email to verify formatting

**Example HR Template Customization:**

```
Subject: Employment Verification Request for {candidate_name}

Dear HR Team,

I am writing on behalf of [Your Company Name] to verify employment information for {candidate_name}, who has listed your organization as a previous employer.

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
[Your Company Name]
[Your Phone Number]
```

**Important Notes:**
- Always keep the `{variable}` placeholders intact
- The system will automatically replace them with actual values
- Test templates after making changes
- Keep a backup of original templates before customizing

## Output

### Transcript and Log Files

All communication (phone calls and emails) is saved in the following structure:

```
transcripts/
├── john_doe/
│   ├── hr_verification_2024-11-08_14-30-00.txt    # Phone call transcript
│   ├── reference_manager_2024-11-08_15-00-00.txt  # Phone call transcript
│   └── emails.log                                  # Email log
└── jane_smith/
    ├── hr_verification_2024-11-08_16-00-00.txt    # Phone call transcript
    ├── reference_coworker_2024-11-08_16-30-00.txt # Phone call transcript
    └── emails.log                                  # Email log
```

### Phone Call Transcript Format

Each phone call transcript includes:
- Call metadata (candidate name, call type, date, duration, contact info)
- Complete conversation with speaker labels
- Timestamp information

Example:

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

### Email Log Format

Each candidate's email log (`emails.log`) contains all emails sent for that candidate:

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

**Email Log Fields:**
- **Timestamp**: When the email was sent
- **Type**: HR Verification or Reference Check
- **Recipient**: Email address of recipient
- **Subject**: Email subject line
- **Status**: SENT (success) or FAILED (with error details)

## Troubleshooting

### Issue: "Error initializing call orchestrator"

**Possible Causes:**
- Missing or invalid `.env` file
- Missing required environment variables
- Invalid API key

**Solutions:**
1. Verify `.env` file exists in the project root
2. Check that all required variables are set:
   - `ELEVENLABS_API_KEY`
   - `ELEVENLABS_HR_AGENT_ID`
   - `ELEVENLABS_REFERENCE_AGENT_ID`
3. Verify your API key is valid in the ElevenLabs dashboard
4. Ensure agent IDs are correct and agents exist

### Issue: "Call failed" or API connection errors

**Possible Causes:**
- Invalid phone number format
- ElevenLabs API service issues
- Insufficient API credits
- Agent not configured for phone calling

**Solutions:**
1. Verify phone number is in E.164 format (e.g., `+1-555-0100`)
2. Check your ElevenLabs account status and credits
3. Verify agents have phone calling capability enabled
4. Check ElevenLabs service status
5. Review error message for specific details

### Issue: "Invalid input" errors

**Possible Causes:**
- Missing required command-line arguments
- Invalid date format
- Invalid relationship type

**Solutions:**
1. Ensure all required arguments are provided
2. Use YYYY-MM-DD format for dates (e.g., `2020-01-15`)
3. Use valid relationship types: `manager`, `coworker`, or `supervisor`
4. Run `python main.py hr --help` or `python main.py reference --help` for usage info

### Issue: Call goes to voicemail

**Behavior:**
- The agent will leave a message if voicemail is detected
- Partial transcript will be saved
- Call may be marked as incomplete

**Solutions:**
1. Try calling at different times when recipient is more likely to answer
2. Ensure phone number is correct
3. Consider sending advance notice to recipients

### Issue: Transcript not saved or empty

**Possible Causes:**
- Call ended too quickly
- Permissions issue with transcript directory
- Disk space issue

**Solutions:**
1. Check that `transcripts/` directory exists and is writable
2. Verify sufficient disk space
3. Check console output for specific error messages
4. Ensure call completed successfully (check call duration)

### Issue: Agent sounds unnatural or doesn't follow script

**Possible Causes:**
- Agent not properly configured in ElevenLabs dashboard
- Wrong agent ID in `.env` file
- Agent prompt needs refinement

**Solutions:**
1. Review agent configuration in ElevenLabs dashboard
2. Test agent with sample calls in ElevenLabs interface
3. Refine agent system prompt and behavior settings
4. Verify correct agent ID is being used

### Issue: ModuleNotFoundError

**Error:** `ModuleNotFoundError: No module named 'elevenlabs'` or similar

**Solutions:**
1. Ensure you've installed dependencies: `pip install -r requirements.txt`
2. Verify you're using the correct Python environment
3. If using virtual environment, ensure it's activated

---

## Email Troubleshooting

### Issue: "SMTP authentication failed" or "Username and Password not accepted"

**Possible Causes:**
- Incorrect SMTP username or password
- Using regular password instead of app password (Gmail)
- 2-factor authentication not configured (Gmail)
- SMTP access not enabled (Outlook)

**Solutions for Gmail:**
1. Verify you're using an App Password, not your regular Gmail password
2. Ensure 2-factor authentication is enabled on your Google account
3. Generate a new App Password if the current one isn't working
4. Remove any spaces from the App Password in your `.env` file
5. Verify `SMTP_USERNAME` matches your Gmail address exactly

**Solutions for Outlook:**
1. Verify your Outlook password is correct
2. Check that POP/SMTP access is enabled in Outlook settings
3. Try logging into Outlook webmail to ensure account is active
4. For Office 365, verify you're using the correct SMTP host (`smtp.office365.com`)

**Solutions for Custom SMTP:**
1. Verify SMTP credentials with your email provider
2. Check that SMTP access is enabled for your account
3. Confirm the correct SMTP host and port

### Issue: "Connection refused" or "Could not connect to SMTP server"

**Possible Causes:**
- Incorrect SMTP host or port
- Firewall blocking SMTP connections
- SMTP server temporarily unavailable

**Solutions:**
1. Verify SMTP host is correct:
   - Gmail: `smtp.gmail.com`
   - Outlook: `smtp-mail.outlook.com`
   - Office 365: `smtp.office365.com`
2. Verify SMTP port is `587` (most common for TLS)
3. Check your firewall settings - ensure port 587 is not blocked
4. Try from a different network (some networks block SMTP)
5. Verify your internet connection is working
6. Check if the email provider's SMTP service is operational

### Issue: "Email address validation failed" or "Invalid email address"

**Possible Causes:**
- Email address format is incorrect
- Missing @ symbol or domain
- Extra spaces in email address

**Solutions:**
1. Verify email address format: `user@domain.com`
2. Remove any spaces before or after the email address
3. Ensure the domain has a valid TLD (.com, .org, etc.)
4. Check for typos in the email address
5. Test with a known valid email address first

### Issue: Email sent successfully but not received

**Possible Causes:**
- Email in recipient's spam/junk folder
- Email blocked by recipient's email server
- Incorrect recipient email address
- Sending limits exceeded

**Solutions:**
1. Check recipient's spam/junk folder
2. Ask recipient to whitelist your sender email address
3. Verify recipient email address is correct
4. Check your sent folder in your email account to confirm it was sent
5. Review email content - avoid spam trigger words
6. Verify you haven't exceeded daily sending limits:
   - Gmail free: 500/day
   - Gmail Workspace: 2000/day
   - Outlook.com: ~300/day
   - Office 365: 10,000/day (varies by plan)

### Issue: "Missing SMTP configuration" or "SMTP credentials not found"

**Possible Causes:**
- `.env` file not created or not in project root
- Missing required SMTP environment variables
- Typo in environment variable names

**Solutions:**
1. Verify `.env` file exists in the project root directory
2. Check that all required SMTP variables are set:
   ```env
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your_email@gmail.com
   SMTP_PASSWORD=your_password
   SMTP_FROM_EMAIL=your_email@gmail.com
   SMTP_FROM_NAME=Your Name
   ```
3. Ensure variable names match exactly (case-sensitive)
4. Restart your terminal/command prompt after editing `.env`
5. Verify no extra spaces around `=` signs in `.env` file

### Issue: "Template not found" or "Template variable missing"

**Possible Causes:**
- Template files missing from `templates/` directory
- Template file renamed or moved
- Required variable removed from template

**Solutions:**
1. Verify template files exist:
   - `templates/hr_verification.txt`
   - `templates/reference_check.txt`
2. If templates are missing, restore from the original installation
3. Check that all required variables are present in templates:
   - HR: `{candidate_name}`, `{job_title}`, `{start_date}`, `{end_date}`, `{sender_name}`, `{sender_email}`
   - Reference: `{candidate_name}`, `{reference_name}`, `{relationship}`, `{sender_name}`, `{sender_email}`
4. Ensure variable names use curly braces: `{variable_name}`

### Issue: Email log not created or not updating

**Possible Causes:**
- Permissions issue with transcripts directory
- Disk space full
- Candidate name contains invalid characters

**Solutions:**
1. Verify `transcripts/` directory exists and is writable
2. Check available disk space
3. Ensure candidate name doesn't contain special characters that are invalid for filenames
4. Check console output for specific error messages
5. Try with a simple candidate name (e.g., "Test User")

### Issue: "SSL/TLS error" or "Certificate verification failed"

**Possible Causes:**
- Outdated Python SSL certificates
- Corporate firewall intercepting SSL connections
- System date/time incorrect

**Solutions:**
1. Update Python SSL certificates:
   ```bash
   pip install --upgrade certifi
   ```
2. Verify system date and time are correct
3. If behind corporate firewall, contact IT department
4. Try from a different network to isolate the issue

### Testing Email Configuration

To test your email setup without sending to real contacts:

1. **Test with your own email:**
   ```bash
   python main.py email-hr \
     --candidate "Test User" \
     --job-title "Test Engineer" \
     --start-date "2020-01-01" \
     --end-date "2023-01-01" \
     --email "your_own_email@example.com"
   ```

2. **Check the email log:**
   ```bash
   type transcripts\test_user\emails.log
   # On Mac/Linux: cat transcripts/test_user/emails.log
   ```

3. **Verify email received:**
   - Check your inbox
   - Check spam/junk folder
   - Verify formatting and content

### Getting Help

If you encounter issues not covered here:

1. **For Phone Calls:** Check the ElevenLabs documentation: https://elevenlabs.io/docs
2. **For Email Issues:**
   - Gmail: https://support.google.com/mail/answer/7126229 (SMTP settings)
   - Outlook: https://support.microsoft.com/en-us/office/pop-imap-and-smtp-settings
   - Review error messages carefully - they often contain specific guidance
3. Verify all configuration steps were completed
4. Test with known working credentials first

## Project Structure

```
employment-verification-agent/
├── main.py                          # CLI entry point
├── requirements.txt                 # Python dependencies
├── .env.example                     # Example environment variables
├── .env                            # Your actual environment variables (not in git)
├── README.md                       # This file
├── templates/                      # Email templates
│   ├── hr_verification.txt         # HR verification email template
│   └── reference_check.txt         # Reference check email template
├── src/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── models.py               # Data models (CallResult, EmailResult)
│   │   ├── call_orchestrator.py   # Phone call coordination layer
│   │   ├── email_orchestrator.py  # Email coordination layer
│   │   ├── elevenlabs_client.py   # ElevenLabs API wrapper
│   │   └── email_client.py        # SMTP email client
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── hr_verification_handler.py    # HR call logic
│   │   └── reference_call_handler.py     # Reference call logic
│   └── utils/
│       ├── __init__.py
│       ├── transcript_manager.py   # Phone transcript formatting and storage
│       ├── template_manager.py     # Email template loading and rendering
│       └── email_logger.py         # Email logging and audit trail
└── transcripts/                    # Generated transcripts and logs (created automatically)
    └── [candidate_name]/
        ├── [call_type]_[timestamp].txt   # Phone call transcripts
        └── emails.log                     # Email log
```

## Development

### Running in Development Mode

```bash
# Activate virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py hr --candidate "Test User" --job-title "Engineer" \
  --start-date "2020-01-01" --end-date "2023-01-01" --phone "+1-555-0100"
```

### Testing

For manual testing:
1. Use test phone numbers that you control
2. Verify transcript files are created correctly
3. Review conversation flow for naturalness
4. Test error scenarios (invalid inputs, connection failures)

## Security Considerations

### General Security
- Never commit your `.env` file to version control
- Store transcripts and logs securely with appropriate access controls
- Ensure compliance with data protection regulations (GDPR, CCPA, etc.)

### Phone Call Security
- Keep your ElevenLabs API key secure
- Ensure compliance with recording laws in your jurisdiction
- Obtain consent before recording calls where required
- Be aware of two-party consent states/countries

### Email Security
- Keep SMTP credentials secure - never share or commit to version control
- Use App Passwords for Gmail (never use your main account password)
- Enable 2-factor authentication on email accounts
- Monitor for unauthorized access to your email account
- Be aware of email sending limits to avoid account suspension
- Ensure email content complies with anti-spam regulations (CAN-SPAM Act, etc.)
- Consider using a dedicated email account for verification purposes
- Regularly rotate SMTP passwords/app passwords
- Review email logs for any suspicious activity

## License

[Add your license information here]

## Support

For issues related to:
- **ElevenLabs API**: Contact ElevenLabs support
- **This Application**: [Add your support contact information]

## Acknowledgments

Built with [ElevenLabs](https://elevenlabs.io/) Conversational AI technology.
