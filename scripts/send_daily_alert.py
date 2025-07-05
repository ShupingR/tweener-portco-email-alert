import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

def send_email_alert():
    # Load credentials from environment variables
    gmail_user = os.environ.get('GMAIL_USERNAME')
    gmail_password = os.environ.get('GMAIL_PASSWORD')
    to_email = 'shuping@tweenerfund.com'
    
    if not gmail_user or not gmail_password:
        raise Exception('GMAIL_USERNAME and GMAIL_PASSWORD must be set as environment variables.')
    
    subject = 'Tweener Daily Job Ran'
    body = f"""
Hello Shuping,

This is an automated alert to confirm that the Tweener scheduled job ran successfully at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.

Best,
Tweener Automation
"""
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = gmail_user
    msg['To'] = to_email
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(gmail_user, gmail_password)
            server.sendmail(gmail_user, [to_email], msg.as_string())
        print('Email sent successfully!')
    except Exception as e:
        print(f'Failed to send email: {e}')
        raise

def main(request=None):
    """Entry point for Google Cloud Function"""
    send_email_alert()
    return 'Daily alert sent.'

if __name__ == '__main__':
    send_email_alert() 