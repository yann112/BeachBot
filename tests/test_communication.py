import os
from dotenv import load_dotenv

from sources.beachbot.communication import EmailSender

load_dotenv()

def test_mail_sending():
    email_config = {
        'smtp_server': os.environ.get('SMTPSERVER'),
        'smtp_port': os.environ.get('SMTPORT'),
        'sender_email': os.environ.get('SENDEREMAIL'),
        'receiver_email': os.environ.get('SENDEREMAIL'),
        'password': os.environ.get('EMAILPASSWORD'),
    }
    sender= EmailSender(**email_config)
    assert sender.send_email("1212 It s just a test", "Hello world")
