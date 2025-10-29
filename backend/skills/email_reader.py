"""
Email Reader Skill - Gmail OAuth Integration (Skeleton)
Read and send emails using Gmail API.

NOTE: This is a skeleton implementation. To use:
1. Set up Gmail API in Google Cloud Console
2. Download credentials.json
3. First run will trigger OAuth flow and save token.json
"""

import os
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

# Try importing Google API libraries
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    import base64
    GMAIL_API_AVAILABLE = True
except ImportError:
    logger.warning(
        "Google API libraries not installed. "
        "Install with: pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client"
    )
    GMAIL_API_AVAILABLE = False


# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Global service
_gmail_service = None


def _get_credentials():
    """
    Get Gmail API credentials.
    
    Setup steps:
    1. Go to https://console.cloud.google.com/
    2. Create a project
    3. Enable Gmail API
    4. Create OAuth 2.0 credentials (Desktop app)
    5. Download credentials.json and place in project root
    6. First run will open browser for authorization
    7. token.json will be saved for future use
    """
    creds = None
    
    # Token file stores the user's access and refresh tokens
    token_path = "token.json"
    creds_path = "credentials.json"
    
    # Check if we have a token
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    # If no valid credentials, authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Refresh expired token
            creds.refresh(Request())
        else:
            # New authentication
            if not os.path.exists(creds_path):
                raise FileNotFoundError(
                    f"Credentials file not found: {creds_path}\n"
                    "Please download from Google Cloud Console:\n"
                    "https://console.cloud.google.com/apis/credentials"
                )
            
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    
    return creds


def _get_gmail_service():
    """Get or create Gmail API service"""
    global _gmail_service
    
    if _gmail_service is None:
        if not GMAIL_API_AVAILABLE:
            raise ImportError("Gmail API libraries not available")
        
        creds = _get_credentials()
        _gmail_service = build('gmail', 'v1', credentials=creds)
        logger.info("✓ Gmail API service initialized")
    
    return _gmail_service


def read_recent_emails(max_results: int = 10) -> List[Dict]:
    """
    Read recent emails from Gmail.
    
    Args:
        max_results: Maximum number of emails to retrieve
    
    Returns:
        list: Email data
        [
            {
                "subject": "Meeting reminder",
                "from": "person@example.com",
                "date": "2025-10-27",
                "snippet": "Don't forget about...",
                "body": "Full email body..."
            },
            ...
        ]
    """
    if not GMAIL_API_AVAILABLE:
        return [{
            "error": "Gmail API not available",
            "note": "Install with: pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client"
        }]
    
    try:
        service = _get_gmail_service()
        
        # Get list of messages
        results = service.users().messages().list(
            userId='me',
            maxResults=max_results,
            labelIds=['INBOX']
        ).execute()
        
        messages = results.get('messages', [])
        
        if not messages:
            return []
        
        emails = []
        
        # Get details for each message
        for msg in messages:
            try:
                message = service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='full'
                ).execute()
                
                # Extract headers
                headers = message['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                from_email = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')
                
                # Extract body (snippet for now)
                snippet = message.get('snippet', '')
                
                # TODO: Extract full body (requires parsing MIME structure)
                
                emails.append({
                    "id": msg['id'],
                    "subject": subject,
                    "from": from_email,
                    "date": date,
                    "snippet": snippet
                })
            
            except HttpError as e:
                logger.error(f"Error fetching message {msg['id']}: {e}")
        
        logger.info(f"✓ Retrieved {len(emails)} emails")
        
        return emails
    
    except Exception as e:
        logger.error(f"Failed to read emails: {e}")
        return [{
            "error": str(e)
        }]


def summarize_emails(emails: List[Dict]) -> str:
    """
    Summarize a list of emails.
    
    Args:
        emails: List of email dicts from read_recent_emails()
    
    Returns:
        str: Natural language summary
    """
    if not emails:
        return "No emails to summarize."
    
    # Create summary text
    summary_parts = []
    
    for i, email in enumerate(emails[:5]):  # Limit to 5 for now
        if "error" in email:
            continue
        
        summary_parts.append(
            f"{i+1}. From {email['from']}: {email['subject']}\n"
            f"   {email['snippet'][:100]}..."
        )
    
    summary = "Recent emails:\n" + "\n".join(summary_parts)
    
    # TODO: Use Qwen to create a more natural summary
    # from backend.core import qwen_api
    # ai_summary = qwen_api.summarize_text(summary)
    
    return summary


# ============================================================================
# UTILITIES
# ============================================================================

def is_available() -> bool:
    """Check if Gmail API is available"""
    return GMAIL_API_AVAILABLE


def is_authenticated() -> bool:
    """Check if user has authenticated"""
    return os.path.exists("token.json")
