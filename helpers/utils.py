from loguru import logger

def log_request(response, *args, **kwargs):
    """
    logs the request url, headers, body

    """
    logger.debug(f"Request: {response.request.method} {response.request.url}")
    logger.debug(f"Headers: {response.request.headers}")
    logger.debug(f"Body: {response.request.body}")


def log_response(response, *args, **kwargs):
    """
    logs the response status code, headers, body

    """
    logger.debug(f"Response Status Code: {response.status_code}")
    logger.debug(f"Response Headers: {response.headers}")
    logger.debug(f"Response Body: {response.text}")