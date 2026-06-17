# Gmail API Setup Guide

This guide will help you set up Gmail API credentials to enable email reading functionality in the AI Executive Assistant.

## Prerequisites

- Google Account
- Access to Google Cloud Console

## Step-by-Step Setup

### 1. Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top
3. Click "New Project"
4. Enter a project name (e.g., "AI Executive Assistant")
5. Click "Create"

### 2. Enable Gmail API

1. In the Google Cloud Console, select your project
2. Go to "APIs & Services" > "Library"
3. Search for "Gmail API"
4. Click on "Gmail API"
5. Click "Enable"

### 3. Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. If prompted, configure the OAuth consent screen:
   - Choose "External" user type
   - Fill in the required fields:
     - App name: "AI Executive Assistant"
     - User support email: Your email
     - Developer contact: Your email
   - Click "Save and Continue"
   - Skip "Scopes" (click "Save and Continue")
   - Add test users (your email address)
   - Click "Save and Continue"

4. Back to "Create OAuth client ID":
   - Application type: "Desktop app"
   - Name: "AI Executive Assistant Desktop"
   - Click "Create"

5. Download the credentials:
   - Click "Download JSON" on the credentials you just created
   - Save the file as `credentials.json` in your project root directory

### 4. Project Structure

Your project root should now have:

```
AI_Executive_Assistant/
├── credentials.json    ← Place your downloaded credentials here
├── .env
├── main.py
├── app.py
└── ...
```

### 5. First Run Authentication

When you run the application for the first time:

1. Run: `python main.py`
2. A browser window will open automatically
3. Sign in with your Google account
4. Grant the requested permissions (read-only access to Gmail)
5. The browser will show "The authentication flow has completed"
6. A `token.pickle` file will be created to store your authentication

### 6. Security Notes

⚠️ **Important Security Information:**

- **credentials.json**: Contains your OAuth client credentials
  - Keep this file secure and private
  - Already added to `.gitignore`
  - Never commit to version control

- **token.pickle**: Contains your access token
  - Keep this file secure and private
  - Already added to `.gitignore`
  - Never commit to version control

- **Scopes**: The application requests read-only access to Gmail
  - Scope: `https://www.googleapis.com/auth/gmail.readonly`
  - Cannot send, delete, or modify emails

### 7. Troubleshooting

#### Error: "credentials.json not found"

- Ensure you've downloaded the credentials file
- Verify it's named exactly `credentials.json`
- Place it in the project root directory (same folder as main.py)

#### Error: "Access blocked: This app's request is invalid"

- Make sure you've added your email as a test user in OAuth consent screen
- Verify the OAuth consent screen is properly configured

#### Error: "The user has not granted the app..."

- Complete the OAuth flow in the browser
- Grant all requested permissions
- Try running the application again

#### Token Expired

- Delete `token.pickle`
- Run the application again to re-authenticate

### 8. Testing

After setup, test the email reader:

```bash
# Activate virtual environment
.venv\Scripts\activate

# Run the application
python main.py
```

You should see:

- System initialization messages
- "Fetching recent emails from Gmail..."
- List of your recent emails with details

## API Quotas

Gmail API has the following quotas (as of 2024):

- 1 billion quota units per day
- Reading a message costs 5 quota units
- Listing messages costs 5 quota units

For typical usage (reading a few emails), you won't hit these limits.

## Additional Resources

- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [OAuth 2.0 for Desktop Apps](https://developers.google.com/identity/protocols/oauth2/native-app)
- [Gmail API Python Quickstart](https://developers.google.com/gmail/api/quickstart/python)

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review the error messages in the console
3. Verify all setup steps were completed
4. Check that credentials.json is in the correct location
