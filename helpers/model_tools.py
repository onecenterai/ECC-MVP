import re
import json
import requests
from typing import Optional, Type, List, Dict, Any

from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool
from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun

# class GetEndpointParamsInput(BaseModel):
#     endpoint_name: str = Field(description="should be the name of an endpoint")

# class GetEndpointParams(BaseTool):
#     name = 'get_endpoint_params'
#     description = f'useful for when you need to ask customers values for params needed to send a request to the company\'s API.'
#     args_schema: Type[BaseModel] = GetEndpointParamsInput

#     def _run(self, endpoint_name: str, run_manager: Optional[CallbackManagerForToolRun]= None) -> List[str]:
#         endpoint = Endpoint.get_by_name(endpoint_name)
#         curl_req = endpoint.example_request

#         #first extract request payload
#         req_payload_pattern = r"-d '(.+?)'"
#         req_payload_match = re.search(req_payload_pattern, curl_req)
            
#         if req_payload_match:
#             req_payload = req_payload_match.group(1)
#         else:
#             req_payload = None 

#         # after getting the payload, we need to extract the keys from the payload ...
#         req_json = json.loads(req_payload)
#         keys = [k for k in req_json.keys()]
#         return keys
        
# class ApiQuery(BaseTool):
#     name = 'api_query'
#     description = f'Useful when want to make an api request, in order to complete a task requested by a customer'
    
#     def _run(self, run_manager: Optional[CallbackManagerForToolRun]= None, *args, **kwargs) -> dict:

#         #first get endpoint example
#         endpoint = Endpoint.get_by_name(kwargs.get('task'))
        
#         if not endpoint:
#             return {'message': 'current task is not available'}
        
#         #next get request type
#         curl_req = endpoint.example_request

#         req_type_pattern = r'-X\s+(\w+)'
#         req_type_match = re.search(req_type_pattern, curl_req)

#         if req_type_match:
#             req_type = req_type_match.group(1)
#         else:
#             return {'message': 'error sending request'}
        
#         #next get endpoint url
#         url = endpoint.endpoint_url

#         #next setup request body. 
#         #ordinarily it should be every other entry in the endpoint_param dict, 
#         #but to play it safe we would extract the request params
#         req_payload_pattern = r"-d '(.+?)'"
#         req_payload_match = re.search(req_payload_pattern, curl_req)
            
#         if req_payload_match:
#             req_payload = req_payload_match.group(1)
#         else:
#             return {'message': 'error sending request'}

#         req_json = json.loads(req_payload)
#         req_keys = [k for k in req_json.keys()]

#         #with the values in req_keys, we would extract values from the endpoint_params
#         body = {key: kwargs.get(key) for key in req_keys}

#         #get headers
#         req_header_pattern = r'-H "([^"]+)"'
#         regex_headers = re.findall(req_header_pattern, curl_req)
#         if len(regex_headers) == 0:
#             headers = None
#         headers =  {h.split(':')[0].strip():h.split(':')[1].strip() for h in regex_headers}

#         #now we can send the request
#         res = requests.request(method=req_type, url=url, data=json.dumps(body), headers=headers)

#         return res.json()
    
        
        
class SendEmergencyNotification(BaseTool):
    ...
