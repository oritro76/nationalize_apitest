import os
import random
import string
import datetime
import json
from faker import Faker
from settings import x_rate_limit_limit_free_tier

# Constantsdocker images -a -q | % { docker image rm $_ -f }
DEFAULT_INITIAL_LIMIT = x_rate_limit_limit_free_tier


def generate_random_number(lower_limit, upper_limit=1000) -> int:
    """
    Generates a random integer between lower_limit and upper_limit.
    """
    return random.randint(lower_limit, upper_limit)


def generate_random_request_id(length: int = 16) -> str:
    """
    Generates a random string of specified length for the request ID.
    """
    letters_and_digits = string.ascii_letters + string.digits
    return "".join(random.choice(letters_and_digits) for _ in range(length))


def get_current_date_header() -> str:
    """
    Returns the current date and time in HTTP header format.
    """
    now = datetime.datetime.now(datetime.timezone.utc)
    return now.strftime("%a, %d %b %Y %H:%M:%S GMT")


def get_remaining_requests(initial_limit: int = 100, num_of_names: int = 1) -> int:
    """
    Returns the remaining requests after deduction.
    """
    remaining = int(os.environ.get("rate_limit_remaining", initial_limit))
    remaining -= num_of_names
    os.environ["rate_limit_remaining"] = str(remaining)
    return max(0, remaining)


def generate_mock_headers(
    initial_limit: str = DEFAULT_INITIAL_LIMIT,
    num_of_names: int = 1,
    is_error: bool = False,
) -> dict:
    """
    Generates mock headers for both successful and error responses.
    """
    if is_error:
        remaining_requests = os.environ.get(
            "rate_limit_remaining", DEFAULT_INITIAL_LIMIT
        )
        content_type = "application/json"
    else:
        remaining_requests = get_remaining_requests(initial_limit, num_of_names)
        content_type = "application/json; charset=utf-8"
    return {
        "Server": "nginx/1.16.1",
        "Content-Type": content_type,
        "Date": get_current_date_header(),
        "Connection": "keep-alive",
        "access-control-allow-credentials": "true",
        "access-control-allow-origin": "*",
        "access-control-expose-headers": "x-rate-limit-limit,x-rate-limit-remaining,x-rate-limit-reset",
        "cache-control": "max-age=0, private, must-revalidate",
        "x-rate-limit-limit": str(initial_limit),
        "x-rate-limit-remaining": str(remaining_requests),
        "x-rate-limit-reset": "44716",
        "x-request-id": generate_random_request_id(),
    }


def generate_random_country_probabilities(
    num_countries: int = 5, decimal_places: int = 17
) -> dict:
    """
    Generates random country probabilities.
    """
    faker = Faker()
    country_codes_with_probability = [
        {
            "country_id": faker.country_code(),
            "probability": round(random.uniform(0, 1.0), decimal_places),
        }
        for _ in range(num_countries)
    ]
    return country_codes_with_probability


def generate_success_response_json(params: dict) -> dict:
    """
    Generates success response JSON.
    """
    if "name" in params:
        return {
            "count": generate_random_number(lower_limit=100),
            "name": params["name"],
            "country": generate_random_country_probabilities(num_countries=3),
        }
    if "name[]" in params:
        return [
            {
                "count": generate_random_number(lower_limit=100),
                "name": name,
                "country": generate_random_country_probabilities(num_countries=3),
            }
            for name in params["name[]"]
        ]


def generate_nationalize_api_mock_responses(request, test_name: str) -> tuple:
    """
    Generates mock responses for the Nationalize API.
    """
    status_code = 200
    num_of_names = 1
    if "test_name" not in os.environ:
        os.environ["test_name"] = test_name
        os.environ["rate_limit_remaining"] = str(DEFAULT_INITIAL_LIMIT)

    if int(os.environ.get("rate_limit_remaining", DEFAULT_INITIAL_LIMIT)) == 0:
        status_code = 429
        response = {"error": "Request limit reached"}

    if "name[]" in request.params and len(request.params.get("name[]", [])) > int(
        os.environ.get("rate_limit_remaining", DEFAULT_INITIAL_LIMIT)
    ):
        status_code = 429
        response = {"error": "Request limit too low to process request"}

    if "name" in request.params and status_code < 400:
        response = {
            "count": generate_random_number(lower_limit=100),
            "name": request.params["name"],
            "country": generate_random_country_probabilities(num_countries=3),
        }

    if "name[]" in request.params and status_code < 400:
        num_of_names = len(request.params.get("name[]", []))
        response = [
            {
                "count": generate_random_number(lower_limit=100),
                "name": name,
                "country": generate_random_country_probabilities(num_countries=3),
            }
            for name in request.params.get("name[]", [])
        ]

    if status_code < 400:
        headers = generate_mock_headers(num_of_names=num_of_names)
    else:
        headers = generate_mock_headers(is_error=True)

    return (status_code, headers, json.dumps(response))
