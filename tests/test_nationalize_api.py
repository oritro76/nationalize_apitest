import pytest
from pydantic import ValidationError

from helpers.test_helpers import *
from constants.error_constants import *
from clients.api_client import http_api_client
from settings import url, max_batch_size
from api_response_models.nationalize_api_models import (
    NationalizeResponse,
)
from test_data.test_data import (
    generate_fake_last_name,
    generate_fake_last_names,
    generate_fake_name,
)

class TestNationalizeApi:

    @pytest.mark.smoke
    def test_successful_name_prediction_with_last_name(self, mock_responses):
        """
        Verifies that the API returns a successful response
        with predicted nationalities for a valid last name
        """
        params = {"name": generate_fake_last_name()}

        response = http_api_client.get(url=url, params=params)

        assert_common_success_response(response=response, params=params)


    def test_successful_name_prediction_with_full_name(self, mock_responses):
        """
        Verifies that the API returns a successful response with
        predicted nationalities for a valid full name.
        """
        params = {"name": generate_fake_name()}

        response = http_api_client.get(url=url, params=params)

        assert_common_success_response(response=response, params=params)


    def test_name_parameter_missing(self):
        """
        Verifies that the API returns an error response for a missing parameter name.

        """

        response = http_api_client.get(url)

        assert_common_error_response(
            status_code=requests.codes.unprocessable_entity,
            response=response,
            error=ERROR_MISSING_NAME,
        )


    @pytest.mark.smoke
    @pytest.mark.parametrize("num_last_names", [2, max_batch_size])
    def test_batch_usage_successful_name_prediction(self, num_last_names, mock_responses):
        """
        Verifies successful prediction of nationalities for a batch of last names.
        """

        names = generate_fake_last_names(num_last_names=num_last_names)
        params = {"name[]": names}

        response = http_api_client.get(url=url, params=params)

        assert response.status_code == requests.codes.ok

        assert_common_headers(response=response)

        for item in response.json():
            try:
                data = NationalizeResponse(**item)
                assert_common_success_batch_usage_response_json(data=data)
            except ValidationError as e:
                assert False, f"Pydantic validation failed: {e}"

        assert_all_names_are_in_response(response=response, names=names)


    def test_batch_usage_with_more_than_ten_names(self):
        """
        Verifies that the API returns an error response when attempting to predict
        nationalities for more than ten names in a batch.
        """
        names = generate_fake_last_names(num_last_names=11)

        params = {"name[]": names}

        response = http_api_client.get(url=url, params=params)

        assert_common_error_response(
            status_code=requests.codes.unprocessable_entity,
            response=response,
            error=ERROR_INVALID_NAME,
        )

    @pytest.mark.rate_limit
    def test_x_rate_limit_remaining_for_batch_usage(self, mock_responses):
        """
        Verifies the remaining request limit for batch usage after making http_api_client.
        """
        params = {"name": generate_fake_last_name()}

        response = http_api_client.get(url=url, params=params)

        assert response.status_code == requests.codes.ok

        x_rate_limit_reamining = int(response.headers["x-rate-limit-remaining"])

        names = generate_fake_last_names(num_last_names=2)
        params = {"name[]": names}

        response = http_api_client.get(url=url, params=params)

        assert response.status_code == requests.codes.ok
        assert x_rate_limit_reamining - len(names) == int(
            response.headers["x-rate-limit-remaining"]
        )

    @pytest.mark.rate_limit
    def test_x_rate_limit_too_low(self, mock_responses):
        """
        Verifies that the API returns an error response when the request
        limit is less than number of names for batch usage.
        """

        params = {"name[]": generate_fake_last_names(num_last_names=2)}

        response = http_api_client.get(url=url, params=params)

        assert response.status_code == requests.codes.ok

        x_rate_limit_reamining = int(response.headers["x-rate-limit-remaining"])
        count = int(x_rate_limit_reamining / max_batch_size)

        send_n_number_of_batch_requests(count=count, num_of_names=max_batch_size)

        x_rate_limit_reamining = x_rate_limit_reamining - (max_batch_size * count)

        params = {"name[]": generate_fake_last_names(num_last_names=max_batch_size)}

        response = http_api_client.get(url=url, params=params)

        assert_common_error_response(
            status_code=requests.codes.too_many_requests,
            response=response,
            error=ERROR_REQUEST_LIMIT_LOW,
        )

    @pytest.mark.rate_limit
    def test_x_rate_limit_reached(self, mock_responses):
        """
        Verifies that the API returns an error response when the
        request limit is reached during batch/normal usage.
        """

        params = {"name[]": generate_fake_last_names(num_last_names=2)}

        response = http_api_client.get(url=url, params=params)

        assert response.status_code == requests.codes.ok

        x_rate_limit_reamining = int(response.headers["x-rate-limit-remaining"])
        count = int(x_rate_limit_reamining / max_batch_size)

        send_n_number_of_batch_requests(count=count, num_of_names=max_batch_size)

        x_rate_limit_reamining = x_rate_limit_reamining - (max_batch_size * count)

        params = {"name[]": generate_fake_last_names(num_last_names=x_rate_limit_reamining)}

        response = http_api_client.get(url=url, params=params)

        assert response.status_code == requests.codes.ok

        params = {"name": generate_fake_last_name()}

        response = http_api_client.get(url=url, params=params)

        assert_common_error_response(
            status_code=requests.codes.too_many_requests,
            response=response,
            error=ERROR_REQUEST_LIMIT_REACHED,
        )
