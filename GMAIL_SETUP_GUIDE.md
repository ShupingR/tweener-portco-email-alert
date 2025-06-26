# Gmail API Setup Guide for update@tweenerfund.com

This guide will help you connect the email tracker to `update@tweenerfund.com` using Gmail API.

## Prerequisites

✅ **Already completed:**
- Python packages installed
- Database with portfolio companies and contacts
- Gmail setup script created

## Step 1: Google Cloud Console Setup

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/
   - Log in with the Google account that has access to `update@tweenerfund.com`

2. **Create or Select Project**
   - Click "Select a project" at the top
   - Either create a new project or select existing "Tweener Fund" project
   - Recommended name: "Tweener Fund Email Tracker"

3. **Enable Gmail API**
   - Go to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click on "Gmail API" and click "Enable"

4. **Create OAuth 2.0 Credentials**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client IDs"
   - If prompted, configure OAuth consent screen:
     - Choose "External" user type
     - Fill in app name: "Tweener Fund Email Tracker"
     - Add your email as developer contact
     - Add scopes: `../auth/gmail.readonly` and `../auth/gmail.send`
   - For Application type, choose "Desktop application"
   - Name it: "Email Tracker Desktop"
   - Click "Create"

5. **Download Credentials**
   - Click the download button (⬇️) next to your new OAuth 2.0 Client ID
   - Save the file as `credentials.json` in the email-alert directory
   - **Important:** Keep this file secure and never commit it to version control

## Step 2: Run Setup Script

Once you have `credentials.json` in the project directory:

```bash
python setup_gmail.py
```

This will:
- Check for credentials.json
- Open a browser for OAuth authentication
- **IMPORTANT:** Make sure to log in with `update@tweenerfund.com`
- Test the connection
- Search for existing emails from portfolio companies

## Step 3: Authentication Flow

When the script runs:

1. **Browser will open** - Don't panic, this is normal
2. **Choose the correct account** - Select `update@tweenerfund.com`
3. **Grant permissions** - Allow the app to read Gmail
4. **Browser will show success** - You can close the browser tab
5. **Script will continue** - It will test the connection

## Step 4: Verify Setup

The script will show:
- ✅ Connected email address (should be update@tweenerfund.com)
- 📊 Total messages in inbox
- 🔍 Search results for portfolio company emails

## Step 5: Run Email Ingestion

After successful setup:

```bash
python gmail_ingest.py
```

This will:
- Connect to update@tweenerfund.com
- Search for emails from all 138 portfolio company contacts
- Extract and store email content, attachments, and dates
- Show progress and results

## Troubleshooting

### Issue: "credentials.json not found"
- Make sure you downloaded the credentials file from Google Cloud Console
- Rename it to exactly `credentials.json`
- Place it in the email-alert directory

### Issue: "Wrong email address connected"
- Delete `token.json` file
- Run `python setup_gmail.py` again
- Make sure to select `update@tweenerfund.com` in the browser

### Issue: "No emails found from portfolio companies"
- Check if portfolio companies are actually sending to update@tweenerfund.com
- They might be sending to a different email address
- Check Gmail spam/promotions folders
- Verify contact email addresses in the database

### Issue: "Permission denied" or "Scope errors"
- Make sure you granted all requested permissions
- Check that Gmail API is enabled in Google Cloud Console
- Verify OAuth consent screen is properly configured

## Security Notes

- `credentials.json` contains sensitive information - keep it secure
- `token.json` will be created after authentication - also keep secure
- Never commit these files to version control
- Consider using environment variables for production deployment

## Next Steps

After successful Gmail setup:

1. **Test email ingestion** - Run the ingestion script
2. **Set up scheduling** - Automate email checking (daily/hourly)
3. **Configure alerts** - Set up the reminder system
4. **Create dashboard** - Build monitoring interface

## Files Created

- `credentials.json` - OAuth credentials (you download this)
- `token.json` - Authentication token (automatically created)
- `setup_gmail.py` - Setup script
- `gmail_ingest.py` - Email ingestion script

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify all steps were followed correctly
3. Check Google Cloud Console for API quotas/limits
4. Ensure update@tweenerfund.com has proper access permissions 