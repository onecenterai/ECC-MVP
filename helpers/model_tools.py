import re
import json
import requests
from typing import Optional

from langchain.tools import BaseTool
from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun

class SendEmergencyNotification(BaseTool):
    name = 'send_emergency_notification'
    description = f'Useful when you need to send an emergency notification to a government agency.'

    def _run(self, run_manager: Optional[CallbackManagerForToolRun]=None, *args, **kwargs) -> dict:
        
        return {'message': 'Notification Sent Successfully'}

class ForwardCallToAgency(BaseTool):
    name = 'forward_call_to_government_agency'
    description = f'Useful when you need to forward very critical emergencies to a human agent.'

    def _run(self, run_manager: Optional[CallbackManagerForToolRun]=None, *args, **kwargs) -> dict:
        return {'message':'Call forwarded successfully'}
