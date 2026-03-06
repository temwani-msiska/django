import logging
import os

logger = logging.getLogger(__name__)

RESEND_API_KEY = os.environ.get('RESEND_API_KEY', '')
FROM_EMAIL = 'noreply@codesheros.co.zm'
CONFIRM_BASE_URL = os.environ.get('CONFIRM_EMAIL_BASE_URL', 'https://codesheros.co.zm/confirm-email')


def send_verification_email(user):
    """Send a verification email to the parent user via Resend."""
    if not RESEND_API_KEY:
        logger.warning('RESEND_API_KEY not set — skipping verification email for %s', user.email)
        return False

    import resend

    resend.api_key = RESEND_API_KEY
    confirm_url = f'{CONFIRM_BASE_URL}?token={user.confirmation_token}'
    name = getattr(user, 'name', '') or user.email

    html_body = f"""\
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family: Arial, sans-serif; background: #f5f0ff; padding: 40px 0;">
  <div style="max-width: 480px; margin: 0 auto; background: #fff; border-radius: 16px; padding: 40px; text-align: center;">
    <h1 style="color: #7c3aed; font-size: 24px;">Welcome to Code SHEROs!</h1>
    <p style="color: #374151; font-size: 16px; line-height: 1.6;">
      Hi {name},<br><br>
      Thanks for signing up! Please verify your email address so your young SHERO can start their coding adventure.
    </p>
    <a href="{confirm_url}"
       style="display: inline-block; margin: 24px 0; padding: 16px 40px;
              background: #7c3aed; color: #fff; font-size: 18px; font-weight: bold;
              text-decoration: none; border-radius: 12px;">
      Verify My Email
    </a>
    <p style="color: #9ca3af; font-size: 13px;">
      This link expires in 24 hours.<br>
      If you didn't create this account, you can safely ignore this email.
    </p>
  </div>
</body>
</html>"""

    try:
        resend.Emails.send({
            'from': FROM_EMAIL,
            'to': [user.email],
            'subject': 'Verify your Code SHEROs account',
            'html': html_body,
        })
        return True
    except Exception:
        logger.exception('Failed to send verification email to %s', user.email)
        return False
