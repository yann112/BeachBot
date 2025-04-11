import logging
import smtplib
from email.mime.text import MIMEText

class EmailSender:
    def __init__(
            self,
            smtp_server,
            smtp_port,
            sender_email,
            receiver_email,
            password,
            logger=None
                ):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.receiver_email = receiver_email
        self.password = password
        self.logger = logger or logging.getLogger(__name__)

    def send_email(self, subject, body):
        """Sends an email with the given subject and body."""
        try:
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = self.sender_email
            msg['To'] = self.receiver_email

            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.sender_email, self.password)
                server.sendmail(self.sender_email, [self.receiver_email], msg.as_string())
            self.logger.info(f"Email sent successfully to {self.receiver_email} with subject: {subject}")
            return True
        except Exception as e:
            self.logger.error(f"Error sending email to {self.receiver_email} with subject '{subject}': {e}")
            return False

if __name__ == "__main__":
    # Example usage: Replace with your actual email credentials
    email_config = {
        'smtp_server': 'your_smtp_server.com',  # Replace with your SMTP server
        'smtp_port': 465,                      # Replace with your SMTP port (e.g., 465 for SSL)
        'sender_email': 'your_email@example.com',    # Replace with your sender email
        'receiver_email': 'recipient@example.com', # Replace with your recipient email
        'password': 'your_email_password'        # Replace with your email password
    }

