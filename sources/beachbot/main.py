from pathlib import Path
from .surf_report import SurfReportService
import os
from dotenv import load_dotenv

from sources.beachbot.communication import EmailSender

def main():
    load_dotenv()
    
    service = SurfReportService(
        config_path=os.environ.get('SCRAPPER_CONFIG'),
        url=os.environ.get('TEST_URL'),
        station_number=os.environ.get('STATION_NUMBER'),
        browser=os.environ.get('browser'),
        headless=os.environ.get('headless'),
        model =os.environ.get('model')
    )

    report = service.generate_surf_report()

    email_config = {
        'smtp_server': os.environ.get('SMTPSERVER'),
        'smtp_port': os.environ.get('SMTPORT'),
        'sender_email': os.environ.get('SENDEREMAIL'),
        'receivers_emails': os.environ.get('SENDEREMAIL'),
        'password': os.environ.get('EMAILPASSWORD'),
    }
    sender= EmailSender(**email_config)
    sender.send_email("Surf Report", report)
    
if __name__ == '__main__':
    main()