<<<<<<< HEAD
# Hirefy
=======
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
# Employment Verification Agent

An AI-powered verification system that automates employment verification and reference checking using phone calls (ElevenLabs conversational AI) and email.

This repository contains a CLI and core modules to:
- Initiate HR verification calls
- Initiate reference calls
- Send verification emails and run live AI-assisted email conversations

See the Quickstart section below to run the CLI or wire a small API.

---

## Quickstart

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and fill in your keys.

3. Run a sample HR verification call (use test numbers):

```bash
python main.py hr --candidate "Test User" --job-title "Engineer" --start-date "2020-01-01" --end-date "2020-12-31" --phone "+15550100"
```

4. For emails, use the `email-hr` and `email-reference` commands; for live AI-assisted email conversations use `live-email-hr` and `live-email-reference`.

---

## Project Layout

- `main.py` - CLI entrypoint
- `src/core/` - Clients and orchestrators (ElevenLabs, email, models)
- `src/handlers/` - Call handlers for HR and references
- `src/utils/` - Transcript and template managers
- `templates/` - Email templates

---

For full documentation see the `docs/` folder and the inline README sections in `workstream-3-wave-plan.md`.

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
>>>>>>> cleanup
