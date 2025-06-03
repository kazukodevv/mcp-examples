#!/usr/bin/env python3

import os
import sys
import webbrowser
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from dotenv import load_dotenv

load_dotenv()

def authenticate_google_calendar():
    """
    Authenticate with Google Calendar API and get refresh token.
    """
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("❌ Missing Google OAuth credentials!")
        print("Please set the following environment variables:")
        print("- GOOGLE_CLIENT_ID")
        print("- GOOGLE_CLIENT_SECRET")
        print("\nYou can get these from: https://console.cloud.google.com/")
        print("\nFor uv users, you can set them with:")
        print("  uv run --env GOOGLE_CLIENT_ID=your_id --env GOOGLE_CLIENT_SECRET=your_secret google-calendar-auth")
        print("\nOr create a .env file:")
        print("  GOOGLE_CLIENT_ID=your_id")
        print("  GOOGLE_CLIENT_SECRET=your_secret")
        sys.exit(1)
    
    # OAuth 2.0 configuration
    scopes = [
        "https://www.googleapis.com/auth/calendar",
        "https://www.googleapis.com/auth/calendar.events",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
        "openid"
    ]
    
    redirect_uri = 'http://localhost:8080'
    
    # Create the OAuth flow
    flow = Flow.from_client_config(
        {
            'web': {
                'client_id': client_id,
                'client_secret': client_secret,
                'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
                'token_uri': 'https://oauth2.googleapis.com/token',
                'redirect_uris': [redirect_uri],
            }
        },
        scopes=scopes
    )
    flow.redirect_uri = redirect_uri
    
    print("🔐 Starting Google Calendar authentication...")
    
    # Get authorization URL
    auth_url, _ = flow.authorization_url(
        access_type='offline',
        prompt='consent',  # Force consent to get refresh token
        include_granted_scopes='true'
    )
    
    print("\n📱 Please visit this URL to authorize the application:")
    print(f"🔗 {auth_url}")
    
    # Try to open browser automatically
    try:
        webbrowser.open(auth_url)
        print("\n🌐 Browser opened automatically.")
    except Exception:
        print("\n❗ Could not open browser automatically.")
        print("Please copy and paste the URL above into your browser.")
    
    # Get authorization code from user
    print("\n⏳ After authorizing, you'll be redirected to a page that may show an error.")
    print("📋 Copy the FULL URL from your browser's address bar and paste it here:")
    
    authorization_response = input("Enter the full redirect URL: ").strip()
    
    if not authorization_response:
        print("❌ No URL provided. Exiting.")
        sys.exit(1)
    
    try:
        # Exchange authorization code for tokens
        flow.fetch_token(authorization_response=authorization_response)
        credentials = flow.credentials
        
        print("\n✅ Authentication successful!")
        
        # Display the tokens
        print("\n📝 Add these to your environment:")
        print(f"GOOGLE_REFRESH_TOKEN={credentials.refresh_token}")
        
        if credentials.token:
            print(f"GOOGLE_ACCESS_TOKEN={credentials.token}")
            print("\n🔑 Note: Access token expires in 1 hour, but refresh token is permanent.")
        
        print("\n💡 For uv users, create a .env file:")
        print(f"GOOGLE_CLIENT_ID={client_id}")
        print(f"GOOGLE_CLIENT_SECRET={client_secret}")
        print(f"GOOGLE_REFRESH_TOKEN={credentials.refresh_token}")
        
        print("\n🎉 Your Google Calendar MCP server is ready to use!")
        print("\nTo run the server with uv:")
        print("  uv run google-calendar-mcp")
        
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        print("\n🔍 Please check:")
        print("- The URL you pasted is complete and correct")
        print("- Your OAuth client is configured properly")
        print("- The redirect URI matches your OAuth client settings")
        sys.exit(1)


def main():
    """Main entry point for the auth script."""
    authenticate_google_calendar()


if __name__ == "__main__":
    main()