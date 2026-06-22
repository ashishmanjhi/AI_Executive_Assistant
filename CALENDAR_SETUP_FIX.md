# 🔧 Calendar Integration Setup Fix

## ❌ Problem Identified

The Google Calendar API is **not enabled** in your Google Cloud project (ID: 213370343774).

**Error Message:**

```
Google Calendar API has not been used in project 213370343774 before or it is disabled.
```

## ✅ Solution: Enable Google Calendar API

### Step 1: Enable the Calendar API

Click this direct link to enable the API:
👉 **https://console.developers.google.com/apis/api/calendar-json.googleapis.com/overview?project=213370343774**

Or follow these steps manually:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project (ID: 213370343774)
3. Navigate to **APIs & Services** → **Library**
4. Search for "Google Calendar API"
5. Click on "Google Calendar API"
6. Click the **"ENABLE"** button
7. Wait 2-3 minutes for the changes to propagate

### Step 2: Verify API is Enabled

After enabling, verify by:

1. Go to **APIs & Services** → **Enabled APIs & services**
2. You should see "Google Calendar API" in the list
3. Status should show as "Enabled"

### Step 3: Re-authenticate

After enabling the API:

1. **Delete the old token:**

   ```bash
   del calendar_token.pickle
   ```

   (Or manually delete the file from your project folder)

2. **Run the test script again:**

   ```bash
   python test_calendar_auth.py
   ```

3. **Or use the Streamlit UI:**
   - Refresh the page
   - Go to Calendar section
   - Click "Authenticate with Google Calendar"
   - Complete the OAuth flow

### Step 4: Test Calendar Access

Once authenticated, you should see:

- ✅ Your calendars listed
- ✅ Your upcoming events (including your flight in 3 days)
- ✅ Ability to create new events

## 📋 Current Status

- ✅ Calendar code implementation: **Complete**
- ✅ OAuth credentials: **Present** (credentials.json exists)
- ✅ Authentication flow: **Working**
- ❌ Calendar API: **NOT ENABLED** ← **This is the issue**
- ⏳ Calendar access: **Pending API enablement**

## 🎯 What Happens After Enabling

Once you enable the Google Calendar API:

1. **List Calendars** will show your calendars (currently shows 0)
2. **View Events** will display your flight and other events
3. **Create Events** will work properly
4. **Check Availability** will function correctly
5. **Find Free Time** will show available slots

## 🔍 Why This Happened

Your `credentials.json` file was created for Gmail API access, but the **Google Calendar API** is a separate API that needs to be explicitly enabled in the same Google Cloud project.

## 📞 Need Help?

If you encounter any issues:

1. Make sure you're logged into the correct Google account
2. Verify you have admin access to the Google Cloud project
3. Wait 2-3 minutes after enabling the API
4. Clear browser cache if the console doesn't update

## ⚡ Quick Fix Command

After enabling the API in Google Cloud Console, run:

```bash
# Delete old token
del calendar_token.pickle

# Test authentication
python test_calendar_auth.py
```

You should see:

```
[OK] Found X calendar(s):
   - Your Calendar Name (PRIMARY)
[OK] Found X event(s):
   1. Your Flight Event
      When: 2026-06-25 ...
```

---

**Next Step:** Click the link above to enable the Google Calendar API, then re-authenticate! 🚀
