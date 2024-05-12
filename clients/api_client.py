import requests
from helpers.utils import log_request, log_response

http_api_client = requests.Session()
http_api_client.hooks['response'] = [log_request, log_response]