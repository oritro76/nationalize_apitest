# Automated e2e tests and load test for GRPC Auth API

**Tech Stack**
Python 3.12, pytest, requests, respnses, Faker, Docker

## Prerequisites
1. Install Python 3.12 from https://www.python.org/ [optional, only for local machine]
2. Install Docker from https://docs.docker.com/engine/install/

## Solution Explained
In this project the https://nationalize.io/ Batch usage functionality is tested with pytest.
As this service has rate limits, responses has been used for mocking the responses.


 Note: Test reports times are in UTC

# Important Folders
- api_response_models = API response models are kept here
- helpers = Helper files for test
- mocks = mocker for APIs
- reports = Test results from API are kept here
- tests = Tests for API
- logs = Logs of all API requests and responses are kept here

## Project Structure At A Glance
```
│   .dockerignore
│   docker-compose.yml
│   gen_grpc_codes_from_proto.sh
│   grpc_client.py
│   main.py
│   README.md
│   requirements.txt
│
├───auth_grpc_service
│       auth_service.py
│       auth_service_context.py
│       decorators.py
│       __init__.py
│
├───docker
│   └───grpc
│           Dockerfile
│
├───grpc_generated
│       auth_pb2.py
│       auth_pb2_grpc.py
│       __init__.py
│
├───protos
│       auth.proto
│
├───reports
│   ├───locust
│   │       report.html
│   │
│   └───test_results
│           report.html
│
└───tests
    │   auth_grpc_test.py
    │   conftest.py
    │   __init__.py
    │
    └───locust_files
            grpc_user.py
            locust_file.py
            locust_master.conf
            locust_worker.conf
            __init__.py
 ```       
## Getting Started

#### Install requirements

```
pip install -r requirements.txt
```

### To run API tests locally

```
pytest --html=./reports/report.html --self-contained-html tests
```

#### Run API tests and Load tests in docker

```
docker compose build
```

```
docker compose up
```
