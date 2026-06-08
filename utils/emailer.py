import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import config

class EmailNotifier:
    def __init__(self):
        self.smtp_server = config.get("smtp_server", "smtp.gmail.com")
        self.smtp_port = config.get("smtp_port", 587)
        self.sender_email = config.get("sender_email", "")
        self.sender_password = config.get("sender_password", "")
    
    def send_notification(self, to_email, subject, body):
        if not self.sender_email:
            print("Email not configured")
            return False
        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.send_message(msg)
            server.quit()
            return True
        except Exception as e:
            print(f"Email failed: {e}")
            return False