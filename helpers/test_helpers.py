from requests.models import Response
import requests
from faker import Faker
from api_response_models.nationalize_api_models import NationalizeResponse, ErrorResponse
from settings import x_rate_limit_limit_free_tier
from loguru import logger
from pydantic import ValidationError
from settings import url


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


def assert_common_headers(
    response: Response, expected_rate_limit_headers=False
) -> None:
    """
    Asserts the presence of common headers in the response.

    """

    assert (
        "x-request-id" in response.headers
    ), f"x-request-id is missing in response headers"

    if expected_rate_limit_headers:
        assert (
            "x-rate-limit-limit" in response.headers
        ), f"x-rate-limit-limit is missing in response headers"
        assert (
            "x-rate-limit-remaining" in response.headers
        ), f"x-rate-limit-remaining is missing in response headers"
        assert (
            "x-rate-limit-reset" in response.headers
        ), f"x-rate-limit-reset is missing in response headers"
        assert (
            response.headers["x-rate-limit-limit"] == x_rate_limit_limit_free_tier
        ), f"x-rate-limit-limit should always be {x_rate_limit_limit_free_tier} for free tier"

    content_type = response.headers.get("Content-Type")
    assert content_type, "Content-Type header is missing"
    if response.status_code == requests.codes.OK:
        assert (
            content_type == "application/json; charset=utf-8"
        ), f"Content type should always be application/json; charset=utf-8"
    else:
        assert (
            content_type == "application/json"
        ), f"Content type should always be application/json"


def assert_common_headers_for_error_response(response: Response) -> None:
    """
    Asserts the presence of common headers in the error response.

    """
    assert (
        "x-rate-limit-limit" not in response.headers
    ), f"x-rate-limit-limit is present in error response headers"
    assert (
        "x-rate-limit-remaining" not in response.headers
    ), f"x-rate-limit-remaining is present in error response headers"
    assert (
        "x-rate-limit-reset" not in response.headers
    ), f"x-rate-limit-reset is present in error response headers"
    assert (
        "x-request-id" in response.headers
    ), f"x-rate-limit-limit is missing in error response headers"
    assert (
        response.headers["Content-Type"] == "application/json"
    ), f"Content type should always be application/json"


def assert_common_success_response_json(data: NationalizeResponse, name: str):
    """
    Asserts the success response.

    """
    assert data.count, f"count is missing in response json"
    assert data.name == name, f"{name} is missing in response json"
    assert data.country, f"country list is missing response json"
    assert len(data.country) > 0, f"country list does not have any data for {name}"


def assert_common_success_batch_usage_response_json(data: NationalizeResponse):
    """
    Asserts the success batch response.

    """
    assert data.count, f"count is missing in response json"
    assert data.name, f"name is missing in response.json"
    assert data.country, f"country list is missing response json"
    assert len(data.country) > 0, f"country list does not have any data for {data.name}"


def assert_all_names_are_in_response(response: Response, names):
    """
    Asserts the names are present in success batch response.

    """

    for name in names:
        assert any(
            item["name"] == name for item in response.json()
        ), f"Name '{name}' not found in response"


def assert_common_success_response(response, params):
    """
    Asserts the http status code, headers and json body success response.

    """
    assert response.status_code == requests.codes.OK

    assert_common_headers(response=response, expected_rate_limit_headers=True)

    try:
        data = NationalizeResponse(**response.json())
        assert_common_success_response_json(data=data, name=params["name"])
    except ValidationError as e:
        assert False, f"Pydantic validation failed: {e}"


def assert_common_error_response(status_code, response, error):
    """
    Asserts the http status code, headers and json body error response.

    """
    assert response.status_code == status_code
    if response.status_code == requests.codes.unprocessable_entity:
        assert_common_headers_for_error_response(response=response)
    else:
        assert_common_headers(response=response, expected_rate_limit_headers=True)
    try:
        data = ErrorResponse(**response.json())
        assert data.error == error
    except ValidationError as e:
        assert False, f"Pydantic validation failed: {e}"


def generate_fake_last_names(num_last_names: int) -> list:
    """
    generate n number of fake last names
    """

    fake = Faker()
    last_names = [fake.last_name() for _ in range(num_last_names)]
    print(last_names)

    return last_names


def generate_fake_last_name() -> str:
    """
    generate fake last name
    """

    fake = Faker()
    return fake.last_name()


def generate_fake_name() -> str:
    """
    generate fake name
    """
    fake = Faker()
    return fake.name()


def send_n_number_of_batch_requests(count, num_of_names):
    """
    execute n number of batch request with n number of fake names
    """
    for _ in range(count):
        names = generate_fake_last_names(num_last_names=num_of_names)
        params = {"name[]": names}

        response = requests.get(
            url=url, params=params, hooks={"response": [log_request, log_response]}
        )
        assert response.status_code == requests.codes.ok
