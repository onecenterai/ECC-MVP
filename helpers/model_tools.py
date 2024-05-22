import re
import json
import requests
from typing import Optional

from langchain.tools import BaseTool, GmailSendMessage
from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun


from . import send_notification

class SendEmergencyNotification(BaseTool):
    name = 'send_emergency_notification'
    description = f'Useful when you need to send an emergency notification to a government agency.'

    def _run(self, run_manager: Optional[CallbackManagerForToolRun]=None, *args, **kwargs) -> dict:
        emergency_email_mapping = {'Fire Service':'jesuobohgift@gmail.com', 
                                   'Emergency Health Care Service':'jesuobohgift@gmail.com',
                                   'Police':'jesuobohgift@gmail.com'}

        target_emails = [emergency_email_mapping.get(service) for service in kwargs.get('agency-names')]
        print(1)
        target_emails = send_notification.Email(email=target_emails)

        res = send_notification.send_mail(target_emails)

        return res

class ForwardCallToAgency(BaseTool):
    name = 'forward_call_to_government_agency'
    description = f'Useful when you need to forward very critical emergencies to a human agent.'

    def _run(self, run_manager: Optional[CallbackManagerForToolRun]=None, *args, **kwargs) -> dict:
        print(kwargs)
        return {'message':'Call forwarded successfully'}
