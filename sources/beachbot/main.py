import os
import logging
from dotenv import load_dotenv

from .surf_report import SurfReportService
from .communication import EmailSender


logger = logging.getLogger(__name__)

def main():
    load_dotenv()

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        filename='run.log',
        filemode='w'
    )
            
    logger.info("Starting Surf Report Service")
    logger.info(f"using browser: {os.environ.get('browser')}")
    service = SurfReportService(
        logger=logger,
        url=os.environ.get('SCRAPPER_URL'),
        station_number=os.environ.get('STATION_NUMBER'),
        browser=os.environ.get('BROWSER'),
        headless=os.environ.get('HEADLESS'),
        model =os.environ.get('MODEL')
    )
    logger.info("Service init: OK")
    report = service.generate_surf_report()
    logger.info("Starting Mail Service")
    email_config = {
        'smtp_server': os.environ.get('SMTPSERVER'),
        'smtp_port': os.environ.get('SMTPORT'),
        'sender_email': os.environ.get('SENDEREMAIL'),
        'receivers_emails': os.environ.get('SENDEREMAIL'),
        'password': os.environ.get('EMAILPASSWORD'),
    }
    sender= EmailSender(**email_config, logger=logger)
    sender.send_email("Surf Report", report)
    
if __name__ == '__main__':
    main()