import smtplib
from email.message import EmailMessage

from config.settings import app_settings


def send():
    msg = EmailMessage()
    msg["Subject"] = "Testing Python SMTP"
    msg["From"] = app_settings.SENDER_EMAIL
    msg["To"] = app_settings.RECIPIENT_EMAIL
    msg.set_content("Hello! This message was sent securely using Python's smtplib.")

    # 3. Connect to the server and send the email
    try:
        with smtplib.SMTP(app_settings.SMTP_SERVER, app_settings.SMTP_PORT) as server:
            server.login(app_settings.SENDER_EMAIL, app_settings.SENDER_PASSWORD)
            server.send_message(msg)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")


send()
