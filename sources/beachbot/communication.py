import logging
import smtplib
from email.mime.text import MIMEText
from typing import List, Union

class EmailSender:
    def __init__(
            self,
            smtp_server: str,
            smtp_port: int,
            sender_email: str,
            receivers_emails: Union[str, List[str]],
            password: str,
            logger: logging.Logger | None = None
                ):
        self.smtp_server: str = smtp_server
        self.smtp_port: int = smtp_port
        self.sender_email: str = sender_email
        self.receivers_emails: List[str] = (
            [receivers_emails] if isinstance(receivers_emails, str) else receivers_emails
        )
        self.password: str = password
        self.logger: logging.Logger = logger or logging.getLogger(__name__)

    def send_email(self, subject: str, body: str) -> bool:
        """Sends an email with the given subject and body to all receivers."""
        try:
            msg: MIMEText = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = self.sender_email
            msg['To'] = ', '.join(self.receivers_emails)  # Format receivers for the 'To' header

            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.sender_email, self.password)
                server.sendmail(self.sender_email, self.receivers_emails, msg.as_string())
            self.logger.info(f"Email sent successfully to {', '.join(self.receivers_emails)} with subject: {subject}")
            return True
        except Exception as e:
            self.logger.error(f"Error sending email to {', '.join(self.receivers_emails)} with subject '{subject}': {e}")
            return False

if __name__ == "__main__":
    # Example usage: Replace with your actual email credentials
    email_config: dict[str, Union[str, int, List[str]]] = {
        'smtp_server': 'your_smtp_server.com',  # Replace with your SMTP server
        'smtp_port': 465,                      # Replace with your SMTP port (e.g., 465 for SSL)
        'sender_email': 'your_email@example.com',    # Replace with your sender email
        'receivers_emails': ['recipient1@example.com', 'recipient2@example.org'], # Now a list of recipients
        'password': 'your_email_password'        # Replace with your email password
    }

    email_sender: EmailSender = EmailSender(**email_config)
    subject: str = "Test Email with Multiple Recipients"
    body: str = "This is a test email sent to multiple recipients."
    email_sender.send_email(subject, body)

    # Example with a single receiver (still works)
    single_receiver_config: dict[str, Union[str, int, List[str]]] = {
        'smtp_server': 'your_smtp_server.com',
        'smtp_port': 465,
        'sender_email': 'your_email@example.com',
        'receivers_emails': 'single_recipient@example.net', # Can also be a single string
        'password': 'your_email_password'
    }
    single_email_sender: EmailSender = EmailSender(**single_receiver_config)
    single_email_sender.send_email("Test Single Recipient", "This is a test email to a single recipient.")