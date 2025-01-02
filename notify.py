import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class Notification:
    def __init__(self, sender_email=None, sender_password=None, smtp_server=None, smtp_port=587, recipient_email=None):
        self.sender_email = os.getenv('SENDER_EMAIL') if sender_email is None else sender_email
        self.sender_password = os.getenv('SENDER_PASSWORD') if sender_password is None else sender_password
        self.smtp_server = os.getenv('SMTP_SERVER') if smtp_server is None else smtp_server
        self.smtp_port = int(os.getenv('SMTP_PORT', 587)) if smtp_port is None else smtp_port
        self.recipient_email = os.getenv('RECIPIENT_EMAIL') if recipient_email is None else recipient_email
        
    def send_email(self, subject, body):
        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = self.recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()  # 启动 TLS 加密
            server.login(self.sender_email, self.sender_password)
            text = msg.as_string()
            server.sendmail(self.sender_email, self.recipient_email, text)
            server.quit()
            print(f"Email sent to {self.recipient_email}")
        except Exception as e:
            print(f"Failed to send email: {str(e)}")


if __name__ == "__main__":
    notification = Notification()
    notification.send_email("Test Email", "This is a test email sent from Server.")