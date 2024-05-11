# Automated e2e tests for Nationalize API

**Tech Stack**
Python 3.12, pytest, requests, respnses, Faker, Docker

## Prerequisites
1. Install Python 3.12 from https://www.python.org/ [optional, only for local machine]
2. Install Docker from https://docs.docker.com/engine/install/

## Solution Explained

This project provides a comprehensive test suite for the Nationalize API, which predicts nationalities based on names. It utilizes the requests library to make HTTP requests and responses to mock API responses for controlled testing scenarios.

Key Features:

Functional Tests: Verifies API behavior for various name formats (single name, last name, batch) and handles expected responses (success, error) with proper data validation using Pydantic models.
Error Handling: Ensures the API returns appropriate errors for missing parameters, exceeding request limits, and invalid requests.
Rate Limiting: Tests the functionality of rate limits for both single requests and batch usage, verifying the remaining request count after each call.
Mocks for Controlled Testing: Leverages mocks.mock_helpers.generate_nationalize_api_mock_responses to simulate API responses with specific headers and content, allowing for isolated unit testing without relying on external calls.

 Note: Test reports times are in UTC

# Important Folders
- api_response_models = API response models are kept here
- helpers = Helper files for test
- mocks = mocker for APIs
- reports = reports of Test results
- tests = Tests for API
- logs = Logs of all API requests and responses

    
## Getting Started

#### Install requirements

```
pip install -r requirements.txt
```

### To run API tests locally

```
pytest --html=./reports/report.html --self-contained-html tests
```

### Mocks 

we need to add the below decorator for the tests that we want to use mocks
```
@responses.activate
```

#### Run API tests and Load tests in docker

```
docker compose build
```

```
docker compose up
```
