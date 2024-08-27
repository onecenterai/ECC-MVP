from typing import Optional

from langchain.tools import BaseTool, GmailSendMessage
from langchain.callbacks.manager import CallbackManagerForToolRun


from . import send_notification

import os
from dotenv import load_dotenv

load_dotenv()

class SendEmergencyNotification(BaseTool):
    name = 'send_emergency_notification'
    description = f'Useful when you need to send an emergency notification to a government agency.'

    def _run(self, *args, run_manager: Optional[CallbackManagerForToolRun]=None, **kwargs) -> dict:
        emergency_email_mapping = {'Fire Service':os.getenv('FIRE_SERVICE_EMAIL'), 
                                   'Emergency Health Care Service':os.getenv('HEALTH_CARE_EMAIL'),
                                   'Police':os.getenv('POLICE_EMAIL')}
        
        agencies = kwargs.get('agency-names')
        target_emails = [emergency_email_mapping.get(service) for service in agencies]
        target_emails = send_notification.Email(email=target_emails)
        location = kwargs.get('location')
        emergency_name = kwargs.get('emergency-name')
        res = send_notification.send_mail(target_emails, location, emergency_name, agencies)

        return res
