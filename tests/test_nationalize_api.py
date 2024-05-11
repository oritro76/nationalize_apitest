import requests
import pytest
from pydantic import ValidationError
import responses
from settings import url, max_batch_size
from api_response_models.nationalize_api_models import NationalizeResponse, ErrorResponse
from helpers.test_helpers import *
from mocks.mock_helpers import generate_nationalize_api_mock_responses
from functools import partial
from helpers.error_constants import *


def test_successful_name_prediction_with_last_name():
    """
    Verifies that the API returns a successful response with predicted nationalities for a valid last name
    """
    params = {"name": generate_fake_last_name()}

    response = requests.get(
        url=url, params=params, hooks={"response": [log_request, log_response]}
    )

    assert_common_success_response(response=response, params=params)


def test_successful_name_prediction_with_full_name():
    """
    Verifies that the API returns a successful response with predicted nationalities for a valid full name.
    """
    params = {"name": generate_fake_name()}

    response = requests.get(
        url=url, params=params, hooks={"response": [log_request, log_response]}
    )

    assert_common_success_response(response=response, params=params)


def test_name_parameter_missing():
    """
    Verifies that the API returns an error response for a missing parameter name.

    """

    response = requests.get(url, hooks={"response": [log_request, log_response]})
    print(response.status_code)
    print(response.json())

    assert_common_error_response(
        status_code=requests.codes.unprocessable_entity,
        response=response,
        error=ERROR_MISSING_NAME,
    )

@responses.activate
@pytest.mark.parametrize("num_last_names", [2, max_batch_size])
def test_batch_usage_successful_name_prediction(num_last_names, request):
    """
    Verifies successful prediction of nationalities for a batch of last names.
    """
    responses.add_callback(
        method=responses.GET,
        url=url,
        callback=partial(
            generate_nationalize_api_mock_responses, test_name=request.node.name
        ),
        content_type="application/json",
    )

    names = generate_fake_last_names(num_last_names=num_last_names)
    params = {"name[]": names}

    response = requests.get(
        url=url, params=params, hooks={"response": [log_request, log_response]}
    )

    assert response.status_code == requests.codes.ok

    assert_common_headers(response=response)

    for item in response.json():
        try:
            data = NationalizeResponse(**item)  # Parse response using Pydantic model
            assert_common_success_batch_usage_response_json(data=data)
        except ValidationError as e:
            assert False, f"Pydantic validation failed: {e}"

    assert_all_names_are_in_response(response=response, names=names)


def test_batch_usage_with_more_than_ten_names():
    """
    Verifies that the API returns an error response when attempting to predict 
    nationalities for more than ten names in a batch.
    """
    names = generate_fake_last_names(num_last_names=11)

    params = {"name[]": names}

    response = requests.get(
        url=url, params=params, hooks={"response": [log_request, log_response]}
    )

    assert_common_error_response(
        status_code=422, response=response, error=ERROR_INVALID_NAME
    )


def test_x_rate_limit_remaining_for_batch_usage():
    """
    Verifies the remaining request limit for batch usage after making requests.
    """
    params = {"name": generate_fake_last_name()}

    response = requests.get(
        url=url, params=params, hooks={"response": [log_request, log_response]}
    )

    assert response.status_code == 200

    x_rate_limit_reamining = int(response.headers["x-rate-limit-remaining"])

    names = generate_fake_last_names(num_last_names=2)
    params = {"name[]": names}

    response = requests.get(url=url, params=params)

    assert response.status_code == requests.codes.ok
    assert x_rate_limit_reamining - len(names) == int(
        response.headers["x-rate-limit-remaining"]
    )


@responses.activate
def test_x_rate_limit_too_low(request):
    """
    Verifies that the API returns an error response when the request limit is less than number of names for batch usage.
    """
    responses.add_callback(
        method=responses.GET,
        url=url,
        callback=partial(
            generate_nationalize_api_mock_responses, test_name=request.node.name
        ),
        content_type="application/json",
    )

    params = {"name[]": generate_fake_last_names(num_last_names=2)}

    response = requests.get(
        url=url, params=params, hooks={"response": [log_request, log_response]}
    )

    assert response.status_code == requests.codes.ok

    x_rate_limit_reamining = int(response.headers["x-rate-limit-remaining"])
    count = int(x_rate_limit_reamining / max_batch_size)

    send_n_number_of_batch_requests(count=count, num_of_names=max_batch_size)

    x_rate_limit_reamining = x_rate_limit_reamining - (max_batch_size * count)

    params = {"name[]": generate_fake_last_names(num_last_names=max_batch_size)}

    response = requests.get(
        url=url, params=params, hooks={"response": [log_request, log_response]}
    )

    assert_common_error_response(
        status_code=requests.codes.too_many_requests,
        response=response,
        error=ERROR_REQUEST_LIMIT_LOW,
    )


@responses.activate
def test_x_rate_limit_reached(request):
    """
    Verifies that the API returns an error response when the request limit is reached during batch/normal usage.
    """
    responses.add_callback(
        method=responses.GET,
        url=url,
        callback=partial(
            generate_nationalize_api_mock_responses, test_name=request.node.name
        ),
        content_type="application/json",
    )

    params = {"name[]": generate_fake_last_names(num_last_names=2)}

    response = requests.get(
        url=url, params=params, hooks={"response": [log_request, log_response]}
    )

    assert response.status_code == 200

    x_rate_limit_reamining = int(response.headers["x-rate-limit-remaining"])
    count = int(x_rate_limit_reamining / max_batch_size)
    print("count", count)

    send_n_number_of_batch_requests(count=count, num_of_names=max_batch_size)

    x_rate_limit_reamining = x_rate_limit_reamining - (max_batch_size * count)

    params = {"name[]": generate_fake_last_names(num_last_names=x_rate_limit_reamining)}

    response = requests.get(
        url=url, params=params, hooks={"response": [log_request, log_response]}
    )

    assert response.status_code == 200

    params = {"name": generate_fake_last_name()}

    response = requests.get(
        url=url, params=params, hooks={"response": [log_request, log_response]}
    )

    assert_common_error_response(
        status_code=requests.codes.too_many_requests,
        response=response,
        error=ERROR_REQUEST_LIMIT_REACHED,
    )
